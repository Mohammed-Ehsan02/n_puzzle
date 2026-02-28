# ==========================================================================  #
#  state.py — Puzzle State Representation                                     #
# ==========================================================================  #
#                                                                              #
#  Each node in the A* search tree is a PuzzleState. It holds:                 #
#    - board:     the tile arrangement (tuple of tuples, immutable)             #
#    - g:         cost from start (number of moves so far)                     #
#    - h:         heuristic estimate to goal (set by the search algorithm)     #
#    - f:         total cost = g + h (used by priority queue)                  #
#    - parent:    pointer to previous state (for path reconstruction)          #
#    - blank_pos: (row, col) of the empty tile                                #
#                                                                              #
#  WHY TUPLES INSTEAD OF LISTS?                                                #
#    - Immutable: can't accidentally modify a state during search              #
#    - Hashable:  can be used directly in sets/dicts (closed set lookup)       #
#    - Faster:    no need for copy.deepcopy() when creating neighbors          #
#    - Memory:    tuples use less memory than lists                            #
#                                                                              #
#  HOW NEIGHBORS WORK:                                                         #
#    The blank tile can swap with up to 4 adjacent tiles (up/down/left/right). #
#    Each swap creates a NEW PuzzleState with g incremented by 1.              #
#    The heuristic h is NOT set here — the search algorithm sets it.           #
#                                                                              #
#  DUNDER METHODS (special Python methods):                                    #
#    __eq__:   two states are equal if their boards match                       #
#    __hash__: hash based on board (for set/dict membership)                   #
#    __lt__:   compare by f value (for heapq priority queue ordering)          #
#    __repr__: debug-friendly string representation                            #
# ==========================================================================  #


class PuzzleState:
    """
    Represents a single configuration of the N-puzzle board.

    This is a node in the search tree. The A* algorithm creates many of
    these, comparing them by f value and checking membership in sets.
    """

    def __init__(self, board, g=0, h=0, parent=None):
        """
        Create a new puzzle state.

        Args:
            board:  2D structure (list of lists OR tuple of tuples).
                    Will be stored internally as tuple of tuples.
            g:      Cost from start state (number of moves). Default 0.
            h:      Heuristic cost to goal. Default 0.
            parent: The PuzzleState we came from (for path reconstruction).
        """
        # Convert to tuple of tuples if given lists (ensures immutability)
        if isinstance(board, list):
            self.board = tuple(tuple(row) for row in board)
        else:
            self.board = board

        self.n = len(self.board)
        self.g = g          # Actual cost from start
        self.h = h          # Heuristic estimate to goal
        self.f = g + h      # Total estimated cost
        self.parent = parent

        # Find the blank tile (0) position
        # We need this to know which moves are possible
        self.blank_pos = None
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] == 0:
                    self.blank_pos = (i, j)
                    return  # Found it, no need to keep searching

    def get_neighbors(self) -> list:
        """
        Generate all valid neighbor states (1 move away from current state).

        For each of the 4 directions (up/down/left/right):
          - Check if the move is within bounds
          - Create a new board with the blank and adjacent tile swapped
          - Wrap it in a new PuzzleState with g = self.g + 1

        Note: h is left at 0. The search algorithm must compute and set it.

        Returns:
            A list of PuzzleState objects (1 to 4 neighbors).
        """
        neighbors = []
        row, col = self.blank_pos

        # Up, Down, Left, Right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            new_r, new_c = row + dr, col + dc

            # Skip if out of bounds
            if not (0 <= new_r < self.n and 0 <= new_c < self.n):
                continue

            # Build new board: convert to list of lists, swap, convert back
            # This is much faster than copy.deepcopy()
            rows = [list(r) for r in self.board]
            rows[row][col], rows[new_r][new_c] = rows[new_r][new_c], rows[row][col]
            new_board = tuple(tuple(r) for r in rows)

            neighbor = PuzzleState(new_board, g=self.g + 1, parent=self)
            neighbors.append(neighbor)

        return neighbors

    def is_goal(self, goal_board) -> bool:
        """Check if this state matches the goal. Works with list or tuple."""
        if isinstance(goal_board, list):
            return self.board == tuple(tuple(row) for row in goal_board)
        return self.board == goal_board

    def __eq__(self, other):
        """Two states are equal if their boards are identical."""
        return isinstance(other, PuzzleState) and self.board == other.board

    def __hash__(self):
        """Hash based on board content (tuples are natively hashable)."""
        return hash(self.board)

    def __lt__(self, other):
        """
        Compare states by f value.
        Used by heapq to determine priority in the open set.
        Lower f = higher priority = gets expanded first.
        """
        return self.f < other.f

    def __repr__(self):
        """Debug string showing cost values."""
        return f"PuzzleState(f={self.f}, g={self.g}, h={self.h})"
