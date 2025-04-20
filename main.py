# Entry point of the N-Puzzle Solver
from goal_generator import generate_snail_goal
from parser import read_puzzle_from_file
from checker import is_solvable

import pprint

def main():
    # TODO: Parse CLI args
    # TODO: Read puzzle (file or random)
    # TODO: Generate goal state
    # TODO: Check solvability
    # TODO: Run solver
    # TODO: Display output
    pass

if __name__ == "__main__":
    main()


puzzle = read_puzzle_from_file("example_4x4.txt")
print("Solvable?" , is_solvable(puzzle))

# pprint.pprint(generate_snail_goal(4))
