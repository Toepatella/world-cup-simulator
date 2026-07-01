"""
Monte Carlo simulation of the 2026 FIFA World Cup group stage.

For each simulated tournament:
  * every REMAINING fixture is scored with the Elo->Poisson model (data already
    played is fixed),
  * all 12 groups are ranked with the verified FIFA-2026 tiebreakers,
  * the 12 third-placed teams are ranked and the best 8 are marked as
    qualifying (this is why all groups must be simulated jointly).

Outputs, per group: each team's probability of finishing 1st, 2nd, 3rd,
qualifying as a best-third, and the overall probability of reaching the Round
of 32. Run:  python simulate.py  [--iters N] [--seed S] [--no-h2h-first] ...
"""

import argparse
import csv
import datetime
import os
import re
from collections import Counter

import numpy as np

import data
import ratings
import tiebreakers as tb
import bracket
from model import (MU_DEFAULT, HOST_ADV_DEFAULT, lambdas, calibrate_sup_scale,
                   calibration_report, implied_wdl)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
N_ADVANCE_THIRDS = 8
ROUND_OF = {n: "R32" for n in range(73, 89)}
ROUND_OF.update({n: "R16" for n in range(89, 97)})
ROUND_OF.update({n: "QF" for n in range(97, 101)})
ROUND_OF.update({n: "SF" for n in (101, 102)})
ROUND_OF[104] = "Final"
# Knockout venues are fixed by the bracket, not the opponent, so hosts get no
# venue boost in the knockout by default (tunable via --ko-host-adv).
KO_HOST_ADV_DEFAULT = 0.0


def build_remaining(mu, sup_scale, host_adv):
    """Return parallel lists for the remaining fixtures and their Poisson means."""
    rem = data.remaining_matches()           # list of (group, home, away)
    la, lb = [], []
    for (_g, home, away) in rem:
        ha = host_adv if home in data.HOSTS else 0.0
        hb = host_adv if away in data.HOSTS else 0.0
        a, b = lambdas(ratings.ELO[home], ratings.ELO[away], mu, sup_scale, ha, hb)
        la.append(a); lb.append(b)
    return rem, np.array(la), np.array(lb)


def team_group(team):
    for g, members in data.GROUPS.items():
        if team in members:
            return g
    raise ValueError(f"Team {team!r} is not in any group")


def simulate(iters, seed, mu, sup_scale, host_adv, ko_host_adv=KO_HOST_ADV_DEFAULT,
             team=None):
    teams = data.all_teams()
    if team is not None:
        team = data._normalize_team_name(team)
    if team is not None and team not in teams:
        raise ValueError(f"Team {team!r} is not in any group")
    team_group_name = team_group(team) if team is not None else None
    team_counters = None
    if team is not None:
        team_counters = {
            "finish": Counter(),
            "out": 0,
            "reach": Counter(),
            "reach_given": {1: Counter(), 2: Counter()},
            "n_finish": Counter(),
            "opp": {"R32": Counter(), "R16": Counter(), "QF": Counter(), "SF": Counter(), "Final": Counter()},
            "beat": {"R32": Counter(), "R16": Counter(), "QF": Counter(), "SF": Counter(), "Final": Counter()},
        }
    team_group_history = {} if team is not None else None

    team_idx = {t: i for i, t in enumerate(teams)}
    rem, la, lb = build_remaining(mu, sup_scale, host_adv)
    n_rem = len(rem)

    rng = np.random.default_rng(seed)
    # sample goals for every remaining fixture across all iterations at once
    hg = rng.poisson(la[:, None], size=(n_rem, iters))   # home goals
    ag = rng.poisson(lb[:, None], size=(n_rem, iters))   # away goals
    lots_all = rng.random((iters, len(teams)))           # final-resort random lot

    # pre-split fixtures by group: fixed (played) tuples + remaining indices
    group_fixed = {g: [(gg, h, a, hs, as_) for (gg, h, a, hs, as_) in data.MATCHES
                       if gg == g and hs is not None] for g in data.GROUPS}
    group_rem = {g: [] for g in data.GROUPS}
    for k, (g, h, a) in enumerate(rem):
        group_rem[g].append((k, g, h, a))

    # group-stage tally counters
    pos1 = {t: 0 for t in teams}
    pos2 = {t: 0 for t in teams}
    pos3 = {t: 0 for t in teams}
    third_qual = {t: 0 for t in teams}
    advanced = {t: 0 for t in teams}
    # knockout tally counters (reached round X = won the previous round)
    reach_r16 = {t: 0 for t in teams}
    reach_qf = {t: 0 for t in teams}
    reach_sf = {t: 0 for t in teams}
    reach_final = {t: 0 for t in teams}
    champ = {t: 0 for t in teams}
    runner_up = {t: 0 for t in teams}

    fifa = ratings.FIFA_POINTS
    elo = ratings.ELO
    hosts = data.HOSTS
    groups = list(data.GROUPS.keys())

    all_match_nos = (bracket.R32_NOS + bracket.R16_NOS + bracket.QF_NOS +
                     bracket.SF_NOS + [bracket.FINAL_NO, bracket.THIRD_PLACE_NO])
    home_slot_counts = {n: Counter() for n in all_match_nos}
    away_slot_counts = {n: Counter() for n in all_match_nos}
    match_win_counts = {n: Counter() for n in all_match_nos}

    def win_fn(a, b):
        """Knockout winner via Elo win-probability (ET/penalties absorbed)."""
        ea = elo[a] + (ko_host_adv if a in hosts else 0.0)
        eb = elo[b] + (ko_host_adv if b in hosts else 0.0)
        p = 1.0 / (1.0 + 10.0 ** (-(ea - eb) / 400.0))
        return (a, b) if rng.random() < p else (b, a)

    for it in range(iters):
        lots = {t: lots_all[it, team_idx[t]] for t in teams}
        winners, runners, thirds_team, third_group = {}, {}, {}, {}
        thirds = []
        team_pos = None
        for g in groups:
            full = list(group_fixed[g])
            for (k, gg, h, a) in group_rem[g]:
                full.append((gg, h, a, int(hg[k, it]), int(ag[k, it])))
            ranked, overall = tb.rank_group(data.GROUPS[g], full, fifa, lots)
            pos1[ranked[0]] += 1
            pos2[ranked[1]] += 1
            pos3[ranked[2]] += 1
            winners[g], runners[g], thirds_team[g] = ranked[0], ranked[1], ranked[2]
            third_group[ranked[2]] = g
            thirds.append((ranked[2], overall[ranked[2]]))
            if team is not None and g == team_group_name:
                team_pos = ranked.index(team) + 1
                team_counters["finish"][team_pos] += 1

        ranked_thirds = tb.rank_best_thirds(thirds, fifa, lots)
        qualifying = ranked_thirds[:N_ADVANCE_THIRDS]
        for team_name, _s in qualifying:
            third_qual[team_name] += 1
        qualified_groups = [third_group[team_name] for team_name, _s in qualifying]

        team_advances = None
        if team is not None:
            qual_teams = {team_name for team_name, _s in qualifying}
            team_advances = team_pos in (1, 2) or team in qual_teams
            if not team_advances:
                team_counters["out"] += 1
            if team_pos in (1, 2):
                team_counters["n_finish"][team_pos] += 1

        # ---- knockout bracket ----
        third_assignment = bracket.allocate_thirds(qualified_groups, rng)
        parts, winner_of, loser_of = bracket.play_bracket_with_matches(
            winners, runners, thirds_team, third_assignment, win_fn)
        for no, (home, away) in parts.items():
            home_slot_counts[no][home] += 1
            away_slot_counts[no][away] += 1
            match_win_counts[no][winner_of[no]] += 1

        r16_winners = [winner_of[n] for n in bracket.R32_NOS]
        qf_winners = [winner_of[n] for n in bracket.R16_NOS]
        sf_winners = [winner_of[n] for n in bracket.QF_NOS]
        final_winners = [winner_of[n] for n in bracket.SF_NOS]
        champ_team = winner_of[bracket.FINAL_NO]
        runner_team = loser_of[bracket.FINAL_NO]

        for t in r16_winners:
            reach_r16[t] += 1
        for t in qf_winners:
            reach_qf[t] += 1
        for t in sf_winners:
            reach_sf[t] += 1
        for t in final_winners:
            reach_final[t] += 1
        champ[champ_team] += 1
        runner_up[runner_team] += 1

        if team is not None and team_advances:
            furthest = "R32"
            for no, (home, away) in parts.items():
                if no == bracket.THIRD_PLACE_NO:
                    continue
                if team not in (home, away):
                    continue
                rnd = ROUND_OF[no]
                opponent = away if home == team else home
                team_counters["opp"][rnd][opponent] += 1
                if winner_of[no] == team:
                    team_counters["beat"][rnd][opponent] += 1
                if ["R32", "R16", "QF", "SF", "Final"].index(rnd) > ["R32", "R16", "QF", "SF", "Final"].index(furthest):
                    furthest = rnd
            if winner_of[bracket.FINAL_NO] == team:
                furthest = "Win"
            team_counters["reach"][furthest] += 1
            if team_pos in (1, 2):
                order = ["R32", "R16", "QF", "SF", "Final", "Win"]
                depth = order.index(furthest)
                for r in order[1:]:
                    if order.index(r) <= depth:
                        team_counters["reach_given"][team_pos][r] += 1

    for t in teams:
        advanced[t] = pos1[t] + pos2[t] + third_qual[t]

    def frac(d):
        return {t: d[t] / iters for t in teams}

    def normalize(counter_map):
        return {no: {t: c / iters for t, c in counts.items()}
                for no, counts in counter_map.items()}

    bracket_summary = {
        "home_slot_probs": normalize(home_slot_counts),
        "away_slot_probs": normalize(away_slot_counts),
        "match_win_probs": normalize(match_win_counts),
        "ko_host_adv": ko_host_adv,
    }

    team_summary = None
    if team is not None:
        team_summary = {
            "team": team,
            "finish": dict(team_counters["finish"]),
            "out": team_counters["out"],
            "reach": dict(team_counters["reach"]),
            "reach_given": {1: dict(team_counters["reach_given"][1]),
                            2: dict(team_counters["reach_given"][2])},
            "n_finish": dict(team_counters["n_finish"]),
            "opp": {r: dict(c) for r, c in team_counters["opp"].items()},
            "beat": {r: dict(c) for r, c in team_counters["beat"].items()},
        }

    return dict(p1=frac(pos1), p2=frac(pos2), p3=frac(pos3),
                pq3=frac(third_qual), adv=frac(advanced),
                r16=frac(reach_r16), qf=frac(reach_qf), sf=frac(reach_sf),
                final=frac(reach_final), champ=frac(champ), runner=frac(runner_up),
                bracket=bracket_summary, team_summary=team_summary)


def current_standings():
    """Points/GD/goals each team has actually earned so far (played matches)."""
    out = {}
    played = [m for m in data.MATCHES if m[3] is not None]
    for g, members in data.GROUPS.items():
        tbl = tb.team_table(members, played)
        out[g] = tbl
    return out


def _standings_order(members, tbl):
    """Sort a group by actual current standing (points, then GD, then goals
    scored) -- the same ordering as a real league table, not by the model's
    advancement probability."""
    return sorted(members,
                  key=lambda t: (tbl[t]["pts"], tbl[t]["gd"], tbl[t]["gf"]),
                  reverse=True)


def _snapshot_date():
    return datetime.date.today().isoformat()


# ---------------------------------------------------------------- reporting

TEAMW = 24  # column width for team names (widest: "Bosnia and Herzegovina" = 22)


def fmt_pct(x):
    """Two-decimal %, so right-justified columns align on the decimal and %."""
    if x >= 0.9995:
        return "100.00%"
    if x <= 0.0:
        return "0.00%"
    if x < 0.0001:
        return "<0.01%"
    return f"{100 * x:.2f}%"


def _stage_label(no):
    if no in bracket.R32_NOS:
        return "R32"
    if no in bracket.R16_NOS:
        return "R16"
    if no in bracket.QF_NOS:
        return "QF"
    if no in bracket.SF_NOS:
        return "SF"
    if no == bracket.FINAL_NO:
        return "Final"
    if no == bracket.THIRD_PLACE_NO:
        return "Third place"
    return str(no)


def _top_n(counter, n=3):
    return sorted(counter.items(), key=lambda x: x[1], reverse=True)[:n]


def _short_team(team, max_len=20):
    if len(team) <= max_len:
        return team
    return team[: max_len - 1] + "."


def _deterministic_bracket(res):
    """Play one single, internally-consistent bracket.

    For completed group stages, we use the actual current standings and FIFA
    2026 tiebreakers so the README bracket reflects the real qualified teams.
    For incomplete groups, we fall back to the probability-based path used by
    the Monte Carlo report.
    """
    winners, runners, thirds = {}, {}, {}
    group_matches = {g: [m for m in data.MATCHES if m[0] == g] for g in data.GROUPS}
    all_groups_complete = all(len([m for m in matches if m[3] is not None]) == 6
                              for matches in group_matches.values())

    if all_groups_complete:
        lots = {t: 0.0 for t in data.all_teams()}
        team_to_group = {}
        third_entries = []
        for g, members in data.GROUPS.items():
            ranked, _ = tb.rank_group(members, group_matches[g],
                                      ratings.FIFA_POINTS, lots)
            winners[g] = ranked[0]
            runners[g] = ranked[1]
            thirds[g] = ranked[2]
            third_entries.append((ranked[2], current_standings()[g][ranked[2]]))
            team_to_group[ranked[2]] = g

        ranked_thirds = tb.rank_best_thirds(third_entries, ratings.FIFA_POINTS, lots)
        qualified_groups = [team_to_group[team] for team, _ in ranked_thirds[:N_ADVANCE_THIRDS]]
    else:
        for g, members in data.GROUPS.items():
            winners[g] = max(members, key=lambda t: res["p1"][t])
            runners[g] = max(members, key=lambda t: res["p2"][t])
            thirds[g] = max(members, key=lambda t: res["p3"][t])

        # most likely 8 third-placed teams to qualify, ranked by Elo strength
        qualified_groups = sorted(thirds, key=lambda g: ratings.ELO[thirds[g]],
                                   reverse=True)[:N_ADVANCE_THIRDS]

    third_assignment = bracket.allocate_thirds(qualified_groups)

    ko_host_adv = res["bracket"].get("ko_host_adv", 0.0)

    def elo_win_prob(a, b):
        ea = ratings.ELO[a] + (ko_host_adv if a in data.HOSTS else 0.0)
        eb = ratings.ELO[b] + (ko_host_adv if b in data.HOSTS else 0.0)
        return 1.0 / (1.0 + 10.0 ** (-(ea - eb) / 400.0))

    def win_fn(a, b):
        p = elo_win_prob(a, b)
        return (a, b) if p >= 0.5 else (b, a)

    parts, winner_of, loser_of = bracket.play_bracket_with_matches(
        winners, runners, thirds, third_assignment, win_fn,
        fixed_results=bracket.FIXED_KNOCKOUT_RESULTS,
        fixed_matchups=bracket.FIXED_KNOCKOUT_MATCHUPS)

    win_pct = {}
    for no, (home, away) in parts.items():
        p_home = elo_win_prob(home, away)
        win_pct[no] = {home: p_home, away: 1.0 - p_home}

    return parts, winner_of, loser_of, win_pct


_BOX_NAMEW = 16
_BOX_WIDTH = _BOX_NAMEW + 1 + 7 + 2  # marker+space+name+space+pct, padded
_GAP = 4  # spaces between a match box and the box it feeds into


def _box_lines(parts, winner_of, win_pct, no):
    """A single match as a 5-line box: stage label, then a bordered card with
    both teams and their Elo win probabilities; '>' marks who advances."""
    home, away = parts[no]
    winner = winner_of[no]
    border = "+" + "-" * _BOX_WIDTH + "+"
    rows = []
    for t in (home, away):
        mark = ">" if t == winner else " "
        pct = fmt_pct(win_pct[no][t])
        row = f"{mark} {_short_team(t, _BOX_NAMEW):<{_BOX_NAMEW}} {pct:>7}"
        rows.append(f"|{row:<{_BOX_WIDTH}}|")
    return [_stage_label(no), border, rows[0], rows[1], border]


def _leaf(parts, winner_of, win_pct, no):
    lines = _box_lines(parts, winner_of, win_pct, no)
    width = max(len(l) for l in lines)
    return {"lines": [l.ljust(width) for l in lines], "width": width, "anchor": len(lines) // 2}


def _hmerge(top, bottom, parent_lines):
    """Stack `top` above `bottom` (no gap) and attach `parent_lines` to the
    right, vertically centered on the midpoint between the two children's
    anchors -- the standard way a bracket box centers over its two feeders."""
    width = max(top["width"], bottom["width"])
    top_lines = [l.ljust(width) for l in top["lines"]]
    bottom_lines = [l.ljust(width) for l in bottom["lines"]]
    combined = top_lines + bottom_lines

    h_top = len(top_lines)
    anchor_top = top["anchor"]
    anchor_bottom = h_top + bottom["anchor"]
    target = (anchor_top + anchor_bottom) // 2

    box_h = len(parent_lines)
    box_anchor = box_h // 2
    start = max(0, target - box_anchor)
    end = start + box_h

    if end > len(combined):
        combined += [" " * width] * (end - len(combined))

    box_w = max(len(l) for l in parent_lines)
    new_lines = []
    for i, left in enumerate(combined):
        if start <= i < end:
            right = parent_lines[i - start]
        else:
            right = " " * box_w
        new_lines.append(left + " " * _GAP + right.ljust(box_w))

    return {"lines": new_lines, "width": width + _GAP + box_w, "anchor": start + box_anchor}


def _r16_group(parts, winner_of, win_pct, r32a, r32b, r16):
    leaf_a = _leaf(parts, winner_of, win_pct, r32a)
    leaf_b = _leaf(parts, winner_of, win_pct, r32b)
    box16 = _box_lines(parts, winner_of, win_pct, r16)
    return _hmerge(leaf_a, leaf_b, box16)


def _qf_group(parts, winner_of, win_pct, g1, g2, qf):
    grp_a = _r16_group(parts, winner_of, win_pct, *g1)
    grp_b = _r16_group(parts, winner_of, win_pct, *g2)
    boxqf = _box_lines(parts, winner_of, win_pct, qf)
    return _hmerge(grp_a, grp_b, boxqf)


def _format_bracket_ascii(res):
    """Deterministic ASCII knockout bracket: every match is a card showing
    each team's Elo-model win probability, and the favorite ('>') is the one
    carried into the next round, laid out as a standard left-to-right
    tournament tree (each round's box centered between its two feeders)."""
    parts, winner_of, loser_of, win_pct = _deterministic_bracket(res)

    # (R32 a, R32 b, R16) feeding each quarterfinal, paired by semifinal
    quarters = [
        ((74, 77, 89), (73, 75, 90), 97),
        ((83, 84, 93), (81, 82, 94), 98),
        ((76, 78, 91), (79, 80, 92), 99),
        ((86, 88, 95), (85, 87, 96), 100),
    ]

    qf_trees = [_qf_group(parts, winner_of, win_pct, g1, g2, qf) for (g1, g2, qf) in quarters]

    sf_box_1 = _box_lines(parts, winner_of, win_pct, 101)
    sf_box_2 = _box_lines(parts, winner_of, win_pct, 102)
    sf_tree_1 = _hmerge(qf_trees[0], qf_trees[1], sf_box_1)
    sf_tree_2 = _hmerge(qf_trees[2], qf_trees[3], sf_box_2)

    final_box = _box_lines(parts, winner_of, win_pct, bracket.FINAL_NO)
    final_tree = _hmerge(sf_tree_1, sf_tree_2, final_box)

    lines = ["## Knockout bracket (most-likely-winner path)", "", "```text"]
    lines += final_tree["lines"]
    lines.append("")
    lines += _box_lines(parts, winner_of, win_pct, bracket.THIRD_PLACE_NO)
    lines.append("")
    lines.append(f"Champion: {winner_of[bracket.FINAL_NO]}")
    lines.append("```")
    lines.append("")
    return lines


def _format_team_summary(team_summary, iters):
    lines = ["## Team analysis summary", "", f"Team: **{team_summary['team']}**", ""]
    lines.append("### Group finish distribution")
    lines.append("| Finish | Count | Probability |")
    lines.append("|---|---|---|")
    for pos in [1, 2, 3, 4]:
        cnt = team_summary['finish'].get(pos, 0)
        lines.append(f"| {pos} | {cnt} | {fmt_pct(cnt / iters)} |")
    lines.append("")
    lines.append("### Knockout progress (unconditional)")
    lines.append("| Stage | Count | Probability |")
    lines.append("|---|---|---|")
    for stage in ["R16", "QF", "SF", "Final", "Win"]:
        cnt = team_summary['reach'].get(stage, 0)
        lines.append(f"| {stage} | {cnt} | {fmt_pct(cnt / iters)} |")
    lines.append("")
    if team_summary['n_finish'].get(1, 0) > 0 or team_summary['n_finish'].get(2, 0) > 0:
        lines.append("### Conditional knockout progress by group finish")
        lines.append("| Finish | Stage | Probability |")
        lines.append("|---|---|---|")
        for finish in [1, 2]:
            for stage in ["R16", "QF", "SF", "Final"]:
                cnt = team_summary['reach_given'][finish].get(stage, 0)
                denom = team_summary['n_finish'].get(finish, 0)
                lines.append(f"| {finish} | {stage} | {fmt_pct(cnt / denom) if denom else '0.00%'} |")
        lines.append("")
    lines.append("### Most common knockout opponents")
    lines.append("```text")
    for stage in ["R32", "R16", "QF", "SF", "Final"]:
        opps = team_summary['opp'].get(stage, {})
        if not opps:
            continue
        lines.append(f"{stage} opponents:")
        for opp, cnt in sorted(opps.items(), key=lambda x: x[1], reverse=True)[:5]:
            wins = team_summary['beat'][stage].get(opp, 0)
            lines.append(f"  {opp:<24} {cnt:>4} times, wins {fmt_pct(wins / cnt)}")
        lines.append("")
    lines.append("```")
    lines.append("")
    return lines


def _prow(t, cells, widths):
    """One left-aligned name cell followed by right-aligned cells."""
    out = f"{t:<{TEAMW}}"
    for c, w in zip(cells, widths):
        out += f"{c:>{w}}"
    return out


def print_report(res, iters, mu, sup_scale, host_adv):
    stand = current_standings()
    os.makedirs(OUT_DIR, exist_ok=True)
    csv_rows = []

    # ---- group stage ----
    gcols = ["1st", "2nd", "3rd", "Best3", "Advance"]
    gw = [9, 9, 9, 9, 10]
    ghead = (f"{'Team':<{TEAMW}}{'Elo':>6}{'Pld':>5}{'Pts':>5}{'GD':>5}"
             + "".join(f"{c:>{w}}" for c, w in zip(gcols, gw)))
    banner = "=" * len(ghead)

    snapshot_date = _snapshot_date()
    print("\n" + banner)
    print("2026 FIFA WORLD CUP  -  MONTE CARLO TOURNAMENT PROBABILITIES")
    print(f"{iters:,} sims | Elo->Poisson (mu={mu}, sup_scale={sup_scale:.4f}, "
          f"host +{host_adv:.0f}) | FIFA-2026 tiebreakers | snapshot {snapshot_date}")
    print(banner)
    print("\nGROUP STAGE   probability of finishing 1st / 2nd / 3rd, qualifying "
          "as a best third, and advancing")

    for g, members in data.GROUPS.items():
        tbl = stand[g]
        order = _standings_order(members, tbl)
        print(f"\nGroup {g}")
        print(ghead)
        print("-" * len(ghead))
        for t in order:
            s = tbl[t]
            head = (f"{t:<{TEAMW}}{ratings.ELO[t]:>6}{s['pld']:>5}{s['pts']:>5}"
                    f"{s['gd']:>+5}")
            cells = [fmt_pct(res[k][t]) for k in ("p1", "p2", "p3", "pq3", "adv")]
            print(head + "".join(f"{c:>{w}}" for c, w in zip(cells, gw)))
            csv_rows.append(dict(
                group=g, team=t, elo=ratings.ELO[t], played=s["pld"],
                points=s["pts"], gd=s["gd"], gf=s["gf"],
                p_first=round(res["p1"][t], 4), p_second=round(res["p2"][t], 4),
                p_third=round(res["p3"][t], 4),
                p_best_third_qualify=round(res["pq3"][t], 4),
                p_advance=round(res["adv"][t], 4),
                p_reach_r16=round(res["r16"][t], 4),
                p_reach_qf=round(res["qf"][t], 4),
                p_reach_sf=round(res["sf"][t], 4),
                p_reach_final=round(res["final"][t], 4),
                p_champion=round(res["champ"][t], 4)))

    # ---- best-third race ----
    print("\n" + banner)
    print("BEST-THIRD RACE   8 of the 12 third-placed teams advance")
    bw = [10, 12, 12]
    bhead = (f"{'Team':<{TEAMW}}{'P(3rd)':>10}{'Adv as 3rd':>12}{'P(adv|3rd)':>12}")
    print(bhead)
    print("-" * len(bhead))
    for t in sorted(data.all_teams(), key=lambda t: res["pq3"][t], reverse=True):
        if res["p3"][t] < 0.005 and res["pq3"][t] < 0.005:
            continue
        cond = res["pq3"][t] / res["p3"][t] if res["p3"][t] > 0 else 0.0
        print(_prow(t, [fmt_pct(res["p3"][t]), fmt_pct(res["pq3"][t]),
                        fmt_pct(cond)], bw))

    # ---- knockout / title odds ----
    print("\n" + banner)
    print("KNOCKOUT STAGE   probability of reaching each round (sorted by title %)")
    kcols = ["R32", "R16", "QF", "SF", "Final", "WIN"]
    kw = [9, 9, 9, 9, 9, 9]
    khead = f"{'Team':<{TEAMW}}" + "".join(f"{c:>{w}}" for c, w in zip(kcols, kw))
    print(khead)
    print("-" * len(khead))
    for t in sorted(data.all_teams(), key=lambda t: res["champ"][t], reverse=True):
        if res["r16"][t] < 0.005 and res["champ"][t] == 0:
            continue
        cells = [fmt_pct(res[k][t]) for k in ("adv", "r16", "qf", "sf", "final", "champ")]
        print(_prow(t, cells, kw))

    print("\nKNOCKOUT BRACKET   most-likely-winner path")
    for line in _format_bracket_ascii(res):
        if line not in ("## Knockout bracket (most-likely-winner path)", "```text", "```"):
            print(line)

    if res.get("team_summary"):
        ts = res["team_summary"]
        print(f"\nTEAM ANALYSIS for {ts['team']}")
        print("Group finish distribution:")
        for pos in [1, 2, 3, 4]:
            cnt = ts['finish'].get(pos, 0)
            print(f"  {pos}: {cnt} ({fmt_pct(cnt / iters)})")
        print("\nKnockout progress:")
        for stage in ["R16", "QF", "SF", "Final", "Win"]:
            cnt = ts['reach'].get(stage, 0)
            print(f"  {stage}: {cnt} ({fmt_pct(cnt / iters)})")
    # write CSV
    csv_path = os.path.join(OUT_DIR, "group_probabilities.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        w.writeheader(); w.writerows(csv_rows)
    print(f"\nWrote {csv_path}")
    _write_markdown(res, stand, iters, mu, sup_scale, host_adv)


def _write_markdown(res, stand, iters, mu, sup_scale, host_adv):
    path = os.path.join(OUT_DIR, "group_probabilities.md")
    snapshot_date = _snapshot_date()
    lines = [
        "# 2026 FIFA World Cup - group-stage advancement probabilities", "",
        f"- Simulations: **{iters:,}** | Model: World Football Elo -> independent "
        f"Poisson | mu={mu}, sup_scale={sup_scale:.4f}, host advantage=+{host_adv:.0f} Elo",
        f"- Tiebreakers: FIFA 2026 (head-to-head first). Snapshot: {snapshot_date}.",
        "- ADV = P(1st) + P(2nd) + P(qualify as one of the 8 best third-placed teams).",
        "",
    ]

    gcols = ["1st", "2nd", "3rd", "Best3", "Advance"]
    gw = [9, 9, 9, 9, 10]
    ghead = (f"{'Team':<{TEAMW}}{'Elo':>6}{'Pld':>5}{'Pts':>5}{'GD':>5}"
             + "".join(f"{c:>{w}}" for c, w in zip(gcols, gw)))
    banner = "=" * len(ghead)

    for g, members in data.GROUPS.items():
        order = _standings_order(members, stand[g])
        lines += [f"## Group {g}", "", "```text", ghead, banner]
        for t in order:
            s = stand[g][t]
            lines.append(_prow(t, [ratings.ELO[t], s["pld"], s["pts"], s["gd"],
                                   fmt_pct(res["p1"][t]), fmt_pct(res["p2"][t]),
                                   fmt_pct(res["p3"][t]), fmt_pct(res["pq3"][t]),
                                   fmt_pct(res["adv"][t])],
                                  [6, 5, 5, 5] + gw))
        lines += ["```", ""]

    lines += ["## Best-third race (8 of the 12 third-placed teams advance)", "", "```text"]
    bhead = f"{'Team':<{TEAMW}}{'P(3rd)':>10}{'Adv as 3rd':>12}{'P(adv|3rd)':>12}"
    lines += [bhead, "-" * len(bhead)]
    for t in sorted(data.all_teams(), key=lambda t: res["pq3"][t], reverse=True):
        if res["p3"][t] < 0.005 and res["pq3"][t] < 0.005:
            continue
        cond = res["pq3"][t] / res["p3"][t] if res["p3"][t] > 0 else 0.0
        lines.append(_prow(t, [fmt_pct(res["p3"][t]), fmt_pct(res["pq3"][t]),
                               fmt_pct(cond)], [10, 12, 12]))
    lines += ["```", ""]

    lines += ["## Knockout-stage odds (sorted by title %)", "", "```text"]
    kcols = ["R32", "R16", "QF", "SF", "Final", "WIN"]
    kw = [9, 9, 9, 9, 9, 9]
    khead = f"{'Team':<{TEAMW}}" + "".join(f"{c:>{w}}" for c, w in zip(kcols, kw))
    lines += [khead, "-" * len(khead)]
    for t in sorted(data.all_teams(), key=lambda x: res["champ"][x], reverse=True):
        if res["r16"][t] < 0.005 and res["champ"][t] == 0:
            continue
        cells = [fmt_pct(res[k][t]) for k in ("adv", "r16", "qf", "sf", "final", "champ")]
        lines.append(_prow(t, cells, kw))
    lines += ["```", ""]

    lines += _format_bracket_ascii(res)
    if res.get("team_summary"):
        lines += _format_team_summary(res["team_summary"], iters)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {path}")


def _update_readme_sources(content, snapshot_date):
    pattern = re.compile(
        r"\| Group composition, played scores, remaining fixtures \| .*? \| \d{4}-\d{2}-\d{2} \|",
        re.S
    )
    replacement = (
        f"| Group composition, played scores, remaining fixtures | "
        f"Wikipedia per-group pages (\"2026 FIFA World Cup Group A … L\"), "
        f"cross-checked vs [NBC](https://www.nbcsports.com/soccer/news/2026-world-cup-group-stage-table-full-standings-for-all-12-groups) / "
        f"[ESPN](https://www.espn.com/soccer/story/_/id/48939282/) and live [GitHub openfootball/worldcup.json]"
        f"(https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json) | {snapshot_date} |"
    )
    return pattern.sub(replacement, content, count=1)


def _update_readme_snapshot(content, snapshot_date):
    return re.sub(
        r"\*\*Snapshot date: .*?\*\*\.",
        f"**Snapshot date: {snapshot_date}.**",
        content,
        count=1
    )


def _format_readme_headline(res, stand, iters, snapshot_date):
    lines = []
    lines.append(f"## Headline results ({iters:,} simulations)")
    lines.append("")
    lines.append("### Title odds — probability of reaching each knockout round (and winning)")
    lines.append("Sorted by championship %. `R32` = reach the knockout stage at all.")
    lines.append("")
    lines.append("| Team | R32 | R16 | QF | SF | Final | **Win** |")
    lines.append("|---|--:|--:|--:|--:|--:|--:|")
    for t in sorted(data.all_teams(), key=lambda x: res["champ"][x], reverse=True):
        if res["r16"][t] < 0.005 and res["champ"][t] == 0:
            continue
        lines.append(
            f"| {t} | {fmt_pct(res['adv'][t])} | {fmt_pct(res['r16'][t])} | "
            f"{fmt_pct(res['qf'][t])} | {fmt_pct(res['sf'][t])} | "
            f"{fmt_pct(res['final'][t])} | **{fmt_pct(res['champ'][t])}** |"
        )
    lines.append("")
    lines.append("*(All 48 teams, including the long shots, are in the CSV. Remaining sides each sit below ~0.7% to win.)*")
    lines.append("")
    lines += _format_bracket_ascii(res)
    lines.append("### Group-stage advancement")
    lines.append("`ADV` = P(1st) + P(2nd) + P(qualify as one of the 8 best thirds). Sorted by ADV.")
    lines.append("Full machine-readable table: [`output/group_probabilities.csv`](output/group_probabilities.csv).")
    lines.append("")
    for g, members in data.GROUPS.items():
        lines.append(f"### Group {g}")
        lines.append("| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |")
        lines.append("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
        order = _standings_order(members, stand[g])
        for t in order:
            s = stand[g][t]
            lines.append(
                f"| {t} | {ratings.ELO[t]} | {s['pld']} | {s['pts']} | {s['gd']:+d} | "
                f"{fmt_pct(res['p1'][t])} | {fmt_pct(res['p2'][t])} | {fmt_pct(res['p3'][t])} | "
                f"{fmt_pct(res['pq3'][t])} | **{fmt_pct(res['adv'][t])}** |"
            )
        lines.append("")
    lines.append(
        f"*Probabilities are Monte Carlo estimates ({iters:,} sims); Monte Carlo standard "
        f"error is ≈0.2pp or less. Numbers reflect the model and the {snapshot_date} snapshot, "
        f"not a claim about real-world certainty.*"
    )
    lines.append("")
    return "\n".join(lines)


def _update_readme(res, stand, iters, mu, sup_scale, host_adv):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
    snapshot_date = datetime.date.today().isoformat()

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    content = _update_readme_snapshot(content, snapshot_date)
    content = _update_readme_sources(content, snapshot_date)

    marker_re = re.compile(r"^##\s*(?:\d+\.\s*)?Headline results.*$", re.M)
    m = marker_re.search(content)
    if not m:
        raise RuntimeError("Could not find README headline results section to update")
    content = content[:m.start()]

    hr_match = re.search(r"^---\s*$", content, re.M)
    if not hr_match:
        raise RuntimeError("Could not find README top section separator to insert headline results")
    insert_idx = content.find("\n", hr_match.end())
    if insert_idx == -1:
        insert_idx = len(content)
    else:
        insert_idx += 1

    content = (
        content[:insert_idx]
        + "\n"
        + _format_readme_headline(res, stand, iters, snapshot_date)
        + "\n"
        + content[insert_idx:]
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {path}")


def main():
    ap = argparse.ArgumentParser(description="2026 World Cup group-stage Monte Carlo")
    ap.add_argument("--iters", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--mu", type=float, default=MU_DEFAULT)
    ap.add_argument("--host-adv", type=float, default=HOST_ADV_DEFAULT,
                    help="group-stage Elo venue boost for host nations")
    ap.add_argument("--ko-host-adv", type=float, default=KO_HOST_ADV_DEFAULT,
                    help="knockout Elo venue boost for host nations (default 0)")
    ap.add_argument("--sup-scale", type=float, default=None,
                    help="override calibrated Elo->goals scale")
    ap.add_argument("--no-h2h-first", action="store_true",
                    help="use pre-2026 order (overall GD before head-to-head)")
    ap.add_argument("--show-calibration", action="store_true")
    ap.add_argument("--team", type=str,
                    help="Analyze a specific team in the same run")
    args = ap.parse_args()

    data.refresh_matches()
    data._sanity_check()
    ratings.check_complete(data.all_teams())
    if args.no_h2h_first:
        tb.set_h2h_first(False)

    if args.sup_scale is not None:
        sup_scale = args.sup_scale
    else:
        sup_scale, rmse = calibrate_sup_scale(mu=args.mu)
        print(f"Calibrated sup_scale = {sup_scale:.4f} "
              f"(Elo-expectancy match RMSE = {rmse:.4f})")

    if args.show_calibration:
        print("\n Elo gap | Elo We | model P(W) P(D) P(L) | lambdaA lambdaB")
        for dr, we, pw, pd, pl, a, b in calibration_report(args.mu, sup_scale):
            print(f"   {dr:>4}  | {we:5.3f}  |  {pw:4.2f} {pd:4.2f} {pl:4.2f}  |  "
                  f"{a:4.2f}   {b:4.2f}")

    team = data._normalize_team_name(args.team) if args.team is not None else None
    res = simulate(args.iters, args.seed, args.mu, sup_scale, args.host_adv,
                   args.ko_host_adv, team=team)
    print_report(res, args.iters, args.mu, sup_scale, args.host_adv)
    _update_readme(res, current_standings(), args.iters, args.mu, sup_scale, args.host_adv)


if __name__ == "__main__":
    main()
