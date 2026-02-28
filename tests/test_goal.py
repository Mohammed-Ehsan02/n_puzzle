# ==========================================================================  #
#  test_goal.py — Tests for snail goal generation                             #
# ==========================================================================  #
#                                                                              #
#  What we test:                                                               #
#    - Known snail patterns for 3×3, 4×4, 5×5 match the subject examples      #
#    - Output is always N×N with correct dimensions                            #
#    - Contains every number from 0 to N²-1 exactly once                       #
#    - The blank (0) is always at the spiral's end (not a corner/edge)         #
#    - Works for edge case sizes (2×2)                                         #
# ==========================================================================  #

import pytest
from goal import generate_snail_goal


class TestSnailGoalKnown:
    """Test against the exact examples from the subject PDF."""

    def test_3x3(self):
        """3×3 snail from subject: 1 2 3 / 8 0 4 / 7 6 5"""
        expected = [
            [1, 2, 3],
            [8, 0, 4],
            [7, 6, 5],
        ]
        assert generate_snail_goal(3) == expected

    def test_4x4(self):
        """4×4 snail from subject: 1 2 3 4 / 12 13 14 5 / 11 0 15 6 / 10 9 8 7"""
        expected = [
            [1,  2,  3,  4],
            [12, 13, 14, 5],
            [11, 0,  15, 6],
            [10, 9,  8,  7],
        ]
        assert generate_snail_goal(4) == expected

    def test_5x5(self):
        """5×5 snail from subject."""
        expected = [
            [1,  2,  3,  4,  5],
            [16, 17, 18, 19, 6],
            [15, 24, 0,  20, 7],
            [14, 23, 22, 21, 8],
            [13, 12, 11, 10, 9],
        ]
        assert generate_snail_goal(5) == expected


class TestSnailGoalProperties:
    """Test structural properties that must hold for any valid snail goal."""

    @pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7, 10])
    def test_dimensions(self, n):
        """Goal must be an N×N grid."""
        goal = generate_snail_goal(n)
        assert len(goal) == n
        for row in goal:
            assert len(row) == n

    @pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7, 10])
    def test_contains_all_numbers(self, n):
        """Goal must contain every number from 0 to N²-1 exactly once."""
        goal = generate_snail_goal(n)
        flat = [val for row in goal for val in row]
        assert sorted(flat) == list(range(n * n))

    @pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7, 10])
    def test_blank_not_in_corner(self, n):
        """The blank (0) should not be in a corner for N >= 3."""
        if n < 3:
            return  # 2×2 is a special case
        goal = generate_snail_goal(n)
        corners = [
            goal[0][0], goal[0][n - 1],
            goal[n - 1][0], goal[n - 1][n - 1],
        ]
        assert 0 not in corners

    @pytest.mark.parametrize("n", [3, 4, 5, 6, 7])
    def test_first_row_starts_with_1_to_n(self, n):
        """First row of snail is always [1, 2, 3, ..., N]."""
        goal = generate_snail_goal(n)
        assert goal[0] == list(range(1, n + 1))

    def test_2x2(self):
        """Edge case: 2×2 snail should be [1,2] / [0,3]."""
        expected = [
            [1, 2],
            [0, 3],
        ]
        assert generate_snail_goal(2) == expected
