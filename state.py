# Represents a puzzle state, with movement and hashing

class PuzzleState:
    def __init__(self, board, g=0, h=0, parent=None):
        # Store grid, blank position, g/h/f values
        pass

    def get_neighbors(self):
        # Return all valid neighbor states (after sliding)
        pass

    def is_goal(self, goal_board):
        # Check if current board matches the goal board
        pass

    def __hash__(self):
        # Allow usage in sets
        pass

    def __eq__(self, other):
        # Check board equality
        pass
