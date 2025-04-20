# Handles input puzzle reading and random generation
import random
from checker import is_solvable  # We'll implement this soon

def read_puzzle_from_file(file_path: str) -> list[list[int]]:
    puzzle = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Filter out comments and empty lines
    lines = [line.split('#')[0].strip() for line in lines if line.strip() and not line.strip().startswith("#")]
    
    if not lines:
        raise ValueError("File is empty or only contains comments.")
    
    try:
        size = int(lines[0])
    except ValueError:
        raise ValueError("First non-comment line must be the puzzle size (integer).")

    if len(lines[1:]) != size:
        raise ValueError(f"Expected {size} rows of puzzle data, got {len(lines[1:])}")

    for line in lines[1:]:
        row = list(map(int, line.split()))
        if len(row) != size:
            raise ValueError(f"Expected {size} elements in row, got {len(row)}")
        puzzle.append(row)

    return puzzle

def generate_random_puzzle(n: int) -> list[list[int]]:
    while True:
        flat_puzzle = list(range(n * n))
        random.shuffle(flat_puzzle)

        # Convert flat list to 2D grid
        puzzle = [flat_puzzle[i * n:(i + 1) * n] for i in range(n)]

        if is_solvable(puzzle):
            return puzzle
