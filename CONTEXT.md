# N-Puzzle Project — Full Context & Documentation

## What is the N-Puzzle?

The N-puzzle (also called "taquin") is a sliding puzzle on an N×N grid.
- One cell is empty (represented by `0`), the rest have unique numbers `1` to `N²-1`.
- You can only move a numbered tile into the empty space (up/down/left/right, no diagonals).
- **Goal**: Reach the "snail solution" — numbers arranged in a clockwise spiral, with `0` in the last position of the spiral.

### Snail Goal Examples

```
3×3:                4×4:                    5×5:
 1  2  3             1   2   3   4           1   2   3   4   5
 8  0  4            12  13  14   5          16  17  18  19   6
 7  6  5            11   0  15   6          15  24   0  20   7
                    10   9   8   7          14  23  22  21   8
                                            13  12  11  10   9
```

The `0` (empty tile) always ends up wherever the spiral terminates (center-ish).

---

## Project Requirements (from subject.pdf)

### Mandatory
1. **A\* search algorithm** (or variant) to find the optimal solution
2. **Any puzzle size** — 3, 4, 5, 17, etc.
3. **Two input modes** — read from file OR generate random solvable puzzle
4. **Transition cost = 1** (every move costs the same)
5. **3+ heuristic functions** — Manhattan distance (mandatory) + 2 more (must be admissible)
6. **Detect unsolvable** puzzles and inform the user
7. **Output at the end**:
   - Time complexity: total states ever selected from the open set
   - Size complexity: max states in memory at once (open + closed)
   - Number of moves in the solution
   - The full sequence of states from start to goal
8. **Makefile** with standard rules

### Bonus
- Uniform-cost search: uses only `g(x)`, sets `h(x) = 0`
- Greedy search: uses only `h(x)`, sets `g(x) = 0`

---

## Directory Structure

```
n_puzzle/
├── Makefile                     # Build/run commands (make help for all commands)
├── CONTEXT.md                   # This file — full documentation
├── README.md                    # Project overview
├── en.subject.pdf               # Original subject
├── src/                         # All source code
│   ├── main.py                  # Entry point — CLI args, orchestration
│   ├── parser.py                # File parsing + random generation
│   ├── state.py                 # PuzzleState class (tuple-based, immutable)
│   ├── goal.py                  # Snail goal generation
│   ├── solvability.py           # Solvability checker (permutation parity)
│   ├── visualizer.py            # Display puzzle states (TODO)
│   └── solver/                  # Search algorithms
│       ├── __init__.py          # Package init
│       ├── a_star.py            # A* search implementation (TODO)
│       ├── heuristics.py        # Manhattan, Misplaced, Linear Conflict (TODO)
│       ├── strategy.py          # Bonus: Greedy, Uniform-cost (TODO)
│       └── utils.py             # Path reconstruction (TODO)
├── puzzles/                     # Test puzzle files
│   └── example_4x4.txt
└── tools/                       # 42-provided utilities (not our code)
    └── npuzzle-gen.py
```

---

## Algorithm: A\* Search

### How A\* Works

A\* finds the shortest path from a start state to a goal state. It combines:
- **g(x)**: the actual cost from start to state `x` (number of moves made so far)
- **h(x)**: the heuristic estimate from state `x` to the goal
- **f(x) = g(x) + h(x)**: the total estimated cost

A\* always expands the state with the **lowest f(x)** from the open set.

### Key Data Structures
- **Open set**: states discovered but not yet expanded (priority queue / min-heap via `heapq`)
- **Closed set**: states already expanded (hash set for O(1) lookup)

### Why A\* is Optimal
If the heuristic `h(x)` is **admissible** (never overestimates the true cost), A\* is guaranteed
to find the optimal (shortest) solution.

### Pseudocode (from subject)
```
open_set ← { initial_state }
closed_set ← ∅

while open_set ≠ ∅:
    current ← state with lowest f(x) in open_set

    if current == goal:
        return reconstruct_path(current)  # SUCCESS

    move current from open_set to closed_set

    for each neighbor of current:
        if neighbor not in open_set and not in closed_set:
            neighbor.g = current.g + 1
            neighbor.h = heuristic(neighbor, goal)
            neighbor.f = neighbor.g + neighbor.h
            neighbor.parent = current
            add neighbor to open_set
        else if new path to neighbor is cheaper:
            update neighbor's g, f, parent
            if neighbor was in closed_set, move it back to open_set
```

---

## Heuristics Explained

A heuristic must be **admissible** = it must NEVER overestimate the actual cost to reach the goal.

### 1. Manhattan Distance (mandatory)
For each tile, compute `|current_row - goal_row| + |current_col - goal_col|`.
Sum over all non-zero tiles. This is admissible because each tile needs at least
that many moves to reach its goal position (tiles interfere with each other,
so actual cost is >= this).

### 2. Misplaced Tiles (Hamming Distance)
Count how many tiles are NOT in their goal position (excluding 0).
Admissible because each misplaced tile needs at least 1 move to fix.
Weaker than Manhattan (less informed), so A\* will explore more states.

### 3. Linear Conflict
Manhattan distance + 2 for every pair of tiles that are in their goal row/column
but in the wrong order relative to each other. Each such conflict requires at least
2 extra moves to resolve. Still admissible. Stronger than plain Manhattan.

---

## Solvability Check (Permutation Parity)

### The Problem
Not every arrangement of tiles can reach the goal. Exactly half of all permutations
are reachable. We must detect this before running A\* (otherwise it loops forever).

### How It Works (General — works for ANY goal including snail)

The puzzle is a permutation problem. Each slide move is a transposition (swap of 2 elements).

1. **Build the permutation** that maps goal → initial state (for each goal position,
   where is that tile currently in the initial state?)
2. **Count inversions** in this permutation (all N² elements including blank).
3. **Compute Manhattan distance** of the blank from initial position to goal position.
4. **Solvable iff**: `inversions % 2 == manhattan_distance % 2`

### Why This Works
- Each slide = 1 transposition = flips permutation parity once.
- The blank travels from its initial position to its goal position. The total
  number of moves always has the same parity as the Manhattan distance
  (because the grid is bipartite — any extra moves come in pairs).
- So: permutation parity must match blank's Manhattan distance parity.

### Why the OLD approach was WRONG
The previous `checker.py` used simple inversion counting with odd/even grid rules.
That formula only works when the goal is `[1, 2, 3, ..., N²-1, 0]`.
Our snail goal has a completely different ordering, so it gave wrong answers.
The new `solvability.py` uses the general permutation parity method that works
for ANY goal state.

---

## File-by-File Breakdown

### `src/goal.py` — Snail Goal Generator
**Status**: COMPLETE, TESTED

**Purpose**: Generate the target snail (clockwise spiral) arrangement for any N×N board.

**Algorithm**: Spiral traversal using direction vectors
- Start at (0,0), move right → down → left → up (clockwise)
- Place numbers 1 through N²-1 along the spiral path
- When hitting a wall or visited cell, turn clockwise
- The final unvisited cell gets 0 (blank)

**Function**: `generate_snail_goal(n)` → returns `list[list[int]]`

---

### `src/solvability.py` — Solvability Checker
**Status**: COMPLETE, TESTED (rewritten — was `checker.py`)

**Purpose**: Determine if a puzzle can reach the snail goal state.

**Libraries**: None (pure Python)

**Functions**:
- `count_inversions(permutation)`: Counts pairs where a larger element precedes a smaller one.
- `is_solvable(puzzle)`: Builds the permutation from goal→initial, counts inversions,
  computes blank Manhattan distance, checks parity match.

**Key insight**: This works for ANY goal state, not just `[1,2,...,0]`.

---

### `src/parser.py` — Input Handling
**Status**: COMPLETE, TESTED (hardened with validations)

**Libraries**: `random` (stdlib)

**Functions**:
- `read_puzzle_from_file(file_path)`: Parses input files per subject format.
  - Strips `#` comments (full-line and inline)
  - Validates: correct row count, correct column count, numbers in range `[0, N²-1]`,
    no duplicates, exactly one blank (0).
  - Raises `ValueError` with clear messages on any issue.

- `generate_random_puzzle(n)`: Shuffles tiles, checks solvability, retries until solvable.
  ~50% of permutations are solvable, so average ~2 attempts.

- `_validate_puzzle(puzzle, size)`: Internal validation helper. Checks range, uniqueness,
  and completeness of tile values.

---

### `src/state.py` — Puzzle State Representation
**Status**: COMPLETE, TESTED (rewritten — now uses tuples)

**Libraries**: None (removed `copy` dependency)

**Class `PuzzleState`**:
- Board stored as **tuple of tuples** (immutable, hashable, fast).
  Accepts list-of-lists input, converts automatically.
- `g`: cost from start (moves so far)
- `h`: heuristic estimate to goal (set by search algorithm)
- `f = g + h`: total estimated cost
- `parent`: pointer to previous state for path reconstruction
- `blank_pos`: (row, col) of the empty tile

**Methods**:
- `get_neighbors()`: Generates 1-4 neighbor states by swapping blank with adjacent tiles.
  Uses list conversion instead of `copy.deepcopy()` (much faster).
  Sets `g = self.g + 1`, leaves `h = 0` for the search algorithm to set.
- `is_goal(goal_board)`: Compares with goal. Accepts both list and tuple formats.
- `__eq__`, `__hash__`: Based on board content (for sets/dicts)
- `__lt__`: Compares by `f` value (for `heapq` priority queue)

---

### `src/main.py` — Entry Point
**Status**: SKELETON (imports wired, `main()` is empty TODO)

Will eventually handle:
- CLI argument parsing (file path, heuristic choice, puzzle size)
- Reading puzzle from file or generating random
- Generating snail goal
- Checking solvability
- Running A\* solver
- Displaying results

---

### `src/solver/a_star.py` — A\* Search
**Status**: DOCUMENTED STUB (not yet implemented)

Will implement the core A\* loop with open/closed sets, using `heapq` for the priority queue.

---

### `src/solver/heuristics.py` — Heuristic Functions
**Status**: DOCUMENTED STUBS (not yet implemented)

Three functions to implement: `manhattan()`, `misplaced()`, `linear_conflict()`.

---

### `src/solver/utils.py` — Search Utilities
**Status**: DOCUMENTED STUB (not yet implemented)

`reconstruct_path()`: Follow parent pointers from goal to start, reverse to get solution.

---

### `src/solver/strategy.py` — Bonus Strategies
**Status**: DOCUMENTED STUBS (bonus — implement last)

`greedy_search()`: `f(x) = h(x)` only. Fast but not optimal.
`uniform_cost_search()`: `f(x) = g(x)` only. Optimal but slow.

---

### `src/visualizer.py` — Display
**Status**: EMPTY (implement after solver works)

---

### `tools/npuzzle-gen.py` — 42-Provided Generator
**Status**: COMPLETE (not our code)

Standalone CLI tool: `python3 tools/npuzzle-gen.py 3 -s` generates a solvable 3×3 puzzle.
Use `make gen S=3` as a shortcut.

---

### `puzzles/example_4x4.txt` — Test Input
A sample 4×4 puzzle file in the subject-specified format.

---

## Makefile Commands

Run `make help` to see all available commands:

| Command | Description |
|---------|-------------|
| `make all` | Syntax-check all source files |
| `make run` | Run the solver |
| `make file F=<path>` | Solve a puzzle from a file |
| `make gen S=<size>` | Generate a random solvable puzzle |
| `make check` | Syntax-check all .py files |
| `make clean` | Remove `__pycache__` and `.pyc` files |
| `make re` | Clean + recompile |
| `make help` | Show help with all commands and examples |

---

## Implementation Progress

| Step | Task | Status |
|------|------|--------|
| 1 | Directory restructure | DONE |
| 2 | Fix `state.py` (tuples) | DONE |
| 3 | Fix `solvability.py` (snail goal) | DONE |
| 4 | Harden `parser.py` (validations) | DONE |
| 5 | Document all files | DONE |
| 6 | Implement heuristics | NEXT |
| 7 | Implement A\* search | TODO |
| 8 | Implement path reconstruction | TODO |
| 9 | Wire up `main.py` | TODO |
| 10 | Implement visualizer | TODO |
| 11 | Test with various sizes | TODO |
| 12 | Bonus: greedy + uniform-cost | TODO |
