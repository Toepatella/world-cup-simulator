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


if __name__ == "__main__":
    unittest.main()
