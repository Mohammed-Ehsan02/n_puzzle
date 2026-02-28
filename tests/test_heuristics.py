# ==========================================================================  #
#  test_heuristics.py — Tests for heuristic functions                         #
# ==========================================================================  #
#                                                                              #
#  What we test:                                                               #
#    - Goal state always returns 0 for all heuristics                          #
#    - One-move-away states return correct small values                        #
#    - Hand-calculated values for known boards                                 #
#    - Admissibility: h(x) <= actual cost (for states we know the answer)     #
#    - Ordering: misplaced <= manhattan <= linear_conflict (for same input)    #
#    - Works for different board sizes (3×3, 4×4)                              #
# ==========================================================================  #

import pytest
from solver.heuristics import manhattan, misplaced, linear_conflict, _build_goal_map
from goal import generate_snail_goal


# ------------------------------------------------------------------ #
#  Fixtures: reusable goals and boards                                #
# ------------------------------------------------------------------ #

# 3×3 snail goal: [[1,2,3],[8,0,4],[7,6,5]]
GOAL_3 = generate_snail_goal(3)

# 4×4 snail goal: [[1,2,3,4],[12,13,14,5],[11,0,15,6],[10,9,8,7]]
GOAL_4 = generate_snail_goal(4)


# ================================================================== #
#  _build_goal_map helper                                              #
# ================================================================== #

class TestGoalMap:

    def test_3x3_map(self):
        """Goal map for 3×3 should map every tile to its (row, col)."""
        gm = _build_goal_map(GOAL_3)
        assert gm[1] == (0, 0)
        assert gm[2] == (0, 1)
        assert gm[3] == (0, 2)
        assert gm[8] == (1, 0)
        assert gm[0] == (1, 1)
        assert gm[4] == (1, 2)
        assert gm[7] == (2, 0)
        assert gm[6] == (2, 1)
        assert gm[5] == (2, 2)

    def test_map_has_all_tiles(self):
        """Map should contain entries for 0 through N²-1."""
        gm = _build_goal_map(GOAL_4)
        assert set(gm.keys()) == set(range(16))


# ================================================================== #
#  Manhattan Distance                                                  #
# ================================================================== #

class TestManhattan:

    def test_goal_is_zero(self):
        """Goal state → 0 distance."""
        assert manhattan(GOAL_3, GOAL_3) == 0
        assert manhattan(GOAL_4, GOAL_4) == 0

    def test_one_move_away(self):
        """
        Swap blank with tile 2 in 3×3 goal.
        Goal:  [[1,2,3],[8,0,4],[7,6,5]]  → blank at (1,1)
        Board: [[1,0,3],[8,2,4],[7,6,5]]  → tile 2 moved from (0,1) to (1,1)

        Only tile 2 is displaced: was at (0,1), now at (1,1), goal is (0,1).
        Manhattan for tile 2 = |1-0| + |1-1| = 1.
        All other tiles are in place → total = 1.
        """
        board = [[1, 0, 3], [8, 2, 4], [7, 6, 5]]
        assert manhattan(board, GOAL_3) == 1

    def test_hand_calculated_3x3(self):
        """
        Board: [[3, 2, 1],
                [8, 0, 4],
                [7, 6, 5]]
        Goal:  [[1, 2, 3],
                [8, 0, 4],
                [7, 6, 5]]

        Tile 3: at (0,0), goal (0,2) → |0-0|+|0-2| = 2
        Tile 2: at (0,1), goal (0,1) → 0
        Tile 1: at (0,2), goal (0,0) → |0-0|+|2-0| = 2
        All others in place → total = 4
        """
        board = [[3, 2, 1], [8, 0, 4], [7, 6, 5]]
        assert manhattan(board, GOAL_3) == 4

    def test_all_tiles_displaced_3x3(self):
        """
        Board: [[5, 6, 7],
                [4, 0, 8],
                [3, 2, 1]]
        Goal:  [[1, 2, 3],
                [8, 0, 4],
                [7, 6, 5]]

        Hand calculate each tile:
        Tile 5: (0,0) → goal (2,2): |0-2|+|0-2| = 4
        Tile 6: (0,1) → goal (2,1): |0-2|+|1-1| = 2
        Tile 7: (0,2) → goal (2,0): |0-2|+|2-0| = 4
        Tile 4: (1,0) → goal (1,2): |1-1|+|0-2| = 2
        Tile 8: (1,2) → goal (1,0): |1-1|+|2-0| = 2
        Tile 3: (2,0) → goal (0,2): |2-0|+|0-2| = 4
        Tile 2: (2,1) → goal (0,1): |2-0|+|1-1| = 2
        Tile 1: (2,2) → goal (0,0): |2-0|+|2-0| = 4
        Total = 4+2+4+2+2+4+2+4 = 24
        """
        board = [[5, 6, 7], [4, 0, 8], [3, 2, 1]]
        assert manhattan(board, GOAL_3) == 24

    def test_4x4_goal(self):
        """4×4 goal → 0."""
        assert manhattan(GOAL_4, GOAL_4) == 0

    def test_always_non_negative(self):
        """Manhattan distance is always >= 0."""
        board = [[3, 2, 6], [1, 4, 0], [8, 7, 5]]
        assert manhattan(board, GOAL_3) >= 0


# ================================================================== #
#  Misplaced Tiles                                                     #
# ================================================================== #

class TestMisplaced:

    def test_goal_is_zero(self):
        """Goal state → 0 misplaced."""
        assert misplaced(GOAL_3, GOAL_3) == 0
        assert misplaced(GOAL_4, GOAL_4) == 0

    def test_one_move_away(self):
        """
        Swap blank with tile 2:
        Board: [[1,0,3],[8,2,4],[7,6,5]]
        Only tile 2 is out of place → 1.
        (blank doesn't count)
        """
        board = [[1, 0, 3], [8, 2, 4], [7, 6, 5]]
        assert misplaced(board, GOAL_3) == 1

    def test_two_tiles_swapped(self):
        """
        Board: [[2, 1, 3],[8,0,4],[7,6,5]]
        Tiles 1 and 2 swapped → 2 misplaced.
        """
        board = [[2, 1, 3], [8, 0, 4], [7, 6, 5]]
        assert misplaced(board, GOAL_3) == 2

    def test_all_wrong(self):
        """
        Board: [[5, 6, 7],[4, 0, 8],[3, 2, 1]]
        Every non-blank tile is in the wrong place → 8 misplaced.
        """
        board = [[5, 6, 7], [4, 0, 8], [3, 2, 1]]
        assert misplaced(board, GOAL_3) == 8

    def test_blank_not_counted(self):
        """
        Even if blank is in wrong position, it's not counted.
        Board: [[0, 2, 3],[8,1,4],[7,6,5]] — blank at (0,0) not (1,1)
        Tile 1 at (1,1) not (0,0) → misplaced.
        Blank at (0,0) → NOT counted.
        Total: 1 (only tile 1).
        """
        board = [[0, 2, 3], [8, 1, 4], [7, 6, 5]]
        assert misplaced(board, GOAL_3) == 1


# ================================================================== #
#  Linear Conflict                                                     #
# ================================================================== #

class TestLinearConflict:

    def test_goal_is_zero(self):
        """Goal state → 0."""
        assert linear_conflict(GOAL_3, GOAL_3) == 0
        assert linear_conflict(GOAL_4, GOAL_4) == 0

    def test_no_conflict_just_manhattan(self):
        """
        Board: [[1, 0, 3],[8, 2, 4],[7, 6, 5]]
        Tile 2 is displaced but there's no linear conflict
        (no two tiles in the same row/col are both in their goal
         row/col in wrong order).
        So linear_conflict == manhattan == 1.
        """
        board = [[1, 0, 3], [8, 2, 4], [7, 6, 5]]
        assert linear_conflict(board, GOAL_3) == manhattan(board, GOAL_3)

    def test_one_row_conflict(self):
        """
        Goal row 0: [1, 2, 3]
        Board:      [[2, 1, 3],[8, 0, 4],[7, 6, 5]]

        Tile 2 at col 0, goal col 1.
        Tile 1 at col 1, goal col 0.
        Both are in their goal ROW (row 0).
        Tile 2 is left of tile 1, but tile 2's goal col (1) > tile 1's goal col (0).
        → 1 conflict → +2 to Manhattan.

        Manhattan: tile 1 = |0-0|+|1-0| = 1, tile 2 = |0-0|+|0-1| = 1 → total 2
        Linear conflict: 2 + 2 = 4
        """
        board = [[2, 1, 3], [8, 0, 4], [7, 6, 5]]
        m = manhattan(board, GOAL_3)
        lc = linear_conflict(board, GOAL_3)
        assert m == 2
        assert lc == m + 2  # One conflict adds 2

    def test_column_conflict(self):
        """
        Goal col 0: [1, 8, 7] (from snail: row0=1, row1=8, row2=7)
        Board: [[8, 2, 3],
                [1, 0, 4],
                [7, 6, 5]]

        Tile 8: at (0,0), goal is (1,0). Goal col = 0 ✓, in col 0 ✓
        Tile 1: at (1,0), goal is (0,0). Goal col = 0 ✓, in col 0 ✓
        Tile 7: at (2,0), goal is (2,0). Already in place.

        Tile 8 is above tile 1. Tile 8's goal row (1) > tile 1's goal row (0).
        → 1 column conflict → +2.

        Manhattan: tile 8 = |0-1|+|0-0| = 1, tile 1 = |1-0|+|0-0| = 1 → 2
        Linear conflict: 2 + 2 = 4
        """
        board = [[8, 2, 3], [1, 0, 4], [7, 6, 5]]
        m = manhattan(board, GOAL_3)
        lc = linear_conflict(board, GOAL_3)
        assert m == 2
        assert lc == m + 2


# ================================================================== #
#  Admissibility: h(x) must NEVER overestimate                         #
# ================================================================== #

class TestAdmissibility:

    def test_one_move_away_all_le_1(self):
        """
        For states exactly 1 move from goal, all heuristics must return <= 1.
        (They can't overestimate — the actual cost IS 1.)
        """
        boards = [
            [[1, 0, 3], [8, 2, 4], [7, 6, 5]],  # swap blank ↔ 2
            [[1, 2, 3], [8, 6, 4], [7, 0, 5]],  # swap blank ↔ 6
            [[1, 2, 3], [0, 8, 4], [7, 6, 5]],  # swap blank ↔ 8
            [[1, 2, 3], [8, 4, 0], [7, 6, 5]],  # swap blank ↔ 4
        ]
        for board in boards:
            assert misplaced(board, GOAL_3) <= 1
            assert manhattan(board, GOAL_3) <= 1
            assert linear_conflict(board, GOAL_3) <= 1


# ================================================================== #
#  Ordering: misplaced <= manhattan <= linear_conflict                  #
# ================================================================== #

class TestOrdering:

    def test_ordering_various_boards(self):
        """
        Misplaced is the weakest heuristic, Manhattan is stronger,
        Linear Conflict is the strongest. For any board:
          misplaced(board) <= manhattan(board) <= linear_conflict(board)
        """
        boards = [
            GOAL_3,
            [[1, 0, 3], [8, 2, 4], [7, 6, 5]],
            [[2, 1, 3], [8, 0, 4], [7, 6, 5]],
            [[3, 2, 1], [8, 0, 4], [7, 6, 5]],
            [[5, 6, 7], [4, 0, 8], [3, 2, 1]],
            [[3, 2, 6], [1, 4, 0], [8, 7, 5]],
        ]
        for board in boards:
            m = misplaced(board, GOAL_3)
            mh = manhattan(board, GOAL_3)
            lc = linear_conflict(board, GOAL_3)
            assert m <= mh, f"misplaced ({m}) > manhattan ({mh}) for {board}"
            assert mh <= lc, f"manhattan ({mh}) > linear_conflict ({lc}) for {board}"
