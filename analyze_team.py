"""
Trace a selected team's best realistic route through the 2026 bracket.

Reuses the main simulation machinery but, each iteration, records the team's
group finish, how far they go, and exactly who they meet (and beat) at each
knockout round. Answers: what has to happen for that team to go as deep as
plausibly possible?
"""
from collections import Counter
import sys

import numpy as np

import data
import ratings
import tiebreakers as tb
import bracket
from model import calibrate_sup_scale
from simulate import build_remaining

TEAM = "France"
ITERS = 60000
SEED = 2026
MU = 2.75
HOST = 70.0
KO_HOST = 0.0   # set >0 to give the selected team a home-crowd edge in the knockout too

ROUND_OF = {}
for n in range(73, 89): ROUND_OF[n] = "R32"
for n in range(89, 97): ROUND_OF[n] = "R16"
for n in range(97, 101): ROUND_OF[n] = "QF"
for n in (101, 102): ROUND_OF[n] = "SF"
ROUND_OF[104] = "Final"


def team_group(team):
    for g, members in data.GROUPS.items():
        if team in members:
            return g
    raise ValueError(f"Team {team!r} is not in any group")


def play_trace(winners, runners, thirds_team, third_assignment, win_fn):
    """Like bracket.play_bracket but also returns each match's two participants."""
    winner_of, loser_of, parts = {}, {}, {}
    for (no, hspec, aspec) in bracket.R32:
        ht = bracket._resolve_r32(hspec, winners, runners, thirds_team, third_assignment)
        at = bracket._resolve_r32(aspec, winners, runners, thirds_team, third_assignment)
        parts[no] = (ht, at)
        w, l = win_fn(ht, at); winner_of[no], loser_of[no] = w, l
    for no in range(89, 105):
        (hk, hn), (ak, an) = bracket.LATER[no]
        ht = winner_of[hn] if hk == "Wm" else loser_of[hn]
        at = winner_of[an] if ak == "Wm" else loser_of[an]
        parts[no] = (ht, at)
        w, l = win_fn(ht, at); winner_of[no], loser_of[no] = w, l
    return winner_of, loser_of, parts


def main():
    sup, _ = calibrate_sup_scale(MU)
    rem, la, lb = build_remaining(MU, sup, HOST)
    n_rem = len(rem)
    teams = data.all_teams()
    team_idx = {t: i for i, t in enumerate(teams)}
    rng = np.random.default_rng(SEED)
    hg = rng.poisson(la[:, None], size=(n_rem, ITERS))
    ag = rng.poisson(lb[:, None], size=(n_rem, ITERS))
    lots_all = rng.random((ITERS, len(teams)))

    group_fixed = {g: [m for m in data.MATCHES if m[0] == g and m[3] is not None]
                   for g in data.GROUPS}
    group_rem = {g: [] for g in data.GROUPS}
    for k, (g, h, a) in enumerate(rem):
        group_rem[g].append((k, g, h, a))

    fifa, elo, hosts = ratings.FIFA_POINTS, ratings.ELO, data.HOSTS

    def win_fn(a, b):
        ea = elo[a] + (KO_HOST if a in hosts else 0.0)
        eb = elo[b] + (KO_HOST if b in hosts else 0.0)
        p = 1.0 / (1.0 + 10.0 ** (-(ea - eb) / 400.0))
        return (a, b) if rng.random() < p else (b, a)

    finish = Counter()                  # selected team's Group finish: 1/2/3/out
    reach = Counter()                   # furthest round reached
    reach_given = {1: Counter(), 2: Counter()}   # by group finish
    n_finish = Counter()
    opp = {"R32": Counter(), "R16": Counter(), "QF": Counter(), "SF": Counter(), "Final": Counter()}
    beat = {"R32": Counter(), "R16": Counter(), "QF": Counter(), "SF": Counter(), "Final": Counter()}

    team = TEAM
    if len(sys.argv) > 1:
        team = " ".join(sys.argv[1:])

    team_group_name = team_group(team)

    for it in range(ITERS):
        lots = {t: lots_all[it, team_idx[t]] for t in teams}
        winners, runners, thirds_team, third_group, thirds = {}, {}, {}, {}, []
        team_pos = None
        for g in data.GROUPS:
            full = list(group_fixed[g])
            for (k, gg, h, a) in group_rem[g]:
                full.append((gg, h, a, int(hg[k, it]), int(ag[k, it])))
            ranked, overall = tb.rank_group(data.GROUPS[g], full, fifa, lots)
            winners[g], runners[g], thirds_team[g] = ranked[0], ranked[1], ranked[2]
            third_group[ranked[2]] = g
            thirds.append((ranked[2], overall[ranked[2]]))
            if g == team_group_name:
                team_pos = ranked.index(team) + 1

        finish[team_pos] += 1
        ranked_thirds = tb.rank_best_thirds(thirds, fifa, lots)
        qualifying = ranked_thirds[:bracket.__dict__.get("N", 8)][:8]
        qualified_groups = [third_group[t] for t, _ in qualifying]
        qual_teams = {t for t, _ in qualifying}

        team_advances = team_pos in (1, 2) or team in qual_teams
        if not team_advances:
            reach["out"] += 1
            if team_pos in (1, 2):
                n_finish[team_pos] += 1
            continue

        third_assignment = bracket.allocate_thirds(qualified_groups, rng)
        winner_of, loser_of, parts = play_trace(
            winners, runners, thirds_team, third_assignment, win_fn)

        # find selected team's matches, opponents, results, furthest round
        furthest = "R32"
        for no, (h, a) in parts.items():
            if team not in (h, a) or no == 103:   # 103 = third-place play-off
                continue
            rnd = ROUND_OF[no]
            o = a if h == team else h
            won = winner_of[no] == team
            if rnd in opp:
                opp[rnd][o] += 1
                if won:
                    beat[rnd][o] += 1
            # furthest round = deepest round in which the team appears
            order = ["R32", "R16", "QF", "SF", "Final"]
            if order.index(rnd) > order.index(furthest):
                furthest = rnd
        # furthest = round REACHED (appeared in). Champion if won the final.
        if winner_of.get(104) == team:
            furthest = "Win"
        reach[furthest] += 1
        if team_pos in (1, 2):
            n_finish[team_pos] += 1
            for r in ("R16", "QF", "SF", "Final", "Win"):
                pass
        # record conditional reach (reached round r = appeared at r or deeper)
        order = ["R32", "R16", "QF", "SF", "Final", "Win"]
        depth = order.index(furthest)
        if team_pos in (1, 2):
            for r in order[1:]:
                if order.index(r) <= depth:
                    reach_given[team_pos][r] += 1

    def pct(n, d):
        return f"{100*n/d:5.1f}%" if d else "   -  "

    print(f"\n{team} — best-path analysis ({ITERS:,} sims, host +{HOST:.0f} group / "
          f"+{KO_HOST:.0f} KO)\n")
    print(f"Group {team_group_name} finish:")
    for p, lbl in [(1, "1st (win group)"), (2, "2nd"), (3, "3rd"),
                   (None, "out")]:
        key = p if p else None
        # 'out' = pos 3 or 4 and not a best-third
        if lbl == "out":
            continue
        print(f"  {lbl:<16}{pct(finish[p], ITERS)}")
    print(f"  (3rd-place finishes sometimes still advance as a best third)\n")

    print(f"Furthest stage {team} reaches (unconditional):")
    for r in ["R16", "QF", "SF", "Final", "Win"]:
        reached = sum(reach[x] for x in ["R16", "QF", "SF", "Final", "Win"]
                      if ["R16", "QF", "SF", "Final", "Win"].index(x) >=
                      ["R16", "QF", "SF", "Final", "Win"].index(r))
        print(f"  reach {r:<6}{pct(reached, ITERS)}")

    print(f"\nConditional on WINNING Group {team_group_name} vs finishing 2nd:")
    print(f"  {'':<8}{'win group':>12}{'finish 2nd':>12}")
    for r in ["R16", "QF", "SF", "Final"]:
        a = pct(reach_given[1][r], n_finish[1])
        b = pct(reach_given[2][r], n_finish[2])
        print(f"  {r:<8}{a:>12}{b:>12}")

    for rnd in ["R32", "R16", "QF", "SF", "Final"]:
        tot = sum(opp[rnd].values())
        print(f"\nMost common {rnd} opponents (and {team}'s win rate vs them):")
        if tot == 0:
            print(f"  (no {rnd} appearances)")
            continue
        for o, c in opp[rnd].most_common(6):
            print(f"  {o:<24}{100*c/tot:5.1f}% of {rnd}s   "
                  f"{team} wins {pct(beat[rnd][o], c)}")


if __name__ == "__main__":
    main()
