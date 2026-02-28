# ==========================================================================  #
#  parser.py — Puzzle Input Handling                                          #
# ==========================================================================  #
#                                                                              #
#  Two ways to get a puzzle into the solver:                                   #
#    1. Read from a file  (read_puzzle_from_file)                              #
#    2. Generate randomly (generate_random_puzzle)                             #
#                                                                              #
#  INPUT FILE FORMAT (from subject appendix):                                  #
#    - Lines starting with '#' are comments (ignored)                          #
#    - Inline comments after '#' are also stripped                             #
#    - First non-comment line: a single integer N (the puzzle size)            #
#    - Next N lines: N space-separated integers each                           #
#    - Numbers must be 0 through N²-1, each appearing exactly once            #
#    - 0 represents the blank (empty) tile                                     #
#    - Alignment doesn't matter (numbers can be spaced however)                #
#                                                                              #
#  LIBRARIES USED:                                                             #
#    - random (stdlib): random.shuffle() to randomize tile positions           #
# ==========================================================================  #

import random
from solvability import is_solvable


def read_puzzle_from_file(file_path: str) -> list[list[int]]:
    """
    Parse a puzzle file into a 2D list.

    Steps:
      1. Read all lines from file.
      2. Strip comments (everything after '#') and blank lines.
      3. First remaining line = puzzle size N.
      4. Next N lines = puzzle rows, each with exactly N integers.
      5. Validate: numbers must be 0..N²-1, each exactly once.

    Args:
        file_path: Path to the puzzle input file.

    Returns:
        A 2D list of integers representing the puzzle board.

    Raises:
        ValueError: If the file format is invalid.
        FileNotFoundError: If the file doesn't exist.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Strip comments and empty lines
    # "3 2 6 #another comment" → "3 2 6"
    cleaned = []
    for line in lines:
        stripped = line.split('#')[0].strip()
        if stripped:
            cleaned.append(stripped)

    if not cleaned:
        raise ValueError("File is empty or contains only comments.")

    # First line must be the puzzle size
    try:
        size = int(cleaned[0])
    except ValueError:
        raise ValueError(
            f"First non-comment line must be the puzzle size (integer), "
            f"got: '{cleaned[0]}'"
        )

    if size < 2:
        raise ValueError(f"Puzzle size must be at least 2, got: {size}")

    # Must have exactly N rows after the size line
    data_lines = cleaned[1:]
    if len(data_lines) != size:
        raise ValueError(
            f"Expected {size} rows of puzzle data, got {len(data_lines)}"
        )

    # Parse each row
    puzzle = []
    for i, line in enumerate(data_lines):
        try:
            row = list(map(int, line.split()))
        except ValueError:
            raise ValueError(
                f"Row {i + 1} contains non-integer values: '{line}'"
            )
        if len(row) != size:
            raise ValueError(
                f"Row {i + 1}: expected {size} numbers, got {len(row)}"
            )
        puzzle.append(row)

    # Validate the puzzle contents
    _validate_puzzle(puzzle, size)
    return puzzle


def generate_random_puzzle(n: int) -> list[list[int]]:
    """
    Generate a random solvable N×N puzzle.

    Algorithm:
      1. Create a flat list [0, 1, 2, ..., N²-1].
      2. Shuffle it randomly.
      3. Reshape into an N×N grid.
      4. Check if it's solvable (relative to the snail goal).
      5. If not, shuffle again and retry.

    About half of all permutations are solvable, so on average
    this takes ~2 attempts.

    Args:
        n: Size of one side of the puzzle.

    Returns:
        A 2D list representing a solvable puzzle.
    """
    if n < 2:
        raise ValueError(f"Puzzle size must be at least 2, got: {n}")

    while True:
        flat = list(range(n * n))
        random.shuffle(flat)

        # Reshape flat list into N×N grid
        puzzle = [flat[i * n:(i + 1) * n] for i in range(n)]

        if is_solvable(puzzle):
            return puzzle


def _validate_puzzle(puzzle: list[list[int]], size: int) -> None:
    """
    Validate that a parsed puzzle has correct content.

    Checks:
      - All numbers are in range [0, N²-1]
      - Each number appears exactly once
      - Exactly one blank tile (0) exists

    Args:
        puzzle: The parsed 2D puzzle board.
        size: The expected side length N.

    Raises:
        ValueError: If any validation fails.
    """
    expected = set(range(size * size))
    seen = []

    for row in puzzle:
        for num in row:
            if num < 0 or num >= size * size:
                raise ValueError(
                    f"Invalid tile value {num}: must be between 0 and {size * size - 1}"
                )
            seen.append(num)

    seen_set = set(seen)

    # Check for duplicates
    if len(seen_set) != len(seen):
        duplicates = [x for x in seen_set if seen.count(x) > 1]
        raise ValueError(f"Duplicate tile values found: {duplicates}")

    # Check for missing numbers
    missing = expected - seen_set
    if missing:
        raise ValueError(f"Missing tile values: {sorted(missing)}")
