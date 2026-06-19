"""
Unit tests for the tiebreaker logic -- the most correctness-critical piece.

The key test constructs a group where the 2026 rule (head-to-head first) and
the pre-2026 rule (overall goal difference first) produce DIFFERENT winners,
and asserts each ordering comes out as expected.
"""

import tiebreakers as tb


def test_team_table_basic():
    matches = [
        ("X", "A", "B", 2, 0),   # A win
        ("X", "A", "C", 1, 1),   # draw
        ("X", "B", "C", 0, 3),   # C win
    ]
    s = tb.team_table(["A", "B", "C"], matches)
    assert s["A"]["pts"] == 4 and s["A"]["gd"] == 2 and s["A"]["gf"] == 3
    assert s["B"]["pts"] == 0 and s["B"]["gd"] == -5
    assert s["C"]["pts"] == 4 and s["C"]["gd"] == 3
    print("test_team_table_basic OK")


def _three_way_group():
    """A, B, C all finish on 6 points; D on 0.
    Head-to-head among {A,B,C}:  A (+2 gd) > B (0) > C (-2)
    Overall goal difference:     C (+7) > A (+3) > B (+1)
    => the two rule-sets must disagree on who finishes 1st.
    """
    teams = ["A", "B", "C", "D"]
    matches = [
        ("T", "A", "B", 3, 0),
        ("T", "B", "C", 3, 0),
        ("T", "C", "A", 1, 0),
        ("T", "A", "D", 1, 0),
        ("T", "B", "D", 1, 0),
        ("T", "C", "D", 9, 0),
    ]
    fifa = {"A": 1500, "B": 1400, "C": 1300, "D": 1200}
    lots = {"A": 0.1, "B": 0.2, "C": 0.3, "D": 0.4}
    return teams, matches, fifa, lots


def test_h2h_first_2026():
    teams, matches, fifa, lots = _three_way_group()
    tb.set_h2h_first(True)
    ranked, _ = tb.rank_group(teams, matches, fifa, lots)
    assert ranked == ["A", "B", "C", "D"], ranked
    print("test_h2h_first_2026 OK ->", ranked)


def test_overall_first_pre2026():
    teams, matches, fifa, lots = _three_way_group()
    tb.set_h2h_first(False)
    ranked, _ = tb.rank_group(teams, matches, fifa, lots)
    assert ranked == ["C", "A", "B", "D"], ranked
    print("test_overall_first_pre2026 OK ->", ranked)
    tb.set_h2h_first(True)  # restore default


def test_best_thirds_order():
    # higher points beats higher GD; GD breaks equal points; fifa breaks the rest
    entries = [
        ("P", dict(pts=4, gd=1, gf=3)),
        ("Q", dict(pts=4, gd=3, gf=5)),
        ("R", dict(pts=3, gd=9, gf=9)),
        ("S", dict(pts=4, gd=3, gf=5)),   # ties Q on pts/gd/gf -> fifa decides
    ]
    fifa = {"P": 1, "Q": 50, "R": 1, "S": 40}
    lots = {"P": 0.5, "Q": 0.5, "R": 0.5, "S": 0.5}
    ranked = [t for t, _ in tb.rank_best_thirds(entries, fifa, lots)]
    assert ranked == ["Q", "S", "P", "R"], ranked
    print("test_best_thirds_order OK ->", ranked)


if __name__ == "__main__":
    test_team_table_basic()
    test_h2h_first_2026()
    test_overall_first_pre2026()
    test_best_thirds_order()
    print("\nAll tiebreaker tests passed.")
