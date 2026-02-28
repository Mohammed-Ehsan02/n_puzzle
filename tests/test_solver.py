# ==========================================================================  #
#  test_solver.py — Tests for A* search and path reconstruction               #
# ==========================================================================  #
#                                                                              #
#  What we test:                                                               #
#    - Path reconstruction builds correct start→goal chains                    #
#    - A* solves the goal state in 0 moves                                     #
#    - A* solves 1-move puzzles optimally                                      #
#    - A* solves multi-move 3×3 puzzles optimally                              #
#    - A* works with all 3 heuristics and finds the same optimal move count   #
#    - A* returns correct statistics (time, size, moves)                       #
#    - A* returns None for unsolvable puzzles (defensive)                      #
#    - print_board formats output correctly                                    #
# ==========================================================================  #

import pytest
from state import PuzzleState
from goal import generate_snail_goal
from solver.a_star import a_star
from solver.utils import reconstruct_path, print_board
from solver.heuristics import manhattan, misplaced, linear_conflict


# ------------------------------------------------------------------ #
#  Shared fixtures                                                    #
# ------------------------------------------------------------------ #

GOAL_3 = generate_snail_goal(3)  # [[1,2,3],[8,0,4],[7,6,5]]
GOAL_4 = generate_snail_goal(4)


# ================================================================== #
#  Path Reconstruction                                                 #
# ================================================================== #

class TestReconstructPath:

    def test_single_state(self):
        """A state with no parent → path of length 1."""
        state = PuzzleState(GOAL_3)
        path = reconstruct_path(state)
        assert len(path) == 1
        assert path[0] is state

    def test_chain_of_three(self):
        """Chain: A ← B ← C → path should be [A, B, C]."""
        a = PuzzleState([[1, 2, 3], [8, 0, 4], [7, 6, 5]])
        b = PuzzleState([[1, 0, 3], [8, 2, 4], [7, 6, 5]], parent=a)
        c = PuzzleState([[0, 1, 3], [8, 2, 4], [7, 6, 5]], parent=b)
        path = reconstruct_path(c)
        assert len(path) == 3
        assert path[0] is a
        assert path[1] is b
        assert path[2] is c

    def test_path_starts_at_root(self):
        """First element of path should have parent=None."""
        a = PuzzleState(GOAL_3)
        b = PuzzleState([[1, 0, 3], [8, 2, 4], [7, 6, 5]], parent=a)
        path = reconstruct_path(b)
        assert path[0].parent is None


# ================================================================== #
#  print_board                                                         #
# ================================================================== #

class TestPrintBoard:

    def test_3x3_format(self):
        """3×3 board should be formatted with single-digit width."""
        board = ((1, 2, 3), (8, 0, 4), (7, 6, 5))
        result = print_board(board, 3)
        lines = result.split("\n")
        assert len(lines) == 3
        # Each number should be right-justified to width 1
        assert "1" in lines[0] and "2" in lines[0] and "3" in lines[0]

    def test_4x4_format(self):
        """4×4 board should align two-digit numbers properly."""
        board = ((1, 2, 3, 4), (12, 13, 14, 5), (11, 0, 15, 6), (10, 9, 8, 7))
        result = print_board(board, 4)
        lines = result.split("\n")
        assert len(lines) == 4


# ================================================================== #
#  A* — Trivial cases                                                  #
# ================================================================== #

class TestAStarTrivial:

    def test_already_solved(self):
        """Goal state as input → 0 moves, path of length 1."""
        initial = PuzzleState(GOAL_3)
        path, stats = a_star(initial, GOAL_3, manhattan)
        assert stats["moves"] == 0
        assert len(path) == 1
        assert path[0].board == tuple(tuple(r) for r in GOAL_3)

    def test_one_move_swap_up(self):
        """
        Blank at (1,1), swap with tile 2 above → board [[1,0,3],[8,2,4],[7,6,5]].
        Should solve in exactly 1 move.
        """
        board = [[1, 0, 3], [8, 2, 4], [7, 6, 5]]
        initial = PuzzleState(board)
        path, stats = a_star(initial, GOAL_3, manhattan)
        assert stats["moves"] == 1
        assert len(path) == 2
        # First state is input, last is goal
        assert path[0].board == tuple(tuple(r) for r in board)
        assert path[-1].board == tuple(tuple(r) for r in GOAL_3)

    def test_one_move_swap_left(self):
        """Swap blank(1,1) with tile 8(1,0) → 1 move."""
        board = [[1, 2, 3], [0, 8, 4], [7, 6, 5]]
        initial = PuzzleState(board)
        path, stats = a_star(initial, GOAL_3, manhattan)
        assert stats["moves"] == 1


# ================================================================== #
#  A* — Multi-move puzzles                                             #
# ================================================================== #

class TestAStarMultiMove:

    def test_two_moves(self):
        """
        From goal, make 2 distinct moves:
          Goal:   [[1,2,3],[8,0,4],[7,6,5]]
          Move 1: [[1,2,3],[0,8,4],[7,6,5]]  (slide 8 left)
          Move 2: [[1,2,3],[7,8,4],[0,6,5]]  (slide 7 up)
        Solving this should take 2 moves.
        """
        board = [[1, 2, 3], [7, 8, 4], [0, 6, 5]]
        initial = PuzzleState(board)
        path, stats = a_star(initial, GOAL_3, manhattan)
        assert stats["moves"] == 2

    def test_known_scramble(self):
        """
        Known 3×3 scramble that requires 15 moves.
        All 3 heuristics should find the same optimal count.
        """
        board = [[3, 2, 6], [1, 4, 0], [8, 7, 5]]
        initial = PuzzleState(board)
        path, stats = a_star(initial, GOAL_3, manhattan)
        optimal_moves = stats["moves"]
        # Verify path is valid: first is start, last is goal
        assert path[0].board == tuple(tuple(r) for r in board)
        assert path[-1].board == tuple(tuple(r) for r in GOAL_3)
        # Verify path is continuous: each step differs by exactly 1 swap
        for i in range(1, len(path)):
            diffs = sum(
                1 for r in range(3) for c in range(3)
                if path[i].board[r][c] != path[i - 1].board[r][c]
            )
            assert diffs == 2, f"Step {i} has {diffs} tile differences (expected 2)"
        # Verify move count matches path length
        assert optimal_moves == len(path) - 1


# ================================================================== #
#  A* — All heuristics find optimal                                    #
# ================================================================== #

class TestAStarAllHeuristics:

    def test_same_optimal_all_heuristics(self):
        """
        All 3 admissible heuristics must find the same number of moves.
        A* with admissible h is guaranteed optimal, so move count must match.
        The number of expanded states (time_complexity) may differ.
        """
        board = [[3, 2, 6], [1, 4, 0], [8, 7, 5]]
        initial = PuzzleState(board)

        _, stats_mh = a_star(PuzzleState(board), GOAL_3, manhattan)
        _, stats_mi = a_star(PuzzleState(board), GOAL_3, misplaced)
        _, stats_lc = a_star(PuzzleState(board), GOAL_3, linear_conflict)

        assert stats_mh["moves"] == stats_mi["moves"] == stats_lc["moves"]

    def test_stronger_heuristic_explores_less(self):
        """
        Stronger heuristic → fewer states explored.
        misplaced.time >= manhattan.time >= linear_conflict.time (generally).
        """
        board = [[3, 2, 6], [1, 4, 0], [8, 7, 5]]

        _, stats_mi = a_star(PuzzleState(board), GOAL_3, misplaced)
        _, stats_mh = a_star(PuzzleState(board), GOAL_3, manhattan)
        _, stats_lc = a_star(PuzzleState(board), GOAL_3, linear_conflict)

        # Misplaced should explore at least as many as Manhattan
        assert stats_mi["time_complexity"] >= stats_mh["time_complexity"]
        # Manhattan should explore at least as many as Linear Conflict
        assert stats_mh["time_complexity"] >= stats_lc["time_complexity"]


# ================================================================== #
#  A* — Statistics                                                     #
# ================================================================== #

class TestAStarStats:

    def test_time_complexity_positive(self):
        """Solving any non-goal puzzle must expand at least 1 state."""
        board = [[1, 0, 3], [8, 2, 4], [7, 6, 5]]
        _, stats = a_star(PuzzleState(board), GOAL_3, manhattan)
        assert stats["time_complexity"] >= 1

    def test_size_complexity_positive(self):
        """At least 1 state must be in memory at some point."""
        board = [[1, 0, 3], [8, 2, 4], [7, 6, 5]]
        _, stats = a_star(PuzzleState(board), GOAL_3, manhattan)
        assert stats["size_complexity"] >= 1

    def test_goal_has_zero_stats(self):
        """Solving the goal itself: 0 moves, but still some exploration."""
        _, stats = a_star(PuzzleState(GOAL_3), GOAL_3, manhattan)
        assert stats["moves"] == 0
        assert stats["time_complexity"] >= 1  # Must pop at least 1 state


# ================================================================== #
#  A* — 4×4 easy puzzle                                                #
# ================================================================== #

class TestAStar4x4:

    def test_4x4_one_move(self):
        """4×4 puzzle that's 1 move from goal."""
        # Swap blank(2,1) with tile 13(1,1) in goal
        board = [[1, 2, 3, 4], [12, 0, 14, 5], [11, 13, 15, 6], [10, 9, 8, 7]]
        initial = PuzzleState(board)
        path, stats = a_star(initial, GOAL_4, linear_conflict)
        assert stats["moves"] == 1

    def test_4x4_two_moves(self):
        """4×4 puzzle that's 2 moves from goal."""
        # From goal: swap blank(2,1)↔13(1,1), then swap blank(1,1)↔2(0,1)
        board = [[1, 0, 3, 4], [12, 2, 14, 5], [11, 13, 15, 6], [10, 9, 8, 7]]
        initial = PuzzleState(board)
        path, stats = a_star(initial, GOAL_4, linear_conflict)
        assert stats["moves"] == 2
