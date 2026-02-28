# ==========================================================================  #
#  utils.py — Search Utilities                                                #
# ==========================================================================  #
#                                                                              #
#  Helper functions shared by the search algorithms.                           #
#                                                                              #
#  PATH RECONSTRUCTION:                                                        #
#    Each PuzzleState has a 'parent' pointer to the state it came from.        #
#    To get the solution path, we start at the goal state and follow           #
#    parent pointers back to the start (where parent is None).                 #
#    Then reverse the list to get start → goal order.                          #
#                                                                              #
#  DISPLAY:                                                                    #
#    print_board() formats a board state nicely for terminal output.           #
# ==========================================================================  #


def reconstruct_path(state) -> list:
    """
    Trace parent pointers from goal back to start, return the full path.

    A* builds a tree of PuzzleStates connected by 'parent' pointers:
        start (parent=None) ← state_1 ← state_2 ← ... ← goal

    We follow these pointers backwards from goal to start, collecting
    each state, then reverse to get the solution in forward order:
        [start, state_1, state_2, ..., goal]

    The number of moves = len(path) - 1  (the start state is move 0).

    Args:
        state: The goal PuzzleState (the end of the solved chain).

    Returns:
        A list of PuzzleStates ordered from initial state to goal state.
    """
    path = []
    current = state
    while current is not None:
        path.append(current)
        current = current.parent
    path.reverse()
    return path


def print_board(board, n: int) -> str:
    """
    Format a board as a readable string for terminal output.

    Example for 3×3:
      " 1  2  3"
      " 8  0  4"
      " 7  6  5"

    The width of each number is based on the largest number (N²-1)
    so columns stay aligned for any puzzle size.

    Args:
        board: The board (tuple of tuples or list of lists).
        n:     The puzzle size (for calculating column width).

    Returns:
        A formatted multi-line string.
    """
    width = len(str(n * n - 1))
    lines = []
    for row in board:
        line = " ".join(str(tile).rjust(width) for tile in row)
        lines.append(line)
    return "\n".join(lines)
