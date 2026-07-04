"""
2026 FIFA World Cup knockout bracket (Round of 32 -> Final).

Structure verified against Wikipedia "2026 FIFA World Cup knockout stage" and
ESPN's published bracket (the two agree on the R32 template and the R16 tree,
which is NOT a simple consecutive pairing).

Slot specs used in the R32 template:
  ('W', 'A')  winner of Group A
  ('R', 'A')  runner-up of Group A
  ('T',  74)  the best-third team allocated to match 74's third-place slot

THIRD_SLOTS gives, per third-place slot, the set of groups whose third-placed
team may be allocated there (straight from the official bracket). Each set
excludes its own match's group winner, so a third can never be drawn against a
team from its own group.

Allocating the 8 best thirds to the 8 slots is a bipartite perfect matching of
{the 8 qualifying groups} onto {the 8 slots} respecting these sets. FIFA uses a
fixed 495-row lookup table for this; we instead compute a deterministic valid
matching (most-constrained-slot first, then alphabetical). This honours every
official constraint -- including no same-group rematch -- and yields a
legitimate bracket; for the minority of group-combinations where FIFA's lookup
would pick a different *valid* matching, a third team's specific opponent may
differ. That is a second-order effect on win probabilities and is the only
knockout-structure approximation in the model (see README).
"""

# Round of 32: (match_no, home_spec, away_spec)
R32 = [
    (73, ("R", "A"), ("R", "B")),
    (74, ("W", "E"), ("T", 74)),
    (75, ("W", "F"), ("R", "C")),
    (76, ("W", "C"), ("R", "F")),
    (77, ("W", "I"), ("T", 77)),
    (78, ("R", "E"), ("R", "I")),
    (79, ("W", "A"), ("T", 79)),
    (80, ("W", "L"), ("T", 80)),
    (81, ("W", "D"), ("T", 81)),
    (82, ("W", "G"), ("T", 82)),
    (83, ("R", "K"), ("R", "L")),
    (84, ("W", "H"), ("R", "J")),
    (85, ("W", "B"), ("T", 85)),
    (86, ("W", "J"), ("R", "H")),
    (87, ("W", "K"), ("T", 87)),
    (88, ("R", "D"), ("R", "G")),
]

# third-place slot (match_no) -> groups eligible to fill it
THIRD_SLOTS = {
    74: set("ABCDF"),
    77: set("CDFGH"),
    79: set("CEFHI"),
    80: set("EHIJK"),
    81: set("BEFIJ"),
    82: set("AEHIJ"),
    85: set("EFGIJ"),
    87: set("DEIJL"),
}

# Round of 16 -> Final. match_no -> (source_home, source_away)
#   ('Wm', n) winner of match n ; ('Lm', n) loser of match n
LATER = {
    89: (("Wm", 74), ("Wm", 77)),
    90: (("Wm", 73), ("Wm", 75)),
    91: (("Wm", 76), ("Wm", 78)),
    92: (("Wm", 79), ("Wm", 80)),
    93: (("Wm", 83), ("Wm", 84)),
    94: (("Wm", 81), ("Wm", 82)),
    95: (("Wm", 86), ("Wm", 88)),
    96: (("Wm", 85), ("Wm", 87)),
    97: (("Wm", 89), ("Wm", 90)),
    98: (("Wm", 93), ("Wm", 94)),
    99: (("Wm", 91), ("Wm", 92)),
    100: (("Wm", 95), ("Wm", 96)),
    101: (("Wm", 97), ("Wm", 98)),
    102: (("Wm", 99), ("Wm", 100)),
    103: (("Lm", 101), ("Lm", 102)),   # third-place play-off
    104: (("Wm", 101), ("Wm", 102)),   # final
}

R32_NOS = list(range(73, 89))
R16_NOS = list(range(89, 97))
QF_NOS = list(range(97, 101))
SF_NOS = [101, 102]
FINAL_NO = 104
THIRD_PLACE_NO = 103
THIRD_SLOT_NOS = sorted(THIRD_SLOTS.keys())

# Official knockout results are applied by PARTICIPANT identity, not by bracket
# slot number: the seeding (group winners/runners/thirds -> R32 template) fully
# determines who meets whom, and a played game's winner is looked up from the
# {frozenset({team_a, team_b}): winner} map the simulator builds from the public
# data source. This keeps the official results consistent with the seeding
# instead of forcing team pairs into fixed slots (which double-booked teams).

# Official FIFA 2026 Round of 32 third-place assignments for the currently
# published qualifying combination (groups B, D, E, F, I, J, K, L).
# This fixes the current bracket so Germany faces Paraguay (match 74) rather
# than an arbitrary valid-but-non-official third-place pairing.
OFFICIAL_THIRD_ASSIGNMENTS = {
    frozenset("BDEFIJKL"): {
        74: "D",
        77: "F",
        79: "E",
        80: "K",
        81: "B",
        82: "I",
        85: "J",
        87: "L",
    },
}


def allocate_thirds(qualified_groups, rng=None):
    """Assign the qualifying third-place GROUPS to the 8 third-place slots.

    qualified_groups: iterable of exactly 8 group letters.
    Returns {slot_match_no -> group_letter}.

    For the currently published 2026 FIFA combination (groups B, D, E, F, I, J,
    K, L), we use the official FIFA match table so the Round of 32 pairings
    match the published bracket exactly. For any other combination, we still
    fall back to a valid matching that satisfies the official constraints.
    """
    qualified = set(qualified_groups)
    official = OFFICIAL_THIRD_ASSIGNMENTS.get(frozenset(qualified))
    if official is not None:
        return dict(official)

    if rng is None:
        order = sorted(THIRD_SLOT_NOS,
                       key=lambda s: (len(THIRD_SLOTS[s] & qualified), s))
    else:
        # most-constrained-first still guides the search; randomise within
        order = sorted(THIRD_SLOT_NOS,
                       key=lambda s: (len(THIRD_SLOTS[s] & qualified),
                                      rng.random()))
    assign = {}
    used = set()

    def backtrack(i):
        if i == len(order):
            return True
        slot = order[i]
        cands = sorted(THIRD_SLOTS[slot] & qualified)
        if rng is not None:
            rng.shuffle(cands)
        for g in cands:
            if g not in used:
                used.add(g); assign[slot] = g
                if backtrack(i + 1):
                    return True
                used.discard(g); del assign[slot]
        return False

    if not backtrack(0):
        raise ValueError(f"no valid third-place allocation for {sorted(qualified)}")
    return assign


def _resolve_r32(spec, winners, runners, thirds_team, third_assignment):
    kind, key = spec
    if kind == "W":
        return winners[key]
    if kind == "R":
        return runners[key]
    if kind == "T":
        return thirds_team[third_assignment[key]]
    raise ValueError(spec)


def play_bracket_with_matches(winners, runners, thirds_team, third_assignment,
                              win_fn, fixed_winners=None):
    """Play the full knockout bracket and return every match's participants.

    winners/runners/thirds_team: dict group_letter -> team name.
    third_assignment: {slot_match_no -> group_letter} from allocate_thirds.
    win_fn(team_a, team_b) -> (winner, loser)  for matches without a result.
    fixed_winners: optional {frozenset({team_a, team_b}): winner} of already
    played knockout games; a match whose seeded participants match a key uses
    the official winner, everything else is predicted by win_fn.

    Returns (parts, winner_of, loser_of) where parts is a dict match_no ->
    (home_team, away_team).
    """
    winner_of, loser_of, parts = {}, {}, {}
    fixed_winners = fixed_winners or {}

    def decide(ht, at):
        w = fixed_winners.get(frozenset((ht, at)))
        if w in (ht, at):                      # official result for this pairing
            return w, (at if w == ht else ht)
        return win_fn(ht, at)                   # not yet played -> predict

    for (no, hspec, aspec) in R32:
        ht = _resolve_r32(hspec, winners, runners, thirds_team, third_assignment)
        at = _resolve_r32(aspec, winners, runners, thirds_team, third_assignment)
        parts[no] = (ht, at)
        winner_of[no], loser_of[no] = decide(ht, at)

    for no in range(89, 105):
        (hk, hn), (ak, an) = LATER[no]
        ht = winner_of[hn] if hk == "Wm" else loser_of[hn]
        at = winner_of[an] if ak == "Wm" else loser_of[an]
        parts[no] = (ht, at)
        winner_of[no], loser_of[no] = decide(ht, at)

    return parts, winner_of, loser_of


def play_bracket(winners, runners, thirds_team, third_assignment, win_fn,
                 fixed_winners=None):
    parts, winner_of, loser_of = play_bracket_with_matches(
        winners, runners, thirds_team, third_assignment, win_fn,
        fixed_winners=fixed_winners)
    return {
        "r16": [winner_of[n] for n in R32_NOS],     # reached R16 (won R32)
        "qf": [winner_of[n] for n in R16_NOS],       # reached QF
        "sf": [winner_of[n] for n in QF_NOS],        # reached SF
        "final": [winner_of[n] for n in SF_NOS],     # reached final
        "champion": winner_of[FINAL_NO],
        "runner_up": loser_of[FINAL_NO],
        "third_place": winner_of[THIRD_PLACE_NO],
        "fourth_place": loser_of[THIRD_PLACE_NO],
    }


def _self_check():
    """Verify a valid allocation exists for all C(12,8)=495 group combinations,
    and report how often more than one valid matching exists (fidelity caveat)."""
    from itertools import combinations
    groups = "ABCDEFGHIJKL"
    multi = 0
    for combo in combinations(groups, 8):
        assign = allocate_thirds(combo)          # raises if none
        assert set(assign.values()) == set(combo)
        assert len(assign) == 8
        for slot, g in assign.items():
            assert g in THIRD_SLOTS[slot]
        if _count_matchings(set(combo)) > 1:
            multi += 1
    total = 495
    print(f"all {total} third-place combinations have a valid allocation")
    print(f"{multi}/{total} combinations admit >1 valid matching "
          f"({100*multi/total:.0f}% where FIFA's lookup may differ from ours)")


def _count_matchings(qualified):
    slots = THIRD_SLOT_NOS
    count = 0

    def bt(i, used):
        nonlocal count
        if i == len(slots):
            count += 1
            return
        for g in THIRD_SLOTS[slots[i]] & qualified:
            if g not in used:
                bt(i + 1, used | {g})
    bt(0, frozenset())
    return count


if __name__ == "__main__":
    # template integrity
    ws = [s[1] for (_n, s, _a) in R32 if s[0] == "W"] + \
         [a[1] for (_n, _s, a) in R32 if a[0] == "W"]
    rs = [s[1] for (_n, s, _a) in R32 if s[0] == "R"] + \
         [a[1] for (_n, _s, a) in R32 if a[0] == "R"]
    assert sorted(ws) == list("ABCDEFGHIJKL"), ws
    assert sorted(rs) == list("ABCDEFGHIJKL"), rs
    print("R32 template OK: 12 winners + 12 runners-up + 8 third slots")
    _self_check()
