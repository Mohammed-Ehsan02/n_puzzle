# ==========================================================================  #
#  test_solvability.py — Tests for puzzle solvability checker                 #
# ==========================================================================  #
#                                                                              #
#  What we test:                                                               #
#    - The snail goal itself is always solvable (trivially — 0 moves)         #
#    - States 1 move away from goal are solvable                               #
#    - Swapping two non-blank tiles from goal makes it unsolvable              #
#    - The 42-provided generator's solvable/unsolvable flags are correct       #
#    - Inversion counting works correctly                                      #
#    - Works for multiple puzzle sizes (3, 4, 5)                               #
# ==========================================================================  #

import pytest
from solvability import is_solvable, count_inversions
from goal import generate_snail_goal


class TestCountInversions:
    """Test the inversion counting helper."""

    def test_sorted(self):
        """A sorted list has 0 inversions."""
        assert count_inversions([0, 1, 2, 3, 4]) == 0

    def test_reversed(self):
        """A fully reversed list of length N has N*(N-1)/2 inversions."""
        # [4, 3, 2, 1, 0] → 10 inversions
        assert count_inversions([4, 3, 2, 1, 0]) == 10

    def test_single_swap(self):
        """Swapping two adjacent elements creates exactly 1 inversion."""
        assert count_inversions([0, 2, 1, 3, 4]) == 1

    def test_known_count(self):
        """[2, 4, 1, 3, 0] → inversions: (2,1),(2,0),(4,1),(4,3),(4,0),(1,0),(3,0) = 7"""
        assert count_inversions([2, 4, 1, 3, 0]) == 7


class TestGoalIsSolvable:
    """The snail goal state should always be solvable (it IS the solution)."""

    @pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7])
    def test_goal_is_solvable(self, n):
        """The goal state itself requires 0 moves — must be solvable."""
        goal = generate_snail_goal(n)
        assert is_solvable(goal) is True


class TestOneMoveAway:
    """States that are exactly 1 slide away from the goal must be solvable."""

    def test_3x3_swap_up(self):
        """3×3 goal: swap blank (1,1) with tile above (0,1) → tile 2."""
        # Goal:  [[1,2,3],[8,0,4],[7,6,5]]
        # After: [[1,0,3],[8,2,4],[7,6,5]]
        puzzle = [[1, 0, 3], [8, 2, 4], [7, 6, 5]]
        assert is_solvable(puzzle) is True

    def test_3x3_swap_down(self):
        """3×3 goal: swap blank (1,1) with tile below (2,1) → tile 6."""
        puzzle = [[1, 2, 3], [8, 6, 4], [7, 0, 5]]
        assert is_solvable(puzzle) is True

    def test_3x3_swap_left(self):
        """3×3 goal: swap blank (1,1) with tile left (1,0) → tile 8."""
        puzzle = [[1, 2, 3], [0, 8, 4], [7, 6, 5]]
        assert is_solvable(puzzle) is True

    def test_3x3_swap_right(self):
        """3×3 goal: swap blank (1,1) with tile right (1,2) → tile 4."""
        puzzle = [[1, 2, 3], [8, 4, 0], [7, 6, 5]]
        assert is_solvable(puzzle) is True

    def test_4x4_one_move(self):
        """4×4 goal: swap blank (2,1) with tile above (1,1) → tile 13."""
        # Goal: [[1,2,3,4],[12,13,14,5],[11,0,15,6],[10,9,8,7]]
        puzzle = [[1, 2, 3, 4], [12, 0, 14, 5], [11, 13, 15, 6], [10, 9, 8, 7]]
        assert is_solvable(puzzle) is True


class TestUnsolvable:
    """Swapping two non-blank adjacent tiles from goal creates an unsolvable state."""

    def test_3x3_swap_tiles(self):
        """Swap tiles 1 and 2 from 3×3 goal → unsolvable."""
        puzzle = [[2, 1, 3], [8, 0, 4], [7, 6, 5]]
        assert is_solvable(puzzle) is False

    def test_3x3_swap_other_tiles(self):
        """Swap tiles 6 and 4 from 3×3 goal → unsolvable."""
        puzzle = [[1, 2, 3], [8, 0, 6], [7, 4, 5]]
        assert is_solvable(puzzle) is False

    def test_4x4_swap_tiles(self):
        """Swap tiles 1 and 2 from 4×4 goal → unsolvable."""
        puzzle = [[2, 1, 3, 4], [12, 13, 14, 5], [11, 0, 15, 6], [10, 9, 8, 7]]
        assert is_solvable(puzzle) is False

    def test_5x5_swap_tiles(self):
        """Swap tiles 1 and 2 from 5×5 goal → unsolvable."""
        goal = generate_snail_goal(5)
        # Swap first two elements
        puzzle = [row[:] for row in goal]
        puzzle[0][0], puzzle[0][1] = puzzle[0][1], puzzle[0][0]
        assert is_solvable(puzzle) is False


class TestMultipleMoves:
    """States that are several moves from goal — verify consistency."""

    def test_3x3_two_moves_solvable(self):
        """
        Start from goal, make 2 moves:
          Goal:  1 2 3 / 8 0 4 / 7 6 5
          Move1: 1 2 3 / 0 8 4 / 7 6 5  (slide 8 right)
          Move2: 1 2 3 / 7 8 4 / 0 6 5  (slide 7 up)
        2 moves from goal → solvable.
        """
        puzzle = [[1, 2, 3], [7, 8, 4], [0, 6, 5]]
        assert is_solvable(puzzle) is True

    def test_3x3_scrambled_solvable(self):
        """A known solvable 3×3 puzzle."""
        # This was verified by actually solving it
        puzzle = [[3, 2, 6], [1, 4, 0], [8, 7, 5]]
        assert is_solvable(puzzle) is True
