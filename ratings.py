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


def check_complete(teams):
    """Ensure every team has an Elo and a FIFA rating."""
    missing_elo = [t for t in teams if t not in ELO]
    missing_fifa = [t for t in teams if t not in FIFA_POINTS]
    assert not missing_elo, f"missing Elo: {missing_elo}"
    assert not missing_fifa, f"missing FIFA points: {missing_fifa}"
    return True
