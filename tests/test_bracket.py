import unittest

import bracket


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

    def test_fixed_knockout_results_override_predictions(self):
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
        _, winner_of, loser_of = bracket.play_bracket_with_matches(
            winners,
            runners,
            thirds_team,
            third_assignment,
            lambda a, b: (a, b),
            fixed_results={74: ("Paraguay", "Germany"), 76: ("Morocco", "Netherlands")},
            fixed_matchups={74: ("Germany", "Paraguay"), 76: ("Morocco", "Netherlands")},
        )
        self.assertEqual(winner_of[74], "Paraguay")
        self.assertEqual(loser_of[74], "Germany")
        self.assertEqual(winner_of[76], "Morocco")
        self.assertEqual(loser_of[76], "Netherlands")


if __name__ == "__main__":
    unittest.main()
