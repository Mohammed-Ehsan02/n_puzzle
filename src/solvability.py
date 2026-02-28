# ==========================================================================  #
#  solvability.py — Puzzle Solvability Checker                                #
# ==========================================================================  #
#                                                                              #
#  Determines if a given puzzle configuration can reach the snail goal.        #
#                                                                              #
#  WHY THIS IS NEEDED:                                                         #
#    Not every arrangement of tiles can reach the goal. Exactly half of all    #
#    possible permutations are reachable. Without this check, the A* search   #
#    would run forever on unsolvable puzzles.                                  #
#                                                                              #
#  HOW IT WORKS (Permutation Parity):                                          #
#    The puzzle is a permutation of tiles. Each legal move (sliding a tile     #
#    into the blank) is a transposition (swap of 2 elements). Whether we      #
#    can get from state A to state B depends on the parity of the             #
#    permutation A→B matching the parity of moves the blank must make.        #
#                                                                              #
#    1. Build the permutation that maps goal positions to initial positions    #
#    2. Count inversions in that permutation (including the blank as a tile)   #
#    3. Compute Manhattan distance of blank from initial to goal position      #
#    4. Solvable iff: inversions % 2 == manhattan_distance % 2                 #
#                                                                              #
#  WHY PARITY WORKS:                                                           #
#    - Each slide move = 1 transposition = flips parity once                   #
#    - The blank moves on a grid. Its total moves always have the same         #
#      parity as its Manhattan distance (extras come in pairs).                #
#    - So: permutation parity must match blank's Manhattan distance parity.    #
#                                                                              #
#  IMPORTANT: The old version used inversion counting for goal [1,2,...,0].    #
#  That does NOT work for the snail goal. This version works for ANY goal.     #
# ==========================================================================  #

from goal import generate_snail_goal


def count_inversions(permutation: list[int]) -> int:
    """
    Count the number of inversions in a permutation.

    An inversion is a pair (i, j) where i < j but permutation[i] > permutation[j].
    The parity of the inversion count tells us the parity of the permutation
    (even inversions = even permutation, odd inversions = odd permutation).

    Args:
        permutation: A list of integers representing a permutation.

    Returns:
        The number of inversions.
    """
    count = 0
    length = len(permutation)
    for i in range(length):
        for j in range(i + 1, length):
            if permutation[i] > permutation[j]:
                count += 1
    return count


def is_solvable(puzzle: list[list[int]]) -> bool:
    """
    Check if the given puzzle can reach the snail goal state.

    Algorithm:
      1. Generate the snail goal for this puzzle size.
      2. Build a permutation mapping: for each position i in the goal,
         P[i] = the position in the initial state where that tile currently is.
      3. Count inversions in P (all N² elements, including blank).
      4. Find the blank tile in both states, compute Manhattan distance.
      5. Solvable iff inversions and Manhattan distance have the same parity.

    Why include the blank in the permutation?
      Because the blank is part of the full state. The parity of the FULL
      permutation (all N² elements) must match the parity of the number
      of transpositions (moves) needed, which equals the blank's travel
      distance parity.

    Args:
        puzzle: 2D list representing the current puzzle state.

    Returns:
        True if the puzzle is solvable, False otherwise.
    """
    n = len(puzzle)
    goal = generate_snail_goal(n)

    # Flatten both boards into 1D lists
    flat_puzzle = [val for row in puzzle for val in row]
    flat_goal = [val for row in goal for val in row]

    # Map each tile value to its position in the initial (puzzle) state
    # Example: if tile 5 is at index 3 in flat_puzzle, then initial_pos[5] = 3
    initial_pos = {}
    for idx, val in enumerate(flat_puzzle):
        initial_pos[val] = idx

    # Build the permutation: for each goal position i, where is that tile
    # currently sitting in the initial state?
    # P[i] = position-in-initial of the tile that belongs at goal-position i
    permutation = [initial_pos[flat_goal[i]] for i in range(n * n)]

    inversions = count_inversions(permutation)

    # Find blank (0) positions in both states
    blank_initial_idx = initial_pos[0]
    blank_goal_idx = flat_goal.index(0)

    # Convert flat indices to (row, col) for Manhattan distance
    blank_i_row, blank_i_col = blank_initial_idx // n, blank_initial_idx % n
    blank_g_row, blank_g_col = blank_goal_idx // n, blank_goal_idx % n

    manhattan_distance = abs(blank_i_row - blank_g_row) + abs(blank_i_col - blank_g_col)

    # Solvable iff both parities match
    return (inversions % 2) == (manhattan_distance % 2)
