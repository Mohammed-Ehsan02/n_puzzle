# ==========================================================================  #
#  test_parser.py — Tests for puzzle file parsing and random generation       #
# ==========================================================================  #
#                                                                              #
#  What we test:                                                               #
#    - Valid files parse correctly                                             #
#    - Comments (full-line and inline) are stripped                            #
#    - Proper errors on: wrong row count, wrong column count, duplicates,     #
#      out-of-range values, missing values, non-integer content               #
#    - Random puzzle generation produces valid, solvable puzzles               #
# ==========================================================================  #

import os
import tempfile
import pytest
from parser import read_puzzle_from_file, generate_random_puzzle


# ------------------------------------------------------------------ #
#  Helper: write a temporary puzzle file and return its path          #
# ------------------------------------------------------------------ #

def _write_temp_file(content: str) -> str:
    """Write content to a temp file, return path. Caller must delete."""
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return path


# ================================================================== #
#  Valid file parsing                                                  #
# ================================================================== #

class TestValidFiles:

    def test_simple_3x3(self):
        """Parse a basic 3×3 puzzle."""
        path = _write_temp_file("3\n1 2 3\n4 5 6\n7 8 0\n")
        try:
            puzzle = read_puzzle_from_file(path)
            assert puzzle == [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        finally:
            os.unlink(path)

    def test_with_comments(self):
        """Comments starting with # should be stripped."""
        content = "# this is a comment\n3\n1 2 3 #inline\n4 5 6\n7 8 0\n"
        path = _write_temp_file(content)
        try:
            puzzle = read_puzzle_from_file(path)
            assert puzzle == [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        finally:
            os.unlink(path)

    def test_with_extra_whitespace(self):
        """Numbers can have varying amounts of whitespace between them."""
        content = "3\n 1   2   3 \n  4  5  6  \n7  8   0\n"
        path = _write_temp_file(content)
        try:
            puzzle = read_puzzle_from_file(path)
            assert puzzle == [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        finally:
            os.unlink(path)

    def test_4x4_from_example_file(self):
        """Parse the actual example_4x4.txt from the project."""
        path = os.path.join(os.path.dirname(__file__), "..", "puzzles", "example_4x4.txt")
        puzzle = read_puzzle_from_file(path)
        assert len(puzzle) == 4
        assert all(len(row) == 4 for row in puzzle)
        # Check all numbers 0-15 present
        flat = [val for row in puzzle for val in row]
        assert sorted(flat) == list(range(16))

    def test_only_comments_before_size(self):
        """Multiple comment lines before the size line."""
        content = "# comment 1\n# comment 2\n# comment 3\n3\n1 2 3\n4 5 6\n7 8 0\n"
        path = _write_temp_file(content)
        try:
            puzzle = read_puzzle_from_file(path)
            assert puzzle == [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        finally:
            os.unlink(path)


# ================================================================== #
#  Invalid files — should raise ValueError                             #
# ================================================================== #

class TestInvalidFiles:

    def test_empty_file(self):
        """Empty file should raise ValueError."""
        path = _write_temp_file("")
        try:
            with pytest.raises(ValueError, match="empty"):
                read_puzzle_from_file(path)
        finally:
            os.unlink(path)

    def test_only_comments(self):
        """File with only comments should raise ValueError."""
        path = _write_temp_file("# just comments\n# nothing else\n")
        try:
            with pytest.raises(ValueError, match="empty"):
                read_puzzle_from_file(path)
        finally:
            os.unlink(path)

    def test_non_integer_size(self):
        """Non-integer on the size line."""
        path = _write_temp_file("abc\n1 2 3\n4 5 6\n7 8 0\n")
        try:
            with pytest.raises(ValueError, match="size"):
                read_puzzle_from_file(path)
        finally:
            os.unlink(path)

    def test_too_few_rows(self):
        """Fewer rows than the size declares."""
        path = _write_temp_file("3\n1 2 3\n4 5 6\n")
        try:
            with pytest.raises(ValueError, match="rows"):
                read_puzzle_from_file(path)
        finally:
            os.unlink(path)

    def test_too_many_rows(self):
        """More rows than the size declares."""
        path = _write_temp_file("3\n1 2 3\n4 5 6\n7 8 0\n9 10 11\n")
        try:
            with pytest.raises(ValueError, match="rows"):
                read_puzzle_from_file(path)
        finally:
            os.unlink(path)

    def test_wrong_column_count(self):
        """A row with too few numbers."""
        path = _write_temp_file("3\n1 2 3\n4 5\n7 8 0\n")
        try:
            with pytest.raises(ValueError, match="numbers"):
                read_puzzle_from_file(path)
        finally:
            os.unlink(path)

    def test_duplicate_values(self):
        """Duplicate tile values."""
        path = _write_temp_file("3\n1 2 3\n4 5 6\n7 8 8\n")
        try:
            with pytest.raises(ValueError, match="[Dd]uplicate"):
                read_puzzle_from_file(path)
        finally:
            os.unlink(path)

    def test_out_of_range(self):
        """Value outside [0, N²-1]."""
        path = _write_temp_file("3\n1 2 3\n4 5 6\n7 8 99\n")
        try:
            with pytest.raises(ValueError, match="[Ii]nvalid"):
                read_puzzle_from_file(path)
        finally:
            os.unlink(path)

    def test_negative_value(self):
        """Negative numbers are invalid."""
        path = _write_temp_file("3\n-1 2 3\n4 5 6\n7 8 0\n")
        try:
            with pytest.raises(ValueError, match="[Ii]nvalid"):
                read_puzzle_from_file(path)
        finally:
            os.unlink(path)

    def test_missing_zero(self):
        """No blank tile (0) in the puzzle."""
        path = _write_temp_file("3\n1 2 3\n4 5 6\n7 8 9\n")
        try:
            with pytest.raises(ValueError):
                read_puzzle_from_file(path)
        finally:
            os.unlink(path)

    def test_size_too_small(self):
        """Size 1 should be rejected."""
        path = _write_temp_file("1\n0\n")
        try:
            with pytest.raises(ValueError, match="at least 2"):
                read_puzzle_from_file(path)
        finally:
            os.unlink(path)

    def test_nonexistent_file(self):
        """File that doesn't exist should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            read_puzzle_from_file("/tmp/this_file_does_not_exist_12345.txt")


# ================================================================== #
#  Random puzzle generation                                            #
# ================================================================== #

class TestRandomGeneration:

    @pytest.mark.parametrize("n", [3, 4, 5])
    def test_correct_dimensions(self, n):
        """Generated puzzle must be N×N."""
        puzzle = generate_random_puzzle(n)
        assert len(puzzle) == n
        assert all(len(row) == n for row in puzzle)

    @pytest.mark.parametrize("n", [3, 4, 5])
    def test_contains_all_numbers(self, n):
        """Generated puzzle must have all numbers 0..N²-1."""
        puzzle = generate_random_puzzle(n)
        flat = sorted(val for row in puzzle for val in row)
        assert flat == list(range(n * n))

    @pytest.mark.parametrize("n", [3, 4, 5])
    def test_is_solvable(self, n):
        """Generated puzzle must be solvable."""
        from solvability import is_solvable
        puzzle = generate_random_puzzle(n)
        assert is_solvable(puzzle) is True

    def test_invalid_size(self):
        """Size < 2 should raise ValueError."""
        with pytest.raises(ValueError, match="at least 2"):
            generate_random_puzzle(1)
