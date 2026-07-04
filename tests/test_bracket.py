import unittest

import bracket
import data
import ratings


class BracketTests(unittest.TestCase):
    def test_official_third_assignment_for_current_qualifiers(self):
        qualified_groups = ["B", "D", "E", "F", "I", "J", "K", "L"]
        assignment = bracket.allocate_thirds(qualified_groups)
        expected = {
            74: "D",
            77: "F",
            79: "E",
            80: "K",
            81: "B",
            82: "I",
            85: "J",
            87: "L",
        }
        self.assertEqual(assignment, expected)

    def test_match_outcome_handles_regulation_extra_time_and_penalties(self):
        # regulation win by two -> team1 result 1, margin 2
        self.assertEqual(data.match_outcome({"ft": [2, 0]}), (1.0, 2, 0))
        # draw
        self.assertEqual(data.match_outcome({"ft": [1, 1]}), (0.5, 0, None))
        # decided in extra time -> use the ET score
        self.assertEqual(data.match_outcome({"ft": [2, 2], "et": [3, 2]}), (1.0, 1, 0))
        # penalty shootout -> counts as a draw for the rating, but team2 advances
        self.assertEqual(
            data.match_outcome({"ft": [1, 1], "et": [1, 1], "p": [3, 4]}),
            (0.5, 0, 1),
        )
        # unplayed
        self.assertIsNone(data.match_outcome({}))
        self.assertIsNone(data.match_outcome(None))

    def _current_seeding(self):
        winners = {
            "A": "Mexico", "B": "Switzerland", "C": "Brazil", "D": "United States",
            "E": "Germany", "F": "Netherlands", "G": "Belgium", "H": "Spain",
            "I": "France", "J": "Argentina", "K": "Colombia", "L": "England",
        }
        runners = {
            "A": "South Korea", "B": "Canada", "C": "Scotland", "D": "Australia",
            "E": "Ivory Coast", "F": "Sweden", "G": "Iran", "H": "Uruguay",
            "I": "Norway", "J": "Austria", "K": "Portugal", "L": "Croatia",
        }
        thirds_team = {
            "B": "Bosnia and Herzegovina", "D": "Paraguay", "E": "Ecuador",
            "F": "Tunisia", "I": "Senegal", "J": "Algeria", "K": "DR Congo",
            "L": "Ghana",
        }
        third_assignment = bracket.allocate_thirds(["B", "D", "E", "F", "I", "J", "K", "L"])
        return winners, runners, thirds_team, third_assignment

    def test_official_result_applied_by_participants(self):
        winners, runners, thirds_team, third_assignment = self._current_seeding()
        # Match 74 seeds Germany (winner E) vs Paraguay (third D). The official
        # result (Paraguay win) is keyed by the pair, not the slot number.
        fixed_winners = {frozenset(("Germany", "Paraguay")): "Paraguay"}
        parts, winner_of, loser_of = bracket.play_bracket_with_matches(
            winners, runners, thirds_team, third_assignment,
            lambda a, b: (a, b),                      # predictor: home always wins
            fixed_winners=fixed_winners,
        )
        self.assertEqual(parts[74], ("Germany", "Paraguay"))
        self.assertEqual(winner_of[74], "Paraguay")   # official result overrides
        self.assertEqual(loser_of[74], "Germany")
        # A pairing with no official result falls back to the predictor.
        self.assertEqual(parts[76], ("Brazil", "Sweden"))
        self.assertEqual(winner_of[76], "Brazil")

    def test_no_team_appears_in_two_round_of_32_slots(self):
        # The old slot-number override double-booked teams; the participant-based
        # application must keep all 32 Round-of-32 participants distinct.
        winners, runners, thirds_team, third_assignment = self._current_seeding()
        fixed_winners = {
            frozenset(("Germany", "Paraguay")): "Paraguay",
            frozenset(("Netherlands", "Scotland")): "Netherlands",
        }
        parts, _wo, _lo = bracket.play_bracket_with_matches(
            winners, runners, thirds_team, third_assignment,
            lambda a, b: (a, b),
            fixed_winners=fixed_winners,
        )
        r32_teams = [t for no in bracket.R32_NOS for t in parts[no]]
        self.assertEqual(len(r32_teams), 32)
        self.assertEqual(len(set(r32_teams)), 32)      # no duplicates


class RatingTests(unittest.TestCase):
    def test_live_update_is_zero_sum_and_rewards_the_winner(self):
        base = {"A": 1500.0, "B": 1500.0}
        played = [{"team1": "A", "team2": "B", "result_a": 1.0, "gd": 1,
                   "round": "Round of 16"}]
        r = ratings.live_ratings(played, base=base)
        self.assertGreater(r["A"], 1500.0)
        self.assertLess(r["B"], 1500.0)
        self.assertAlmostEqual(r["A"] + r["B"], 3000.0, places=6)
        # equal ratings, one-goal win in a K=50 round -> +/-25
        self.assertAlmostEqual(r["A"], 1525.0, places=6)

    def test_bigger_win_and_later_round_move_more_points(self):
        base = {"A": 1500.0, "B": 1500.0}
        blowout = ratings.live_ratings(
            [{"team1": "A", "team2": "B", "result_a": 1.0, "gd": 4,
              "round": "Final"}], base=base)
        narrow = ratings.live_ratings(
            [{"team1": "A", "team2": "B", "result_a": 1.0, "gd": 1,
              "round": "Round of 16"}], base=base)
        self.assertGreater(blowout["A"], narrow["A"])


if __name__ == "__main__":
    unittest.main()
