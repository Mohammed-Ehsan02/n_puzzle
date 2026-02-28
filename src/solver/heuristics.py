# ==========================================================================  #
#  heuristics.py — Heuristic Functions for A*                                 #
# ==========================================================================  #
#                                                                              #
#  A heuristic estimates the remaining cost from a state to the goal.          #
#  For A* to find the OPTIMAL solution, heuristics must be ADMISSIBLE:         #
#    → They must NEVER overestimate the true cost.                             #
#    → Underestimating or being exact is fine.                                 #
#                                                                              #
#  We implement 3 heuristics (subject requires at least 3):                    #
#                                                                              #
#  1. Manhattan Distance (mandatory):                                          #
#     For each tile, sum |current_row - goal_row| + |current_col - goal_col|.  #
#     Admissible because each tile needs at least that many moves.             #
#                                                                              #
#  2. Misplaced Tiles (Hamming Distance):                                      #
#     Count tiles not in their goal position. Admissible because each          #
#     misplaced tile needs at least 1 move. Weaker than Manhattan.             #
#                                                                              #
#  3. Linear Conflict:                                                         #
#     Manhattan + 2 for each pair of tiles in the same row/column that         #
#     are both in their goal row/column but in wrong order relative to         #
#     each other. Each such conflict needs at least 2 extra moves.             #
#     Stronger than Manhattan, still admissible.                               #
#                                                                              #
#  SHARED HELPER:                                                              #
#    _build_goal_map(goal) creates a dict: tile_value → (row, col).            #
#    All three heuristics need to know where each tile belongs.                #
#    We build this map once and pass it around.                                #
#                                                                              #
#  WHY ADMISSIBILITY MATTERS:                                                  #
#    If h(x) overestimates, A* might skip the optimal path because it          #
#    thinks it's too expensive. Admissible h guarantees A* finds the           #
#    shortest solution. All three of our heuristics are proven admissible:     #
#      - Misplaced: each wrong tile needs >= 1 move (trivially true)          #
#      - Manhattan: each tile needs >= its taxicab distance (no shortcuts)    #
#      - Linear conflict: Manhattan + provably necessary extra moves           #
# ==========================================================================  #


def _build_goal_map(goal) -> dict:
    """
    Build a lookup: tile_value → (goal_row, goal_col).

    This tells us where every tile SHOULD be in the solved state.
    We build this once and reuse it across heuristic calls.

    Example for 3×3 snail goal [[1,2,3],[8,0,4],[7,6,5]]:
      {1: (0,0), 2: (0,1), 3: (0,2), 8: (1,0), 0: (1,1),
       4: (1,2), 7: (2,0), 6: (2,1), 5: (2,2)}

    Args:
        goal: The goal board (list of lists or tuple of tuples).

    Returns:
        Dict mapping tile value to its (row, col) in the goal.
    """
    goal_map = {}
    n = len(goal)
    for r in range(n):
        for c in range(n):
            goal_map[goal[r][c]] = (r, c)
    return goal_map


# ================================================================== #
#  1. Manhattan Distance (mandatory)                                   #
# ================================================================== #

def manhattan(board, goal) -> int:
    """
    Manhattan distance heuristic.

    For each non-blank tile, compute the taxicab distance between its
    current position and its goal position. Sum all distances.

    Example:
      If tile 5 is at (0, 2) but belongs at (2, 2):
        distance = |0-2| + |2-2| = 2

    Why admissible:
      Each tile must move at least this many steps to reach its goal.
      Tiles can't teleport — they must slide one cell at a time.
      The actual cost is >= this because other tiles get in the way.

    Args:
        board: Current board (tuple of tuples or list of lists).
        goal:  Goal board (same format).

    Returns:
        Total Manhattan distance (int). 0 means board == goal.
    """
    goal_map = _build_goal_map(goal)
    n = len(board)
    distance = 0

    for r in range(n):
        for c in range(n):
            tile = board[r][c]
            if tile == 0:
                continue  # Skip the blank tile
            goal_r, goal_c = goal_map[tile]
            distance += abs(r - goal_r) + abs(c - goal_c)

    return distance


# ================================================================== #
#  2. Misplaced Tiles (Hamming Distance)                               #
# ================================================================== #

def misplaced(board, goal) -> int:
    """
    Misplaced tiles (Hamming distance) heuristic.

    Count the number of tiles that are NOT in their goal position.
    The blank tile (0) is excluded from the count.

    Example:
      board: [[1,0,3],[8,2,4],[7,6,5]]   (tile 2 is at (1,1) not (0,1))
      goal:  [[1,2,3],[8,0,4],[7,6,5]]
      Only tile 2 is misplaced → returns 1.
      (The blank moved too, but we don't count it.)

    Why admissible:
      Each misplaced tile needs AT LEAST 1 move to get to its goal.
      So counting them gives a lower bound on total moves.
      This is weaker than Manhattan (less informed), so A* explores more.

    Args:
        board: Current board.
        goal:  Goal board.

    Returns:
        Number of misplaced non-blank tiles (int). 0 means board == goal.
    """
    n = len(board)
    count = 0

    for r in range(n):
        for c in range(n):
            tile = board[r][c]
            if tile == 0:
                continue  # Skip the blank tile
            if tile != goal[r][c]:
                count += 1

    return count


# ================================================================== #
#  3. Linear Conflict                                                  #
# ================================================================== #

def linear_conflict(board, goal) -> int:
    """
    Linear conflict heuristic.

    Start with Manhattan distance, then add 2 for every "linear conflict".

    A linear conflict occurs when:
      - Two tiles are in the SAME ROW as their goal positions, AND
      - They are in the WRONG ORDER relative to each other in that row.
      (Same logic applies for columns.)

    Each such conflict needs at least 2 extra moves to resolve:
      one tile must leave the row, the other passes, then it comes back.

    Example:
      Row has [3, 1, 2] but goal row is [1, 2, 3].
      Tile 3 is at col 0, belongs at col 2.
      Tile 1 is at col 1, belongs at col 0.
      3 is left of 1 in current, but 3 should be RIGHT of 1 in goal.
      → That's 1 conflict → add 2 to Manhattan.

    Why admissible:
      Manhattan distance is admissible. Each linear conflict provably
      requires 2 additional moves beyond Manhattan. So Manhattan + 2*conflicts
      is still a lower bound on actual cost.

    Args:
        board: Current board.
        goal:  Goal board.

    Returns:
        Manhattan distance + 2 * number of linear conflicts (int).
    """
    goal_map = _build_goal_map(goal)
    n = len(board)

    # Start with Manhattan distance
    distance = manhattan(board, goal)

    # Count row conflicts
    for r in range(n):
        distance += _count_row_conflicts(board, goal_map, r, n)

    # Count column conflicts
    for c in range(n):
        distance += _count_col_conflicts(board, goal_map, c, n)

    return distance


def _count_row_conflicts(board, goal_map: dict, row: int, n: int) -> int:
    """
    Count linear conflicts in a single row.

    A conflict in row R: tiles A and B are both in row R, both BELONG
    in row R (their goal row is R), but A is to the left of B while
    A's goal column is to the right of B's goal column.

    Args:
        board:    The current board.
        goal_map: Dict mapping tile_value → (goal_row, goal_col).
        row:      Which row to check.
        n:        Board size.

    Returns:
        2 * number of conflicts in this row.
    """
    # Collect tiles in this row that belong in this row
    tiles_in_goal_row = []
    for c in range(n):
        tile = board[row][c]
        if tile == 0:
            continue
        goal_r, goal_c = goal_map[tile]
        if goal_r == row:
            # This tile is in its goal row — record (current_col, goal_col)
            tiles_in_goal_row.append((c, goal_c))

    # Count conflicts: pairs where current order != goal order
    conflicts = 0
    for i in range(len(tiles_in_goal_row)):
        for j in range(i + 1, len(tiles_in_goal_row)):
            cur_ci, goal_ci = tiles_in_goal_row[i]
            cur_cj, goal_cj = tiles_in_goal_row[j]
            # i is left of j in current (cur_ci < cur_cj, guaranteed by loop order)
            # but i should be right of j in goal
            if goal_ci > goal_cj:
                conflicts += 1

    return 2 * conflicts


def _count_col_conflicts(board, goal_map: dict, col: int, n: int) -> int:
    """
    Count linear conflicts in a single column.

    Same logic as row conflicts but transposed: tiles in column C that
    belong in column C but are in the wrong vertical order.

    Args:
        board:    The current board.
        goal_map: Dict mapping tile_value → (goal_row, goal_col).
        col:      Which column to check.
        n:        Board size.

    Returns:
        2 * number of conflicts in this column.
    """
    # Collect tiles in this column that belong in this column
    tiles_in_goal_col = []
    for r in range(n):
        tile = board[r][col]
        if tile == 0:
            continue
        goal_r, goal_c = goal_map[tile]
        if goal_c == col:
            # This tile is in its goal column — record (current_row, goal_row)
            tiles_in_goal_col.append((r, goal_r))

    # Count conflicts: pairs where current order != goal order
    conflicts = 0
    for i in range(len(tiles_in_goal_col)):
        for j in range(i + 1, len(tiles_in_goal_col)):
            cur_ri, goal_ri = tiles_in_goal_col[i]
            cur_rj, goal_rj = tiles_in_goal_col[j]
            # i is above j in current (cur_ri < cur_rj, guaranteed by loop order)
            # but i should be below j in goal
            if goal_ri > goal_rj:
                conflicts += 1

    return 2 * conflicts
