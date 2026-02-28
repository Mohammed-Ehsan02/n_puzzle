# ==========================================================================  #
#  a_star.py — A* Search Algorithm                                            #
# ==========================================================================  #
#                                                                              #
#  A* finds the shortest (optimal) path from an initial state to the goal.    #
#  It uses f(x) = g(x) + h(x) to prioritize which states to explore:          #
#    - g(x): actual cost from start (number of moves so far)                   #
#    - h(x): heuristic estimate of remaining cost to goal                      #
#    - f(x): total estimated cost (lower = explore first)                      #
#                                                                              #
#  DATA STRUCTURES:                                                            #
#    - Open set (priority queue / min-heap):                                   #
#        States discovered but not yet expanded. We always pick the one        #
#        with the lowest f value. Implemented with heapq.                      #
#    - Closed set (hash set):                                                  #
#        States already expanded. We never re-expand these (unless we          #
#        find a cheaper path — see reopening below).                           #
#    - Open dict (hash map):                                                   #
#        board → PuzzleState, for O(1) lookup of states in the open set.      #
#        heapq doesn't support "is this element in the heap?" efficiently,    #
#        so we keep a parallel dict.                                           #
#                                                                              #
#  REOPENING (from subject pseudocode):                                        #
#    If we find a cheaper path to a state already in closed, we must           #
#    move it back to open with the new (lower) g value. This is rare           #
#    with admissible+consistent heuristics, but we implement it for            #
#    correctness per the subject's pseudocode.                                 #
#                                                                              #
#  STATISTICS (required by subject):                                           #
#    - time_complexity:  total states ever popped from open set                #
#    - size_complexity:  max(len(open) + len(closed)) at any point             #
#    - moves:            number of steps in the solution path                  #
#                                                                              #
#  LIBRARY:                                                                    #
#    - heapq (stdlib): provides heappush/heappop for O(log n) priority queue  #
# ==========================================================================  #

import heapq
from state import PuzzleState
from solver.utils import reconstruct_path


def a_star(initial_state, goal_board, heuristic_func):
    """
    Run A* search to solve the puzzle.

    Algorithm (following the subject's pseudocode):
      1. Put initial state in the open set.
      2. While open set is not empty:
         a. Pop state with lowest f from open set.
         b. If it's the goal → reconstruct and return the path.
         c. Move it to the closed set.
         d. For each neighbor:
            - If not in open and not in closed: add to open.
            - If already in open/closed but new path is cheaper: update it.
              If it was in closed, move it back to open (reopening).
      3. If open set empties → no solution (shouldn't happen if solvable).

    Args:
        initial_state:  PuzzleState of the starting board.
        goal_board:     The goal board (list of lists or tuple of tuples).
        heuristic_func: A function(board, goal) → int that estimates cost.

    Returns:
        A tuple (path, stats) where:
          - path:  list of PuzzleStates from initial to goal
          - stats: dict with 'time_complexity', 'size_complexity', 'moves'

        Returns (None, stats) if no solution exists (shouldn't happen for
        solvable puzzles, but handled gracefully).
    """
    # Compute h for the initial state
    initial_state.h = heuristic_func(initial_state.board, goal_board)
    initial_state.f = initial_state.g + initial_state.h

    # ------------------------------------------------------------------
    # Open set: min-heap ordered by f value.
    # heapq uses __lt__ on PuzzleState, which compares by f.
    # ------------------------------------------------------------------
    open_heap = [initial_state]

    # Parallel dict for O(1) "is this board in the open set?" lookup.
    # Maps board (tuple of tuples) → PuzzleState
    open_dict = {initial_state.board: initial_state}

    # ------------------------------------------------------------------
    # Closed set: boards we've already fully expanded.
    # Maps board (tuple of tuples) → PuzzleState
    # ------------------------------------------------------------------
    closed_dict = {}

    # ------------------------------------------------------------------
    # Statistics tracking (required by subject)
    # ------------------------------------------------------------------
    time_complexity = 0   # States popped from open (expanded)
    size_complexity = 0   # Max total states in memory at once

    # Convert goal for comparison (ensure tuple of tuples)
    if isinstance(goal_board, list):
        goal_tuple = tuple(tuple(row) for row in goal_board)
    else:
        goal_tuple = goal_board

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    while open_heap:
        # Track max memory usage
        current_memory = len(open_dict) + len(closed_dict)
        if current_memory > size_complexity:
            size_complexity = current_memory

        # Pop state with lowest f value
        current = heapq.heappop(open_heap)

        # Skip stale entries: if this board was already updated with a
        # better path, the old entry is still in the heap. Skip it.
        if current.board not in open_dict:
            continue
        if open_dict[current.board] is not current:
            continue

        # Remove from open set
        del open_dict[current.board]
        time_complexity += 1

        # Goal check
        if current.board == goal_tuple:
            path = reconstruct_path(current)
            stats = {
                "time_complexity": time_complexity,
                "size_complexity": size_complexity,
                "moves": len(path) - 1,
            }
            return path, stats

        # Move current to closed set
        closed_dict[current.board] = current

        # Expand neighbors
        for neighbor in current.get_neighbors():
            board = neighbor.board

            # Compute h and f for this neighbor
            neighbor.h = heuristic_func(board, goal_board)
            neighbor.f = neighbor.g + neighbor.h

            # Case 1: Not seen before → add to open
            if board not in open_dict and board not in closed_dict:
                open_dict[board] = neighbor
                heapq.heappush(open_heap, neighbor)

            # Case 2: Already in open → update if cheaper
            elif board in open_dict:
                existing = open_dict[board]
                if neighbor.g < existing.g:
                    # Found a cheaper path — replace in open set.
                    # We can't remove from heap efficiently, so we add
                    # the new one and let the stale check skip the old.
                    open_dict[board] = neighbor
                    heapq.heappush(open_heap, neighbor)

            # Case 3: Already in closed → reopen if cheaper
            elif board in closed_dict:
                existing = closed_dict[board]
                if neighbor.g < existing.g:
                    # Cheaper path found to an already-expanded state.
                    # Move it back to open with the new cost.
                    del closed_dict[board]
                    open_dict[board] = neighbor
                    heapq.heappush(open_heap, neighbor)

    # Open set exhausted — no solution found
    stats = {
        "time_complexity": time_complexity,
        "size_complexity": size_complexity,
        "moves": -1,
    }
    return None, stats
