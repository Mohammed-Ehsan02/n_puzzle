# Generates the snail goal for any N x N board

def generate_snail_goal(n: int) -> list[list[int]]:
    goal = [[0] * n for _ in range(n)]
    visited = [[False] * n for _ in range(n)]
    
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    row = col = dir_idx = 0
    num = 1

    for _ in range(n * n - 1):
        goal[row][col] = num
        visited[row][col] = True
        num += 1

        # Next coordinates
        next_row = row + directions[dir_idx][0]
        next_col = col + directions[dir_idx][1]

        # Change direction if needed
        if (0 <= next_row < n and 0 <= next_col < n and not visited[next_row][next_col]):
            row, col = next_row, next_col
        else:
            dir_idx = (dir_idx + 1) % 4
            row += directions[dir_idx][0]
            col += directions[dir_idx][1]

    # Final cell = 0 (empty tile)
    goal[row][col] = 0
    return goal

