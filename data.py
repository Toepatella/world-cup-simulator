"""
Static tournament data for the 2026 FIFA World Cup group stage.

Snapshot date: 2026-06-18.
Source: per-group Wikipedia pages ("2026 FIFA World Cup Group A" ... "Group L"),
cross-checked against NBC/ESPN consolidated standings.

A match is FIXED (already played) if it has integer scores; it is REMAINING
(to be simulated) if its scores are None. Each group of 4 plays 6 matches
(round-robin), so there are 12 * 6 = 72 group matches in total.

Naming: ASCII canonical names are used as the single key across all modules
(data, ratings, output). E.g. "Czech Republic", "Curacao", "Ivory Coast",
"DR Congo", "Bosnia and Herzegovina", "United States", "Turkey".
"""

import json
import urllib.request

# group letter -> the four teams
GROUPS = {
    "A": ["Mexico", "South Korea", "South Africa", "Czech Republic"],
    "B": ["Canada", "Switzerland", "Bosnia and Herzegovina", "Qatar"],
    "C": ["Brazil", "Scotland", "Morocco", "Haiti"],
    "D": ["United States", "Australia", "Turkey", "Paraguay"],
    "E": ["Germany", "Ivory Coast", "Ecuador", "Curacao"],
    "F": ["Sweden", "Netherlands", "Japan", "Tunisia"],
    "G": ["Belgium", "Iran", "New Zealand", "Egypt"],
    "H": ["Spain", "Uruguay", "Saudi Arabia", "Cape Verde"],
    "I": ["France", "Norway", "Senegal", "Iraq"],
    "J": ["Argentina", "Austria", "Jordan", "Algeria"],
    "K": ["Colombia", "Portugal", "DR Congo", "Uzbekistan"],
    "L": ["England", "Ghana", "Croatia", "Panama"],
}

# Host nations get a venue (home) advantage in every group match because they
# play in their own country. No two hosts share a group, so there are no
# host-vs-host fixtures.
HOSTS = {"United States", "Mexico", "Canada"}

# All 72 group matches: (group, home, away, home_goals, away_goals).
# home_goals/away_goals are None for matches not yet played as of 2026-06-18.
# "home" is the nominal first-listed team from the official fixture list; it
# carries no advantage in the model except for the three host nations (handled
# via HOSTS, by venue, not by nominal home/away).
MATCHES = [
    # ---- Group A (matchdays 1-2 complete) ----
    ("A", "Mexico", "South Africa", 2, 0),
    ("A", "South Korea", "Czech Republic", 2, 1),
    ("A", "Czech Republic", "South Africa", 1, 1),
    ("A", "Mexico", "South Korea", 1, 0),
    ("A", "Czech Republic", "Mexico", None, None),
    ("A", "South Africa", "South Korea", None, None),

    # ---- Group B (matchdays 1-2 complete) ----
    ("B", "Canada", "Bosnia and Herzegovina", 1, 1),
    ("B", "Qatar", "Switzerland", 1, 1),
    ("B", "Switzerland", "Bosnia and Herzegovina", 4, 1),
    ("B", "Canada", "Qatar", 6, 0),
    ("B", "Switzerland", "Canada", None, None),
    ("B", "Bosnia and Herzegovina", "Qatar", None, None),

    # ---- Group C (matchday 1 complete) ----
    ("C", "Brazil", "Morocco", 1, 1),
    ("C", "Haiti", "Scotland", 0, 1),
    ("C", "Scotland", "Morocco", None, None),
    ("C", "Brazil", "Haiti", None, None),
    ("C", "Scotland", "Brazil", None, None),
    ("C", "Morocco", "Haiti", None, None),

    # ---- Group D (matchday 1 complete) ----
    ("D", "United States", "Paraguay", 4, 1),
    ("D", "Australia", "Turkey", 2, 0),
    ("D", "United States", "Australia", None, None),
    ("D", "Turkey", "Paraguay", None, None),
    ("D", "Turkey", "United States", None, None),
    ("D", "Paraguay", "Australia", None, None),

    # ---- Group E (matchday 1 complete) ----
    ("E", "Germany", "Curacao", 7, 1),
    ("E", "Ivory Coast", "Ecuador", 1, 0),
    ("E", "Germany", "Ivory Coast", None, None),
    ("E", "Ecuador", "Curacao", None, None),
    ("E", "Curacao", "Ivory Coast", None, None),
    ("E", "Ecuador", "Germany", None, None),

    # ---- Group F (matchday 1 complete) ----
    ("F", "Netherlands", "Japan", 2, 2),
    ("F", "Sweden", "Tunisia", 5, 1),
    ("F", "Netherlands", "Sweden", None, None),
    ("F", "Tunisia", "Japan", None, None),
    ("F", "Japan", "Sweden", None, None),
    ("F", "Tunisia", "Netherlands", None, None),

    # ---- Group G (matchday 1 complete) ----
    ("G", "Belgium", "Egypt", 1, 1),
    ("G", "Iran", "New Zealand", 2, 2),
    ("G", "Belgium", "Iran", None, None),
    ("G", "New Zealand", "Egypt", None, None),
    ("G", "Egypt", "Iran", None, None),
    ("G", "New Zealand", "Belgium", None, None),

    # ---- Group H (matchday 1 complete) ----
    ("H", "Spain", "Cape Verde", 0, 0),
    ("H", "Saudi Arabia", "Uruguay", 1, 1),
    ("H", "Spain", "Saudi Arabia", None, None),
    ("H", "Uruguay", "Cape Verde", None, None),
    ("H", "Cape Verde", "Saudi Arabia", None, None),
    ("H", "Uruguay", "Spain", None, None),

    # ---- Group I (matchday 1 complete) ----
    ("I", "France", "Senegal", 3, 1),
    ("I", "Iraq", "Norway", 1, 4),
    ("I", "France", "Iraq", None, None),
    ("I", "Norway", "Senegal", None, None),
    ("I", "Norway", "France", None, None),
    ("I", "Senegal", "Iraq", None, None),

    # ---- Group J (matchday 1 complete) ----
    ("J", "Argentina", "Algeria", 3, 0),
    ("J", "Austria", "Jordan", 3, 1),
    ("J", "Argentina", "Austria", None, None),
    ("J", "Jordan", "Algeria", None, None),
    ("J", "Algeria", "Austria", None, None),
    ("J", "Jordan", "Argentina", None, None),

    # ---- Group K (matchday 1 complete) ----
    ("K", "Portugal", "DR Congo", 1, 1),
    ("K", "Uzbekistan", "Colombia", 1, 3),
    ("K", "Portugal", "Uzbekistan", None, None),
    ("K", "Colombia", "DR Congo", None, None),
    ("K", "Colombia", "Portugal", None, None),
    ("K", "DR Congo", "Uzbekistan", None, None),

    # ---- Group L (matchday 1 complete) ----
    ("L", "England", "Croatia", 4, 2),
    ("L", "Ghana", "Panama", 1, 0),
    ("L", "England", "Ghana", None, None),
    ("L", "Panama", "Croatia", None, None),
    ("L", "Panama", "England", None, None),
    ("L", "Croatia", "Ghana", None, None),
]


def played_matches():
    """All matches with a final score (treated as fixed)."""
    return [m for m in MATCHES if m[3] is not None]


def remaining_matches():
    """All matches still to be played (to be simulated)."""
    return [(g, h, a) for (g, h, a, hs, as_) in MATCHES if hs is None]


def all_teams():
    teams = []
    for g in GROUPS.values():
        teams.extend(g)
    return teams


def _sanity_check():
    """Validate the dataset is internally consistent."""
    teams = all_teams()
    assert len(teams) == 48, f"expected 48 teams, got {len(teams)}"
    assert len(set(teams)) == 48, "duplicate team names across groups"
    assert len(MATCHES) == 72, f"expected 72 matches, got {len(MATCHES)}"
    # every group must have exactly the 6 round-robin pairings of its 4 teams
    from itertools import combinations
    for g, members in GROUPS.items():
        pairs = {frozenset(p) for p in combinations(members, 2)}
        got = {frozenset((h, a)) for (gg, h, a, _, _) in MATCHES if gg == g}
        assert len(members) == 4, f"group {g} does not have 4 teams"
        assert pairs == got, f"group {g} fixtures != round-robin: {pairs ^ got}"
    return True


REMOTE_JSON_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
REMOTE_JSON_USER_AGENT = "world-cup-simulator/1.0"


TEAM_ALIAS_MAP = {
    "USA": "United States",
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
    "Curaçao": "Curacao",
    "Cura�ao": "Curacao",
}


def _normalize_team_name(name):
    if not isinstance(name, str):
        return name
    name = name.strip()
    if name in TEAM_ALIAS_MAP:
        return TEAM_ALIAS_MAP[name]
    # support some common formatting variants
    if name.lower() == "usa":
        return "United States"
    if name.lower().replace("&", "and").replace("  ", " ") == "bosnia and herzegovina":
        return "Bosnia and Herzegovina"
    if "cura" in name.lower():
        return "Curacao"
    return name


def _parse_remote_match(obj):
    group = obj.get("group")
    if not group:
        return None
    group = group.strip()
    if group.lower().startswith("group "):
        group = group.split(None, 1)[1]
    if group not in GROUPS:
        return None

    team1 = _normalize_team_name(obj.get("team1"))
    team2 = _normalize_team_name(obj.get("team2"))
    if not team1 or not team2:
        return None

    score = obj.get("score") or {}
    ft = score.get("ft")
    if (isinstance(ft, list) and len(ft) >= 2 and
            ft[0] is not None and ft[1] is not None):
        try:
            home_goals = int(ft[0])
            away_goals = int(ft[1])
        except (TypeError, ValueError):
            home_goals = away_goals = None
    else:
        home_goals = away_goals = None

    if team1 not in GROUPS[group] or team2 not in GROUPS[group]:
        return None

    return (group, team1, team2, home_goals, away_goals)


_REMOTE_CACHE = None


def _fetch_remote_raw(timeout=15):
    """Fetch (and cache for this process) the full worldcup.json document."""
    global _REMOTE_CACHE
    if _REMOTE_CACHE is None:
        req = urllib.request.Request(
            REMOTE_JSON_URL,
            headers={"User-Agent": REMOTE_JSON_USER_AGENT,
                     "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            _REMOTE_CACHE = json.load(resp)
    return _REMOTE_CACHE


def _score_pair(score, key):
    """Return (a, b) ints for score[key] if it is a valid pair, else None."""
    v = (score or {}).get(key)
    if isinstance(v, list) and len(v) >= 2 and v[0] is not None and v[1] is not None:
        try:
            return int(v[0]), int(v[1])
        except (TypeError, ValueError):
            return None
    return None


def match_outcome(score):
    """Resolve a score dict into (result_a, gd, winner).

    result_a is team1's Elo result (1 win / 0.5 draw / 0 loss); gd is the
    winning margin used for the Elo goal-difference weight; winner is 0 (team1),
    1 (team2), or None for a genuine draw. Priority: penalties decide the winner
    but count as a draw for the rating (level after extra time); otherwise extra
    time if present, else full time. Returns None if the match is unplayed.
    """
    pens = _score_pair(score, "p")
    if pens is not None:                       # shootout: level after ET
        return 0.5, 0, (0 if pens[0] > pens[1] else 1)
    decided = _score_pair(score, "et") or _score_pair(score, "ft")
    if decided is None:
        return None
    a, b = decided
    gd = abs(a - b)
    if a > b:
        return 1.0, gd, 0
    if a < b:
        return 0.0, gd, 1
    return 0.5, 0, None


def _is_knockout_round(round_name):
    r = (round_name or "").strip().lower()
    return (r.startswith("round of") or r.startswith("quarter")
            or r.startswith("semi") or r.startswith("final")
            or r.startswith("match for third") or r.startswith("third"))


def fetch_latest_matches(timeout=15):
    """Fetch the latest group-stage match results from the public worldcup.json file."""
    raw = _fetch_remote_raw(timeout=timeout)

    matches = []
    for entry in raw.get("matches", []):
        parsed = _parse_remote_match(entry)
        if parsed is not None:
            matches.append(parsed)

    if not matches:
        raise ValueError("No valid group-stage matches were found in the remote dataset")

    matches.sort(key=lambda m: (m[0], m[1], m[2]))
    return matches


def fetch_played_matches(timeout=15):
    """Every decided match (group + knockout), in chronological order.

    Returned as dicts consumed by ratings.live_ratings: team1, team2, result_a,
    gd, round, and host1/host2 flags (a host nation plays its group games at
    home, so it gets the venue boost in the rating update). Ordered by date so
    ratings can be updated after every game.
    """
    raw = _fetch_remote_raw(timeout=timeout)
    valid = set(all_teams())
    out = []
    for entry in raw.get("matches", []):
        t1 = _normalize_team_name(entry.get("team1"))
        t2 = _normalize_team_name(entry.get("team2"))
        if t1 not in valid or t2 not in valid:      # skips "W89"/"L101" placeholders
            continue
        outcome = match_outcome(entry.get("score"))
        if outcome is None:
            continue
        result_a, gd, _winner = outcome
        round_name = str(entry.get("round", "")).strip()
        is_group = not _is_knockout_round(round_name)
        out.append({
            "team1": t1, "team2": t2,
            "result_a": result_a, "gd": gd,
            "round": round_name,
            "host1": is_group and t1 in HOSTS,
            "host2": is_group and t2 in HOSTS,
            "date": entry.get("date", ""),
            "num": entry.get("num") or 0,
        })
    out.sort(key=lambda m: (m["date"], m["num"], m["team1"]))
    return out


def played_matches_chrono(timeout=15):
    """Chronological decided matches for rating updates, with a local fallback.

    Prefers the remote feed (full detail: extra time, penalties, knockout
    rounds). If it is unreachable, falls back to the local group-stage MATCHES.
    """
    try:
        return fetch_played_matches(timeout=timeout)
    except Exception:
        out = []
        for (g, h, a, hs, as_) in MATCHES:
            if hs is None:
                continue
            gd = abs(hs - as_)
            result_a = 1.0 if hs > as_ else (0.0 if hs < as_ else 0.5)
            out.append({
                "team1": h, "team2": a,
                "result_a": result_a, "gd": gd,
                "round": g,
                "host1": h in HOSTS, "host2": a in HOSTS,
                "date": "", "num": 0,
            })
        return out


def official_knockout_results(timeout=15):
    """Played knockout matches as (round, team1, team2, winner, loser).

    Only real teams count (placeholder slots like "W89" are skipped) and only
    matches with a decided result are returned. Callers apply these by
    participant identity, so no bracket-slot numbers are needed here.
    """
    try:
        raw = _fetch_remote_raw(timeout=timeout)
    except Exception:
        return []
    valid = set(all_teams())
    results = []
    for entry in raw.get("matches", []):
        round_name = str(entry.get("round", "")).strip()
        if not _is_knockout_round(round_name):
            continue
        t1 = _normalize_team_name(entry.get("team1"))
        t2 = _normalize_team_name(entry.get("team2"))
        if t1 not in valid or t2 not in valid:
            continue
        outcome = match_outcome(entry.get("score"))
        if outcome is None:
            continue
        _result_a, _gd, winner = outcome
        if winner is None:                          # a knockout must have a winner
            continue
        w = t1 if winner == 0 else t2
        l = t2 if winner == 0 else t1
        results.append((round_name, t1, t2, w, l))
    return results


def refresh_matches(timeout=15, verbose=True):
    """Update MATCHES from the remote worldcup.json dataset if available."""
    try:
        latest = fetch_latest_matches(timeout=timeout)
        global MATCHES
        if latest != MATCHES:
            if verbose:
                print(f"Fetched latest group-stage data from {REMOTE_JSON_URL}")
            MATCHES = latest
        return latest
    except Exception as exc:
        if verbose:
            print("Warning: unable to refresh live match data:", exc)
        return None


if __name__ == "__main__":
    _sanity_check()
    print("data.py OK:", len(all_teams()), "teams,",
          len(played_matches()), "played,",
          len(remaining_matches()), "remaining")
