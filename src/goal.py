# ==========================================================================  #
#  goal.py — Snail Goal Generator                                            #
# ==========================================================================  #
#                                                                              #
#  Generates the target "snail" (clockwise spiral) arrangement for any N×N    #
#  board. This is the solved state that the A* search works towards.          #
#                                                                              #
#  The snail pattern fills numbers 1 → N²-1 in a clockwise spiral starting   #
#  from the top-left corner. The last cell in the spiral gets 0 (blank).      #
#                                                                              #
#  Example for N=3:       Example for N=4:                                    #
#    1  2  3                1   2   3   4                                     #
#    8  0  4               12  13  14   5                                     #
#    7  6  5               11   0  15   6                                     #
#                          10   9   8   7                                     #
# ==========================================================================  #


def generate_snail_goal(n: int) -> list[list[int]]:
    """
    Generate the snail (clockwise spiral) goal state for an N×N puzzle.

    Algorithm:
      - Start at position (0, 0), facing right.
      - Place numbers 1 through N²-1 along the spiral path.
      - When we hit a wall or an already-visited cell, turn clockwise
        (right → down → left → up → right → ...).
      - The very last cell in the spiral gets 0 (the blank tile).

    Args:
        n: Size of one side of the puzzle (e.g., 3 for a 3×3 grid).

    Returns:
        A 2D list (list of lists) representing the goal board.
    """
    goal = [[0] * n for _ in range(n)]
    visited = [[False] * n for _ in range(n)]

    # Direction vectors: right, down, left, up (clockwise order)
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    row = 0
    col = 0
    dir_idx = 0  # Start moving right
    num = 1

    # Place numbers 1 through N²-1 along the spiral
    for _ in range(n * n - 1):
        goal[row][col] = num
        visited[row][col] = True
        num += 1

        # Peek at the next cell in current direction
        next_row = row + directions[dir_idx][0]
        next_col = col + directions[dir_idx][1]

        # If next cell is valid and unvisited, move there
        if 0 <= next_row < n and 0 <= next_col < n and not visited[next_row][next_col]:
            row, col = next_row, next_col
        else:
            # Turn clockwise and move in the new direction
            dir_idx = (dir_idx + 1) % 4
            row += directions[dir_idx][0]
            col += directions[dir_idx][1]

    # The last unvisited cell gets 0 (blank tile)
    goal[row][col] = 0
    return goal
