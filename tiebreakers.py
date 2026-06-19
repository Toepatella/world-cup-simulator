"""
FIFA 2026 World Cup group-stage ranking and tiebreaker logic.

VERIFIED against the official "Regulations for the FIFA World Cup 26" (Article
13) and cross-checked on FIFA.com / ESPN / SofaScore / NBC / SI. The 2026
edition CHANGED the order versus 2018/2022: head-to-head is now applied
*before* overall goal difference (UEFA-style), and drawing of lots was removed
in favour of the FIFA World Ranking.

Ranking teams WITHIN a group (when two or more are level on points):
  1. Points in all group matches                          [defines the tied set]
  2. Head-to-head points  (matches among the tied teams)
  3. Head-to-head goal difference
  4. Head-to-head goals scored
     -> criteria 2-4 are RE-APPLIED to any teams that remain tied
  5. Overall goal difference (all group matches)
  6. Overall goals scored (all group matches)
  7. Fair-play / team-conduct points        -- NOT modelled (no card data)
  8. FIFA/Coca-Cola Men's World Ranking (most recent, then earlier editions)
  (a uniform random "lot" is kept only as an absolute last resort to guarantee
   a strict order; it almost never triggers because FIFA points are distinct.)

Ranking the 12 THIRD-placed teams to pick the best 8 (no head-to-head, since
they are in different groups):
  Points -> Overall GD -> Overall goals scored -> Fair play (skipped) ->
  FIFA World Ranking.

`set_h2h_first(False)` switches the within-group order back to the pre-2026
"overall GD first" convention, for sensitivity analysis.

Matches are 5-tuples: (group, home, away, home_goals, away_goals).
"""


def team_table(teams, matches):
    """Stats for `teams` over `matches`. Only matches whose BOTH participants
    are in `teams` count, so this serves both the overall table (all group
    matches) and any head-to-head mini-table (same matches, smaller team set)."""
    teams = set(teams)
    stats = {t: dict(pld=0, w=0, d=0, l=0, gf=0, ga=0, gd=0, pts=0) for t in teams}
    for (_g, home, away, hg, ag) in matches:
        if home not in teams or away not in teams or hg is None or ag is None:
            continue
        sh, sa = stats[home], stats[away]
        sh["pld"] += 1; sa["pld"] += 1
        sh["gf"] += hg; sh["ga"] += ag
        sa["gf"] += ag; sa["ga"] += hg
        if hg > ag:
            sh["w"] += 1; sh["pts"] += 3; sa["l"] += 1
        elif hg < ag:
            sa["w"] += 1; sa["pts"] += 3; sh["l"] += 1
        else:
            sh["d"] += 1; sa["d"] += 1; sh["pts"] += 1; sa["pts"] += 1
    for s in stats.values():
        s["gd"] = s["gf"] - s["ga"]
    return stats


# --- individual tiebreak criteria: each returns {team -> value}, higher better,
#     evaluated on the CURRENT tied subset (so head-to-head re-applies correctly)

def _h2h_pts(subset, gm, overall):
    t = team_table(subset, gm); return {x: t[x]["pts"] for x in subset}

def _h2h_gd(subset, gm, overall):
    t = team_table(subset, gm); return {x: t[x]["gd"] for x in subset}

def _h2h_gf(subset, gm, overall):
    t = team_table(subset, gm); return {x: t[x]["gf"] for x in subset}

def _ov_gd(subset, gm, overall):
    return {x: overall[x]["gd"] for x in subset}

def _ov_gf(subset, gm, overall):
    return {x: overall[x]["gf"] for x in subset}


_H2H_FIRST = True  # 2026 default; flip with set_h2h_first for sensitivity runs


def set_h2h_first(flag):
    global _H2H_FIRST
    _H2H_FIRST = bool(flag)


def _criteria():
    if _H2H_FIRST:
        return [_h2h_pts, _h2h_gd, _h2h_gf, _ov_gd, _ov_gf]      # 2026 rules
    return [_ov_gd, _ov_gf, _h2h_pts, _h2h_gd, _h2h_gf]          # pre-2026 rules


def _resolve(subset, gm, overall, criteria, fifa_points, lots):
    """Order a set of teams already equal on points, applying `criteria` in
    order; head-to-head criteria recompute on the current subset (re-application).
    Final fallback: FIFA ranking points, then a uniform random lot."""
    if len(subset) == 1:
        return list(subset)
    if not criteria:
        return sorted(subset, key=lambda t: (fifa_points.get(t, 0.0), lots[t]),
                      reverse=True)
    crit = criteria[0]
    vals = crit(subset, gm, overall)
    ordered = []
    for v in sorted(set(vals.values()), reverse=True):
        part = [t for t in subset if vals[t] == v]
        if len(part) == 1:
            ordered.append(part[0])
        elif len(part) == len(subset):
            # this criterion separated nobody -> advance to the next criterion
            ordered.extend(_resolve(part, gm, overall, criteria[1:], fifa_points, lots))
        else:
            # a smaller still-tied block -> re-run from the full criteria list so
            # head-to-head is recomputed among just these teams
            ordered.extend(_resolve(part, gm, overall, criteria, fifa_points, lots))
    return ordered


def rank_group(teams, group_matches, fifa_points, lots):
    """Return (ranked_teams, overall_stats); ranked_teams is best-first (1st..4th)."""
    overall = team_table(teams, group_matches)
    by_pts = sorted(teams, key=lambda t: overall[t]["pts"], reverse=True)
    criteria = _criteria()
    ranked = []
    i = 0
    while i < len(by_pts):
        j = i
        while j + 1 < len(by_pts) and overall[by_pts[j + 1]]["pts"] == overall[by_pts[i]]["pts"]:
            j += 1
        block = by_pts[i:j + 1]
        if len(block) == 1:
            ranked.append(block[0])
        else:
            ranked.extend(_resolve(block, group_matches, overall, criteria, fifa_points, lots))
        i = j + 1
    return ranked, overall


def rank_best_thirds(third_entries, fifa_points, lots):
    """Rank the 12 third-placed teams; the top 8 advance. Criteria: points,
    overall GD, overall goals scored, FIFA ranking, then lot (no head-to-head)."""
    def key(entry):
        team, s = entry
        return (s["pts"], s["gd"], s["gf"], fifa_points.get(team, 0.0), lots[team])
    return sorted(third_entries, key=key, reverse=True)
