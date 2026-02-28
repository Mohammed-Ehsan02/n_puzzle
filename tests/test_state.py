# ==========================================================================  #
#  test_state.py — Tests for PuzzleState class                                #
# ==========================================================================  #
#                                                                              #
#  What we test:                                                               #
#    - Board is stored as tuple of tuples (immutable)                          #
#    - Accepts both list and tuple input                                       #
#    - Blank position is found correctly                                       #
#    - g, h, f costs are computed correctly                                    #
#    - Neighbors are generated correctly (bounds, swap, g increment)           #
#    - Equality and hashing work (for sets/dicts)                              #
#    - Comparison works by f value (for heapq)                                 #
#    - is_goal works with both list and tuple goals                            #
# ==========================================================================  #

import pytest
from state import PuzzleState


# ================================================================== #
#  Construction and storage                                            #
# ================================================================== #

class TestConstruction:

    def test_list_input_stored_as_tuple(self):
        """List-of-lists input should be converted to tuple-of-tuples."""
        board = [[1, 2, 3], [4, 0, 5], [6, 7, 8]]
        ps = PuzzleState(board)
        assert isinstance(ps.board, tuple)
        assert all(isinstance(row, tuple) for row in ps.board)

    def test_tuple_input_stays_tuple(self):
        """Tuple-of-tuples input should be kept as-is."""
        board = ((1, 2, 3), (4, 0, 5), (6, 7, 8))
        ps = PuzzleState(board)
        assert ps.board == board

    def test_blank_found(self):
        """Blank position (0) must be detected correctly."""
        ps = PuzzleState([[1, 2, 3], [4, 5, 6], [7, 0, 8]])
        assert ps.blank_pos == (2, 1)

    def test_blank_at_corner(self):
        """Blank at top-left corner."""
        ps = PuzzleState([[0, 1, 2], [3, 4, 5], [6, 7, 8]])
        assert ps.blank_pos == (0, 0)

    def test_blank_at_bottom_right(self):
        """Blank at bottom-right corner."""
        ps = PuzzleState([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        assert ps.blank_pos == (2, 2)

    def test_size_detected(self):
        """Board size N should be auto-detected."""
        ps3 = PuzzleState([[1, 2, 3], [4, 0, 5], [6, 7, 8]])
        ps4 = PuzzleState([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]])
        assert ps3.n == 3
        assert ps4.n == 4


# ================================================================== #
#  Cost values                                                         #
# ================================================================== #

class TestCosts:

    def test_default_costs(self):
        """Default g=0, h=0, f=0."""
        ps = PuzzleState([[1, 0], [2, 3]])
        assert ps.g == 0
        assert ps.h == 0
        assert ps.f == 0

    def test_custom_costs(self):
        """g and h set explicitly, f = g + h."""
        ps = PuzzleState([[1, 0], [2, 3]], g=5, h=3)
        assert ps.g == 5
        assert ps.h == 3
        assert ps.f == 8

    def test_parent_stored(self):
        """Parent state should be stored for path reconstruction."""
        parent = PuzzleState([[1, 2, 3], [4, 0, 5], [6, 7, 8]])
        child = PuzzleState([[1, 0, 3], [4, 2, 5], [6, 7, 8]], parent=parent)
        assert child.parent is parent

    def test_no_parent_by_default(self):
        """Initial state has no parent."""
        ps = PuzzleState([[1, 0], [2, 3]])
        assert ps.parent is None


# ================================================================== #
#  Neighbor generation                                                 #
# ================================================================== #

class TestNeighbors:

    def test_center_blank_has_4_neighbors(self):
        """Blank in center of 3×3 → 4 possible moves."""
        ps = PuzzleState([[1, 2, 3], [8, 0, 4], [7, 6, 5]])
        neighbors = ps.get_neighbors()
        assert len(neighbors) == 4

    def test_corner_blank_has_2_neighbors(self):
        """Blank in corner → only 2 possible moves."""
        ps = PuzzleState([[0, 1, 2], [3, 4, 5], [6, 7, 8]])
        neighbors = ps.get_neighbors()
        assert len(neighbors) == 2

    def test_edge_blank_has_3_neighbors(self):
        """Blank on edge (not corner) → 3 possible moves."""
        ps = PuzzleState([[1, 0, 2], [3, 4, 5], [6, 7, 8]])
        neighbors = ps.get_neighbors()
        assert len(neighbors) == 3

    def test_neighbor_g_incremented(self):
        """Each neighbor should have g = parent.g + 1."""
        ps = PuzzleState([[1, 2, 3], [8, 0, 4], [7, 6, 5]], g=5)
        for neighbor in ps.get_neighbors():
            assert neighbor.g == 6

    def test_neighbor_parent_set(self):
        """Each neighbor's parent should point back to current state."""
        ps = PuzzleState([[1, 2, 3], [8, 0, 4], [7, 6, 5]])
        for neighbor in ps.get_neighbors():
            assert neighbor.parent is ps

    def test_neighbor_boards_are_valid(self):
        """Neighbors should have exactly one swap (blank ↔ adjacent)."""
        ps = PuzzleState([[1, 2, 3], [8, 0, 4], [7, 6, 5]])
        original_flat = sorted(val for row in ps.board for val in row)
        for neighbor in ps.get_neighbors():
            # Same numbers, just rearranged
            flat = sorted(val for row in neighbor.board for val in row)
            assert flat == original_flat
            # Exactly 2 positions differ (the swap)
            diffs = sum(
                1 for i in range(3) for j in range(3)
                if ps.board[i][j] != neighbor.board[i][j]
            )
            assert diffs == 2

    def test_neighbor_immutability(self):
        """Creating neighbors should not modify the original state."""
        board = [[1, 2, 3], [8, 0, 4], [7, 6, 5]]
        ps = PuzzleState(board)
        original_board = ps.board
        _ = ps.get_neighbors()
        assert ps.board == original_board


# ================================================================== #
#  Equality and hashing                                                #
# ================================================================== #

class TestEqualityHashing:

    def test_equal_same_board(self):
        """Two states with the same board are equal."""
        ps1 = PuzzleState([[1, 0], [2, 3]])
        ps2 = PuzzleState([[1, 0], [2, 3]])
        assert ps1 == ps2

    def test_not_equal_different_board(self):
        """Two states with different boards are not equal."""
        ps1 = PuzzleState([[1, 0], [2, 3]])
        ps2 = PuzzleState([[0, 1], [2, 3]])
        assert ps1 != ps2

    def test_equal_regardless_of_costs(self):
        """Equality depends only on board, not on g/h/f."""
        ps1 = PuzzleState([[1, 0], [2, 3]], g=0, h=0)
        ps2 = PuzzleState([[1, 0], [2, 3]], g=5, h=10)
        assert ps1 == ps2

    def test_same_hash_for_equal_states(self):
        """Equal states must have the same hash (set/dict requirement)."""
        ps1 = PuzzleState([[1, 0], [2, 3]])
        ps2 = PuzzleState(((1, 0), (2, 3)))
        assert hash(ps1) == hash(ps2)

    def test_set_membership(self):
        """Can find a state in a set via a different instance."""
        ps1 = PuzzleState([[1, 0], [2, 3]])
        ps2 = PuzzleState([[1, 0], [2, 3]])
        s = {ps1}
        assert ps2 in s

    def test_not_equal_to_non_state(self):
        """Comparing with a non-PuzzleState should return False."""
        ps = PuzzleState([[1, 0], [2, 3]])
        assert ps != "not a state"
        assert ps != 42
        assert ps != [[1, 0], [2, 3]]


# ================================================================== #
#  Comparison (for heapq)                                              #
# ================================================================== #

class TestComparison:

    def test_lt_by_f_value(self):
        """State with lower f should be 'less than'."""
        ps1 = PuzzleState([[1, 0], [2, 3]], g=1, h=2)  # f=3
        ps2 = PuzzleState([[0, 1], [2, 3]], g=2, h=5)  # f=7
        assert ps1 < ps2
        assert not ps2 < ps1

    def test_sorted_by_f(self):
        """Sorting a list of states should order by f value."""
        ps_a = PuzzleState([[1, 0], [2, 3]], g=5, h=5)   # f=10
        ps_b = PuzzleState([[0, 1], [2, 3]], g=1, h=1)   # f=2
        ps_c = PuzzleState([[1, 2], [0, 3]], g=3, h=3)   # f=6
        result = sorted([ps_a, ps_b, ps_c])
        assert result[0].f == 2
        assert result[1].f == 6
        assert result[2].f == 10


# ================================================================== #
#  Goal checking                                                       #
# ================================================================== #

class TestIsGoal:

    def test_is_goal_with_list(self):
        """is_goal should work with list-of-lists goal."""
        ps = PuzzleState([[1, 2, 3], [8, 0, 4], [7, 6, 5]])
        assert ps.is_goal([[1, 2, 3], [8, 0, 4], [7, 6, 5]]) is True

    def test_is_goal_with_tuple(self):
        """is_goal should work with tuple-of-tuples goal."""
        ps = PuzzleState([[1, 2, 3], [8, 0, 4], [7, 6, 5]])
        assert ps.is_goal(((1, 2, 3), (8, 0, 4), (7, 6, 5))) is True

    def test_not_goal(self):
        """Different board is not the goal."""
        ps = PuzzleState([[1, 0, 3], [8, 2, 4], [7, 6, 5]])
        assert ps.is_goal([[1, 2, 3], [8, 0, 4], [7, 6, 5]]) is False
