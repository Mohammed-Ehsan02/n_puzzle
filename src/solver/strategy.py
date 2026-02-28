# ==========================================================================  #
#  strategy.py — Alternative Search Strategies (BONUS)                        #
# ==========================================================================  #
#                                                                              #
#  These are variations of A* that use different f(x) formulas:                #
#                                                                              #
#  GREEDY SEARCH:                                                              #
#    f(x) = h(x)  (only heuristic, ignores path cost)                         #
#    Fast but NOT guaranteed to find optimal solution.                          #
#    It always expands the state that "looks" closest to goal.                 #
#                                                                              #
#  UNIFORM-COST SEARCH:                                                        #
#    f(x) = g(x)  (only path cost, ignores heuristic)                         #
#    Guaranteed optimal but slow (like BFS with costs).                        #
#    Equivalent to Dijkstra's algorithm.                                       #
#                                                                              #
#  Both produce the same output format as A* but may find different            #
#  solutions. That's the point — comparing the 3 strategies.                   #
#                                                                              #
#  STATUS: Bonus — implement only after mandatory part is perfect.             #
# ==========================================================================  #


def greedy_search(initial_state, goal_board, heuristic_func):
    """
    Greedy best-first search: f(x) = h(x).

    Args:
        initial_state:  PuzzleState of the starting board.
        goal_board:     The goal board.
        heuristic_func: A function(board, goal) -> int.

    Returns:
        TODO: Same format as a_star().
    """
    # TODO: Implement (bonus)
    pass


def uniform_cost_search(initial_state, goal_board):
    """
    Uniform-cost search: f(x) = g(x).

    No heuristic needed — just expands cheapest path first.

    Args:
        initial_state: PuzzleState of the starting board.
        goal_board:    The goal board.

    Returns:
        TODO: Same format as a_star().
    """
    # TODO: Implement (bonus)
    pass
