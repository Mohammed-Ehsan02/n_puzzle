# ==========================================================================  #
#  main.py — Entry Point of the N-Puzzle Solver                               #
# ==========================================================================  #
#                                                                              #
#  This is where everything comes together:                                    #
#    1. Parse CLI arguments (file path, puzzle size, heuristic choice)         #
#    2. Read puzzle from file OR generate a random solvable one                #
#    3. Generate the snail goal for that puzzle size                            #
#    4. Check if the puzzle is solvable                                        #
#    5. Run A* with the chosen heuristic                                       #
#    6. Display: solution path, move count, and complexity stats               #
#                                                                              #
#  USAGE:                                                                      #
#    python3 src/main.py -f puzzles/example_4x4.txt                            #
#    python3 src/main.py -s 3                                                  #
#    python3 src/main.py -f puzzle.txt -H linear_conflict                      #
#                                                                              #
#  LIBRARY:                                                                    #
#    - argparse (stdlib): CLI argument parsing                                 #
#    - sys (stdlib): exit codes                                                #
#    - time (stdlib): measuring solve duration                                 #
# ==========================================================================  #

import argparse
import sys
import time

from goal import generate_snail_goal
from parser import read_puzzle_from_file, generate_random_puzzle
from solvability import is_solvable
from state import PuzzleState
from solver.a_star import a_star
from solver.heuristics import manhattan, misplaced, linear_conflict
from solver.utils import print_board

# Map of heuristic names → functions, so user can choose by name
HEURISTICS = {
    "manhattan": manhattan,
    "misplaced": misplaced,
    "linear_conflict": linear_conflict,
}


def parse_args():
    """
    Parse command-line arguments.

    Two input modes (mutually exclusive):
      -f / --file   : path to a puzzle file
      -s / --size   : generate a random solvable NxN puzzle

    Heuristic choice:
      -H / --heuristic : one of manhattan, misplaced, linear_conflict
                         Defaults to manhattan.

    Returns:
        argparse.Namespace with attributes: file, size, heuristic
    """
    parser = argparse.ArgumentParser(
        description="N-Puzzle Solver — solves sliding puzzles using A* search.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python3 src/main.py -f puzzles/example_4x4.txt\n"
            "  python3 src/main.py -s 3\n"
            "  python3 src/main.py -s 3 -H linear_conflict\n"
        ),
    )

    # Input source: file or random (at least one required)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", "--file",
        type=str,
        help="Path to a puzzle input file",
    )
    group.add_argument(
        "-s", "--size",
        type=int,
        help="Generate a random solvable NxN puzzle",
    )

    # Heuristic choice
    parser.add_argument(
        "-H", "--heuristic",
        type=str,
        choices=HEURISTICS.keys(),
        default="manhattan",
        help="Heuristic function (default: manhattan)",
    )

    return parser.parse_args()


def display_solution(puzzle, goal, path, stats, heuristic_name, elapsed):
    """
    Print the solution in the format required by the subject:
      - The ordered sequence of states from initial to goal
      - Number of moves
      - Time complexity (states opened)
      - Size complexity (max states in memory)

    Args:
        puzzle:         The initial puzzle board (list of lists).
        goal:           The goal board (list of lists).
        path:           List of PuzzleStates from start to goal.
        stats:          Dict with time_complexity, size_complexity, moves.
        heuristic_name: Name of the heuristic used.
        elapsed:        Time taken to solve in seconds.
    """
    n = len(puzzle)

    print("=" * 40)
    print("         N-PUZZLE SOLVER")
    print("=" * 40)
    print()

    # Initial state
    print("Initial state:")
    print(print_board(puzzle, n))
    print()

    # Goal state
    print("Goal state (snail):")
    print(print_board(goal, n))
    print()

    # Solution sequence
    print("-" * 40)
    print("Solution sequence:")
    print("-" * 40)
    for i, state in enumerate(path):
        if i == 0:
            print(f"\nStep {i} (initial):")
        else:
            print(f"\nStep {i}:")
        print(print_board(state.board, n))
    print()

    # Statistics
    print("=" * 40)
    print("         RESULTS")
    print("=" * 40)
    print(f"  Heuristic:        {heuristic_name}")
    print(f"  Moves:            {stats['moves']}")
    print(f"  Time complexity:  {stats['time_complexity']} states")
    print(f"  Size complexity:  {stats['size_complexity']} states")
    print(f"  Solved in:        {elapsed:.4f} seconds")
    print("=" * 40)


def main():
    args = parse_args()

    # ------------------------------------------------------------------
    # Step 1: Get the puzzle (from file or random)
    # ------------------------------------------------------------------
    if args.file:
        try:
            puzzle = read_puzzle_from_file(args.file)
        except FileNotFoundError:
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: invalid puzzle file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if args.size < 2:
            print("Error: puzzle size must be at least 2.", file=sys.stderr)
            sys.exit(1)
        puzzle = generate_random_puzzle(args.size)
        print(f"Generated random solvable {args.size}x{args.size} puzzle.\n")

    n = len(puzzle)

    # ------------------------------------------------------------------
    # Step 2: Generate the snail goal
    # ------------------------------------------------------------------
    goal = generate_snail_goal(n)

    # ------------------------------------------------------------------
    # Step 3: Check solvability
    # ------------------------------------------------------------------
    if not is_solvable(puzzle):
        print("This puzzle is unsolvable.")
        print()
        print("Initial state:")
        print(print_board(puzzle, n))
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 4: Run A* search
    # ------------------------------------------------------------------
    heuristic_name = args.heuristic
    heuristic_func = HEURISTICS[heuristic_name]
    initial_state = PuzzleState(puzzle)

    start_time = time.time()
    path, stats = a_star(initial_state, goal, heuristic_func)
    elapsed = time.time() - start_time

    if path is None:
        # Should never happen for solvable puzzles, but just in case
        print("Error: A* could not find a solution.", file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 5: Display solution
    # ------------------------------------------------------------------
    display_solution(puzzle, goal, path, stats, heuristic_name, elapsed)


if __name__ == "__main__":
    main()
