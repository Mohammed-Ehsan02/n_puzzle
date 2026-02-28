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
#  STATUS: Not yet implemented — needed when A* is implemented.                #
# ==========================================================================  #


def reconstruct_path(state):
    """
    Trace parent pointers from goal back to start, return the full path.

    Args:
        state: The goal PuzzleState (end of the solution).

    Returns:
        A list of PuzzleStates from initial state to goal state.
    """
    # TODO: Implement
    pass
