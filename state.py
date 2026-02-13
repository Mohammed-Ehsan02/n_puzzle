# Represents a puzzle state, with movement and hashing
import copy

class PuzzleState:
    def __init__(self, board, g=0, h=0, parent=None):
        self.board = board
        self.n = len(board)
        self.g = g  # Cost so far
        self.h = h  # Heuristic cost
        self.f = g + h  # Total cost
        self.parent = parent

        # Find blank tile (0) position
        for i in range(self.n):
            for j in range(self.n):
                if board[i][j] == 0:
                    self.blank_pos = (i, j)
                    break

    def get_neighbors(self) -> list:
        neighbors = []
        row, col = self.blank_pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

        for dr, dc in directions:
            new_r, new_c = row + dr, col + dc

            if 0 <= new_r < self.n and 0 <= new_c < self.n:
                # Copy board and swap blank with adjacent tile
                new_board = copy.deepcopy(self.board)
                new_board[row][col], new_board[new_r][new_c] = new_board[new_r][new_c], new_board[row][col]

                neighbor = PuzzleState(new_board, g=self.g + 1, parent=self)
                neighbors.append(neighbor)

        return neighbors

    def is_goal(self, goal_board: list[list[int]]) -> bool:
        return self.board == goal_board

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.board))

    def __lt__(self, other):
        return self.f < other.f  # For priority queue comparison

    def __repr__(self):
        return f"PuzzleState(f={self.f}, g={self.g}, h={self.h})"
