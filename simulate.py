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
import os

import numpy as np

import data
import ratings
import tiebreakers as tb
import bracket
from model import (MU_DEFAULT, HOST_ADV_DEFAULT, lambdas, calibrate_sup_scale,
                   calibration_report, implied_wdl)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
N_ADVANCE_THIRDS = 8
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


def simulate(iters, seed, mu, sup_scale, host_adv, ko_host_adv=KO_HOST_ADV_DEFAULT):
    teams = data.all_teams()
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

        ranked_thirds = tb.rank_best_thirds(thirds, fifa, lots)
        qualifying = ranked_thirds[:N_ADVANCE_THIRDS]
        for team, _s in qualifying:
            third_qual[team] += 1
        qualified_groups = [third_group[team] for team, _s in qualifying]

        # ---- knockout bracket ----
        third_assignment = bracket.allocate_thirds(qualified_groups, rng)
        ko = bracket.play_bracket(winners, runners, thirds_team,
                                  third_assignment, win_fn)
        for t in ko["r16"]:
            reach_r16[t] += 1
        for t in ko["qf"]:
            reach_qf[t] += 1
        for t in ko["sf"]:
            reach_sf[t] += 1
        for t in ko["final"]:
            reach_final[t] += 1
        champ[ko["champion"]] += 1
        runner_up[ko["runner_up"]] += 1

    for t in teams:
        advanced[t] = pos1[t] + pos2[t] + third_qual[t]

    def frac(d):
        return {t: d[t] / iters for t in teams}

    return dict(p1=frac(pos1), p2=frac(pos2), p3=frac(pos3),
                pq3=frac(third_qual), adv=frac(advanced),
                r16=frac(reach_r16), qf=frac(reach_qf), sf=frac(reach_sf),
                final=frac(reach_final), champ=frac(champ), runner=frac(runner_up))


def current_standings():
    """Points/GD/goals each team has actually earned so far (played matches)."""
    out = {}
    played = [m for m in data.MATCHES if m[3] is not None]
    for g, members in data.GROUPS.items():
        tbl = tb.team_table(members, played)
        out[g] = tbl
    return out


# ---------------------------------------------------------------- reporting

TEAMW = 24  # column width for team names (widest: "Bosnia and Herzegovina" = 22)


def fmt_pct(x):
    """One-decimal %, so right-justified columns align on the decimal and %."""
    if x >= 0.9995:
        return "100.0%"
    if x <= 0.0:
        return "0.0%"
    if x < 0.001:
        return "<0.1%"
    return f"{100 * x:.1f}%"


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

    print("\n" + banner)
    print("2026 FIFA WORLD CUP  -  MONTE CARLO TOURNAMENT PROBABILITIES")
    print(f"{iters:,} sims | Elo->Poisson (mu={mu}, sup_scale={sup_scale:.4f}, "
          f"host +{host_adv:.0f}) | FIFA-2026 tiebreakers | snapshot 2026-06-18")
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

    # write CSV
    csv_path = os.path.join(OUT_DIR, "group_probabilities.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        w.writeheader(); w.writerows(csv_rows)
    print(f"\nWrote {csv_path}")
    _write_markdown(res, stand, iters, mu, sup_scale, host_adv)


def _write_markdown(res, stand, iters, mu, sup_scale, host_adv):
    path = os.path.join(OUT_DIR, "group_probabilities.md")
    lines = [
        "# 2026 FIFA World Cup - group-stage advancement probabilities", "",
        f"- Simulations: **{iters:,}** | Model: World Football Elo -> independent "
        f"Poisson | mu={mu}, sup_scale={sup_scale:.4f}, host advantage=+{host_adv:.0f} Elo",
        f"- Tiebreakers: FIFA 2026 (head-to-head first). Snapshot: 2026-06-18.",
        "- ADV = P(1st) + P(2nd) + P(qualify as one of the 8 best third-placed teams).",
        "",
    ]
    for g, members in data.GROUPS.items():
        order = sorted(members, key=lambda t: res["adv"][t], reverse=True)
        lines += [f"## Group {g}", "",
                  "| Team | Elo | Pld | Pts | GD | 1st | 2nd | 3rd | Best-3 | **Advance** |",
                  "|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|"]
        for t in order:
            s = stand[g][t]
            lines.append(
                f"| {t} | {ratings.ELO[t]} | {s['pld']} | {s['pts']} | {s['gd']:+d} | "
                f"{fmt_pct(res['p1'][t])} | {fmt_pct(res['p2'][t])} | {fmt_pct(res['p3'][t])} | "
                f"{fmt_pct(res['pq3'][t])} | **{fmt_pct(res['adv'][t])}** |")
        lines.append("")

    lines += ["## Knockout-stage odds (sorted by title %)", "",
              "| Team | Reach R32 | R16 | QF | SF | Final | **Win** |",
              "|---|--:|--:|--:|--:|--:|--:|"]
    for t in sorted(data.all_teams(), key=lambda x: res["champ"][x], reverse=True):
        if res["r16"][t] < 0.005 and res["champ"][t] == 0:
            continue
        lines.append(
            f"| {t} | {fmt_pct(res['adv'][t])} | {fmt_pct(res['r16'][t])} | "
            f"{fmt_pct(res['qf'][t])} | {fmt_pct(res['sf'][t])} | "
            f"{fmt_pct(res['final'][t])} | **{fmt_pct(res['champ'][t])}** |")
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {path}")


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
    args = ap.parse_args()

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

    res = simulate(args.iters, args.seed, args.mu, sup_scale, args.host_adv,
                   args.ko_host_adv)
    print_report(res, args.iters, args.mu, sup_scale, args.host_adv)


if __name__ == "__main__":
    main()
