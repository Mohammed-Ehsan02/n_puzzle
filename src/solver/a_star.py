# ==========================================================================  #
#  a_star.py — A* Search Algorithm                                            #
# ==========================================================================  #
#                                                                              #
#  A* finds the shortest path from an initial state to the goal state.         #
#  It uses f(x) = g(x) + h(x) to prioritize which states to explore:          #
#    - g(x): actual cost from start (number of moves so far)                   #
#    - h(x): heuristic estimate of remaining cost to goal                      #
#    - f(x): total estimated cost (lower = explore first)                      #
#                                                                              #
#  Data structures needed:                                                     #
#    - Open set:   priority queue (min-heap) of states to explore              #
#    - Closed set: hash set of already-expanded states                         #
#                                                                              #
#  LIBRARIES NEEDED:                                                           #
#    - heapq (stdlib): min-heap operations for the priority queue              #
#                                                                              #
#  STATUS: Not yet implemented — next step after heuristics.                   #
# ==========================================================================  #


def a_star(initial_state, goal_board, heuristic_func):
    """
    Run A* search to solve the puzzle.

    Args:
        initial_state:  PuzzleState of the starting board.
        goal_board:     The goal board (2D list or tuple of tuples).
        heuristic_func: A function(board, goal) -> int that estimates cost.

    Returns:
        TODO: A tuple of (path, stats) where:
          - path: list of PuzzleStates from initial to goal
          - stats: dict with 'time_complexity', 'size_complexity', 'moves'
    """
    # TODO: Implement A* search
    pass
