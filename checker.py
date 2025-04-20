# Checks if the puzzle is solvable

def is_solvable(puzzle: list[list[int]]) -> bool:
    n = len(puzzle)

    # Flatten the puzzle into a 1D list
    flat = [num for row in puzzle for num in row if num != 0]

    # Count inversions
    inversions = 0
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i] > flat[j]:
                inversions += 1

    if n % 2 == 1:
        # Odd grid: solvable if inversions is even
        return inversions % 2 == 0
    else:
        # Even grid: need to know row of blank from bottom
        for i in range(n):
            for j in range(n):
                if puzzle[i][j] == 0:
                    row_from_bottom = n - i
                    break

        return (inversions + row_from_bottom) % 2 == 0
