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


def _bracket_match_order():
    return (bracket.R32_NOS + bracket.R16_NOS + bracket.QF_NOS +
            bracket.SF_NOS + [bracket.THIRD_PLACE_NO, bracket.FINAL_NO])


def _format_bracket_table(res):
    lines = []
    lines.append("### Projected knockout bracket")
    lines.append("")
    lines.append("| Match | Stage | Favored winner | P(win) |")
    lines.append("|---|---|---|---|")
    for no in _bracket_match_order():
        probs = res["bracket"]["match_win_probs"].get(no, {})
        if not probs:
            continue
        winner, p = max(probs.items(), key=lambda x: x[1])
        lines.append(f"| {no} | {_stage_label(no)} | {winner} | {fmt_pct(p)} |")
    lines.append("")
    return lines


def _match_appearances(res, no):
    home_probs = res["bracket"]["home_slot_probs"].get(no, {})
    away_probs = res["bracket"]["away_slot_probs"].get(no, {})
    appear = Counter()
    for t, p in home_probs.items():
        appear[t] += p
    for t, p in away_probs.items():
        appear[t] += p
    return appear


def _match_conditional_win_rows(res, no, top=4):
    appear = _match_appearances(res, no)
    win_probs = res["bracket"]["match_win_probs"].get(no, {})
    rows = []
    for team, p_appear in sorted(appear.items(), key=lambda x: x[1], reverse=True)[:top]:
        p_win = win_probs.get(team, 0.0)
        p_given = p_win / p_appear if p_appear > 0 else 0.0
        rows.append((team, p_appear, p_given, p_win))
    return rows


def _format_bracket_detailed(res):
    lines = ["## Projected knockout bracket details", "", "```text"]
    for no in _bracket_match_order():
        rows = _match_conditional_win_rows(res, no, top=4)
        if not rows:
            continue
        lines.append(f"Match {no} ({_stage_label(no)})")
        for team, p_appear, p_given, p_win in rows:
            lines.append(
                f"  {team:<24} appears {fmt_pct(p_appear):>8} of the time, "
                f"wins {fmt_pct(p_given):>8} if there, total win {fmt_pct(p_win):>8}"
            )
        lines.append("")
    lines.append("```")
    lines.append("")
    return lines


def _short_team(team, max_len=12):
    if len(team) <= max_len:
        return team
    return team[: max_len - 1] + "…"


def _slot_team(res, no, side):
    probs = res["bracket"][f"{side}_slot_probs"].get(no, {})
    if not probs:
        return "?"
    team, p = max(probs.items(), key=lambda x: x[1])
    return f"{_short_team(team)} ({fmt_pct(p)})"


def _match_graphic_block(res, no):
    home_probs = res["bracket"]["home_slot_probs"].get(no, {})
    away_probs = res["bracket"]["away_slot_probs"].get(no, {})
    win_probs = res["bracket"]["match_win_probs"].get(no, {})
    if not home_probs and not away_probs:
        return [f"{no:>3} {_stage_label(no)}"]

    home_best, home_best_p = max(home_probs.items(), key=lambda x: x[1])
    away_best, away_best_p = max(away_probs.items(), key=lambda x: x[1])
    home_pair_win = win_probs.get(home_best, 0.0)
    away_pair_win = win_probs.get(away_best, 0.0)
    total = home_pair_win + away_pair_win
    if total > 0:
        home_pair_win /= total
        away_pair_win /= total
    return [
        f"{no:>3} {_stage_label(no)}",
        f"  {_short_team(home_best, 24):<24} {fmt_pct(home_best_p):>9}",
        f"  {_short_team(away_best, 24):<24} {fmt_pct(away_best_p):>9}",
        f"  {_short_team(home_best, 24)} win {fmt_pct(home_pair_win)}, {_short_team(away_best, 24)} win {fmt_pct(away_pair_win)}",
    ]


def _bracket_layout_rows(res):
    rows = [""] * 37
    def put(stage, row, no):
        rows[row] = rows[row] or {}
        rows[row][stage] = _match_graphic_block(res, no)

    put("r32", 0, 74); put("r16", 1, 89); put("qf", 3, 97); put("r32", 4, 73); put("r16", 5, 90)
    put("sf", 8, 101)
    put("r32", 10, 83); put("r16", 11, 93); put("qf", 13, 98); put("r32", 14, 81); put("r16", 15, 94)
    put("final", 18, 104)
    put("r32", 20, 76); put("r16", 21, 91); put("qf", 23, 99); put("r32", 24, 79); put("r16", 25, 92)
    put("sf", 28, 102)
    put("r32", 30, 86); put("r16", 31, 95); put("qf", 33, 100); put("r32", 34, 85); put("r16", 35, 96)
    put("r32", 36, 87)
    return rows


def _format_bracket_graphic(res):
    widths = [38, 34, 34, 34, 34]
    header = (
        f"{'R32':<{widths[0]}}{'R16':<{widths[1]}}"
        f"{'QF':<{widths[2]}}{'SF':<{widths[3]}}{'Final':<{widths[4]}}"
    )
    sep = "".join("-" * w for w in widths)
    lines = ["## Full knockout bracket graphic", "", "```text", header, sep]
    for row in _bracket_layout_rows(res):
        if not row:
            lines.append("")
            continue
        blocks = [row.get(stage, [""]) for stage in ("r32", "r16", "qf", "sf", "final")]
        max_lines = max(len(block) for block in blocks)
        for i in range(max_lines):
            cells = [(block[i] if i < len(block) else "") for block in blocks]
            lines.append("".join(c.ljust(w) for c, w in zip(cells, widths)))
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
        order = sorted(members, key=lambda t: res["adv"][t], reverse=True)
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

    print("\nBRACKET SUMMARY   most likely winner and win probability by match")
    print("| Match | Stage | Favored winner | P(win) |")
    print("|---|---|---|---|")
    for no in _bracket_match_order():
        win_probs = res["bracket"]["match_win_probs"].get(no, {})
        if not win_probs:
            continue
        winner, p = max(win_probs.items(), key=lambda x: x[1])
        print(f"| {no} | {_stage_label(no)} | {winner} | {fmt_pct(p)} |")

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
        order = sorted(members, key=lambda t: res["adv"][t], reverse=True)
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

    lines += _format_bracket_table(res)
    lines += _format_bracket_graphic(res)
    lines += _format_bracket_detailed(res)
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
    lines.append("### Projected knockout bracket")
    lines.append("")
    lines.append("| Match | Stage | Favored winner | P(win) |")
    lines.append("|---|---|---|---|")
    for no in _bracket_match_order():
        win_probs = res["bracket"]["match_win_probs"].get(no, {})
        if not win_probs:
            continue
        winner, p = max(win_probs.items(), key=lambda x: x[1])
        lines.append(f"| {no} | {_stage_label(no)} | {winner} | {fmt_pct(p)} |")
    lines.append("")
    lines += _format_bracket_graphic(res)
    lines.append("### Group-stage advancement")
    lines.append("`ADV` = P(1st) + P(2nd) + P(qualify as one of the 8 best thirds). Sorted by ADV.")
    lines.append("Full machine-readable table: [`output/group_probabilities.csv`](output/group_probabilities.csv).")
    lines.append("")
    for g, members in data.GROUPS.items():
        lines.append(f"### Group {g}")
        lines.append("| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |")
        lines.append("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
        order = sorted(members, key=lambda t: res["adv"][t], reverse=True)
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
