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
#  STATUS: Not yet implemented — this is the next step.                        #
# ==========================================================================  #


def manhattan(board, goal):
    """
    Manhattan distance heuristic.

    For each non-blank tile, compute the taxicab distance between its
    current position and its goal position. Sum all distances.

    Args:
        board: Current board (tuple of tuples or list of lists).
        goal:  Goal board (same format).

    Returns:
        Total Manhattan distance (int).
    """
    # TODO: Implement
    pass


def misplaced(board, goal):
    """
    Misplaced tiles (Hamming distance) heuristic.

    Count the number of tiles that are NOT in their goal position.
    The blank tile (0) is excluded from the count.

    Args:
        board: Current board.
        goal:  Goal board.

    Returns:
        Number of misplaced tiles (int).
    """
    # TODO: Implement
    pass


def linear_conflict(board, goal):
    """
    Linear conflict heuristic.

    Start with Manhattan distance, then add 2 for every pair of tiles
    that are in the same row (or column) as their goal positions, but
    are in the wrong order relative to each other.

    This is strictly more informed than Manhattan while still admissible.

    Args:
        board: Current board.
        goal:  Goal board.

    Returns:
        Manhattan distance + 2 * number of linear conflicts (int).
    """
    # TODO: Implement
    pass
