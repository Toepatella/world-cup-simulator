"""
Team strength ratings for the 2026 FIFA World Cup.

PRIMARY model metric: World Football Elo rating (eloratings.net), snapshot
17 June 2026. Elo is the standard published metric for football match
prediction; eloratings.net itself notes Elo has the highest predictive
capability for football matches. Values were sourced from eloratings.net via
the Wikipedia "World Football Elo Ratings" data table (dated 17 June 2026)
and cross-checked against footballratings.org.

SECONDARY metric (used only as the regulation's final tiebreaker and as a
robustness cross-check): FIFA/Coca-Cola Men's World Ranking points, official
release of 11 June 2026 (inside.fifa.com).

Both were gathered and cross-checked by an automated verification pass; the
group compositions and played results they are paired with were confirmed
against ESPN/NBC/Sky/Fox with zero discrepancies.

Keys here match data.GROUPS exactly (ASCII canonical names).
"""

ELO_AS_OF = "2026-06-17"
ELO_SOURCE = (
    "World Football Elo Ratings (eloratings.net), snapshot 2026-06-17, via the "
    "Wikipedia 'World Football Elo Ratings' data table, cross-checked vs "
    "footballratings.org."
)

# World Football Elo rating per team (higher = stronger).
ELO = {
    "Spain": 2129,
    "Argentina": 2128,
    "France": 2084,
    "England": 2055,
    "Colombia": 1998,
    "Brazil": 1978,
    "Portugal": 1967,
    "Netherlands": 1944,
    "Germany": 1939,
    "Norway": 1929,
    "Japan": 1910,
    "Ecuador": 1890,
    "Croatia": 1881,
    "Mexico": 1881,
    "Belgium": 1879,
    "Uruguay": 1870,
    "Switzerland": 1865,
    "Austria": 1857,
    "Turkey": 1849,
    "Morocco": 1840,
    "Australia": 1839,
    "Senegal": 1839,
    "Scotland": 1794,
    "South Korea": 1786,
    "Paraguay": 1780,
    "United States": 1780,
    "Canada": 1767,
    "Algeria": 1759,
    "Iran": 1756,
    "Sweden": 1755,
    "Ivory Coast": 1743,
    "Czech Republic": 1712,
    "Egypt": 1711,
    "Uzbekistan": 1698,
    "Panama": 1683,
    "DR Congo": 1674,
    "Jordan": 1653,
    "Bosnia and Herzegovina": 1616,
    "Cape Verde": 1606,
    "Saudi Arabia": 1598,
    "Iraq": 1592,
    "Tunisia": 1585,
    "New Zealand": 1578,
    "Ghana": 1557,
    "Haiti": 1536,
    "South Africa": 1511,
    "Qatar": 1447,
    "Curacao": 1427,
}

FIFA_AS_OF = "2026-06-11"
FIFA_SOURCE = "FIFA/Coca-Cola Men's World Ranking, official release 2026-06-11."

# FIFA ranking points per team. Used as the official final tiebreaker
# (post-2026 rules: drawing of lots was replaced by the FIFA ranking) and as
# an alternative strength metric for robustness checks.
FIFA_POINTS = {
    "Argentina": 1877.27,
    "Spain": 1874.71,
    "France": 1870.70,
    "England": 1828.02,
    "Portugal": 1767.85,
    "Brazil": 1765.86,
    "Morocco": 1755.10,
    "Netherlands": 1753.57,
    "Belgium": 1742.24,
    "Germany": 1735.77,
    "Croatia": 1714.87,
    "Colombia": 1698.35,
    "Mexico": 1687.48,
    "Senegal": 1684.07,
    "Uruguay": 1673.07,
    "United States": 1671.23,
    "Japan": 1661.58,
    "Switzerland": 1650.06,
    "Iran": 1619.58,
    "Turkey": 1605.73,
    "Ecuador": 1598.52,
    "Austria": 1597.40,
    "South Korea": 1591.63,
    "Algeria": 1571.03,
    "Egypt": 1562.37,
    "Canada": 1559.48,
    "Norway": 1557.44,
    "Ivory Coast": 1540.87,
    "Panama": 1539.16,
    "Czech Republic": 1505.74,
    "Paraguay": 1505.35,
    "Scotland": 1503.34,
    "Sweden": 1509.79,
    "Australia": 1579.34,
    "Tunisia": 1476.41,
    "DR Congo": 1474.43,
    "Uzbekistan": 1458.73,
    "Qatar": 1450.31,
    "Iraq": 1446.28,
    "South Africa": 1428.38,
    "Saudi Arabia": 1423.88,
    "Bosnia and Herzegovina": 1387.22,
    "Jordan": 1387.74,
    "Cape Verde": 1371.11,
    "Ghana": 1346.88,
    "Curacao": 1294.77,
    "Haiti": 1293.10,
    "New Zealand": 1275.58,
}


# ---------------------------------------------------------------------------
# Live rating: "FIFA points as an Elo system".
#
# The model no longer predicts from the static World Football Elo table above
# (kept only as a historical cross-check). Instead the FIFA/Coca-Cola ranking
# points are used AS the Elo rating: every team starts at its pre-tournament
# FIFA_POINTS value, and the rating is updated after every *played* match with
# the standard football-Elo rule
#
#     r_A += K * (W_A - We_A) ,   We_A = 1 / (1 + 10 ** (-(r_A - r_B) / 400))
#
# where W_A is A's result (1 win / 0.5 draw / 0 loss), K = importance * G, the
# importance is FIFA's World Cup coefficient (50 up to the QFs, 60 from the QFs
# onward) and G is the football-Elo goal-difference multiplier. Penalty
# shootouts count as draws (the eloratings.net convention). The update is
# zero-sum, so the total rating mass is conserved.
#
# RATING holds the current (live) values and is what the simulator reads for
# both prediction and the final FIFA-ranking tiebreaker; call update_live()
# once the played-match list is known.
# ---------------------------------------------------------------------------

RATING = dict(FIFA_POINTS)  # live values; overwritten by update_live()

K_BASE_UP_TO_QF = 50.0      # FIFA importance, group stage .. Round of 16
K_BASE_FROM_QF = 60.0       # FIFA importance, quarter-finals onward


def match_importance(round_name):
    """FIFA World Cup importance coefficient for a match, from its round name."""
    r = (round_name or "").strip().lower()
    if (r.startswith("quarter") or r.startswith("semi") or r.startswith("final")
            or r.startswith("match for third") or r.startswith("third")):
        return K_BASE_FROM_QF
    return K_BASE_UP_TO_QF  # group stage, Round of 32, Round of 16


def _goal_diff_multiplier(gd):
    """Football-Elo weight for the winning margin (eloratings.net scheme)."""
    gd = abs(int(gd))
    if gd <= 1:
        return 1.0
    if gd == 2:
        return 1.5
    return (11.0 + gd) / 8.0


def expected_result(rating_a, rating_b):
    """Elo expected score for A against B (win=1, draw=0.5)."""
    return 1.0 / (1.0 + 10.0 ** (-(rating_a - rating_b) / 400.0))


def apply_match(rating, team_a, team_b, result_a, gd, importance,
                host_a=0.0, host_b=0.0):
    """Update `rating` in place for one played match (result_a in {1, 0.5, 0})."""
    if team_a not in rating or team_b not in rating:
        return
    we_a = expected_result(rating[team_a] + host_a, rating[team_b] + host_b)
    delta = importance * _goal_diff_multiplier(gd) * (result_a - we_a)
    rating[team_a] += delta
    rating[team_b] -= delta


def live_ratings(played, base=None, host_adv=0.0):
    """Return live ratings after applying `played` matches to a `base` snapshot.

    `played` is a chronological list of dicts, each with keys team1, team2,
    result_a (1/0.5/0 for team1), gd (winning margin), round (for importance),
    and optional host1/host2 flags (team played at home -> gets host_adv in the
    expected-result calc). `base` defaults to the pre-tournament FIFA_POINTS.
    """
    rating = dict(base if base is not None else FIFA_POINTS)
    for m in played:
        ha = host_adv if m.get("host1") else 0.0
        hb = host_adv if m.get("host2") else 0.0
        apply_match(rating, m["team1"], m["team2"], m["result_a"], m["gd"],
                    match_importance(m.get("round")), ha, hb)
    return rating


def update_live(played, base=None, host_adv=0.0):
    """Compute live ratings and store them in the module-level RATING dict."""
    global RATING
    RATING = live_ratings(played, base=base, host_adv=host_adv)
    return RATING


def check_complete(teams):
    """Ensure every team has a starting (FIFA) rating; Elo is optional legacy."""
    missing_fifa = [t for t in teams if t not in FIFA_POINTS]
    assert not missing_fifa, f"missing FIFA points: {missing_fifa}"
    return True
