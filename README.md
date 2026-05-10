# n_puzzle

42 project. Solves the N-puzzle ("taquin") using the A\* search algorithm.
Given an N×N sliding-tile puzzle, the program finds the shortest sequence of
moves to reach the **snail goal** (clockwise spiral from `1` with the blank
at the spiral's center).

---

## Subject Requirements

- Implement A\* (or a variant) to solve the N-puzzle
- Support arbitrary sizes (3, 4, 5, …)
- Accept both random states and input files (format defined by subject)
- Cost per move = 1
- Provide ≥ 3 admissible heuristics, Manhattan distance mandatory
- Output: time complexity, size complexity, move count, ordered solution
- Detect unsolvable puzzles and exit cleanly
- Provide a Makefile

All mandatory requirements are met. Bonus part not implemented.

---

## Project Structure

```
.
├── Makefile                  # all / clean / fclean / re + helpers
├── conftest.py               # pytest path setup
├── src/
│   ├── main.py               # CLI entry, orchestrates pipeline
│   ├── parser.py             # File parsing + random puzzle generation
│   ├── goal.py               # Snail goal generator
│   ├── solvability.py        # Permutation-parity solvability check
│   ├── state.py              # PuzzleState class (search node)
│   └── solver/
│       ├── a_star.py         # A* search algorithm
│       ├── heuristics.py     # Manhattan, misplaced, linear conflict
│       └── utils.py          # Path reconstruction, board printing
├── puzzles/                  # Sample puzzles (easy/medium/hard for 3-5)
├── tools/
│   └── npuzzle-gen.py        # Subject-provided puzzle generator
└── tests/                    # 142 pytest cases
```

---

## Build & Run

The project is pure Python 3 (stdlib only — no external dependencies).

### Makefile targets

| Target | Action |
|--------|--------|
| `make` / `make all` | Syntax-check all source files |
| `make help` | Show available commands |
| `make solve S=N [H=heuristic]` | Solve a random N×N puzzle |
| `make file F=path [H=heuristic]` | Solve a puzzle from a file |
| `make gen S=N` | Print a random solvable N×N puzzle |
| `make test` | Run all tests (pytest) |
| `make test T=name` | Run a single test file (e.g., `T=heuristics`) |
| `make check` | Syntax check only |
| `make clean` | Remove `__pycache__` and `.pyc` |
| `make fclean` | `clean` + remove pytest/mypy caches |
| `make re` | `fclean` then `all` |

### Direct invocation

```bash
python3 src/main.py -f puzzles/easy_3x3.txt
python3 src/main.py -s 3 -H linear_conflict
python3 src/main.py -f puzzles/example_4x4.txt    # unsolvable demo
```

CLI flags (`src/main.py`):

| Flag | Meaning |
|------|---------|
| `-f PATH` / `--file PATH` | Read puzzle from file |
| `-s N` / `--size N` | Generate a random solvable N×N puzzle |
| `-H NAME` / `--heuristic NAME` | `manhattan` (default), `misplaced`, `linear_conflict` |

`-f` and `-s` are mutually exclusive. One is required.

---

## Input File Format

Per subject appendix:

```
# comments allowed (full line or inline)
3
3 2 6 #inline comment ok
1 4 0
8 7 5
```

Rules:
- Lines starting with `#` are comments. Inline `#` also strips trailing comment.
- First non-comment line: integer `N` (puzzle size, ≥ 2).
- Next `N` lines: `N` whitespace-separated integers each.
- Tile values: `0..N²−1`, each appearing exactly once. `0` = blank.
- Alignment is irrelevant — `1 2 3` and `  1   2   3` both work.

Validation errors raise `ValueError` with a clear message.

---

## Output

For solvable puzzles, the program prints:

1. **Initial state** — the puzzle as given.
2. **Goal state** — the generated snail pattern.
3. **Solution sequence** — every board from initial to goal, step by step.
4. **Stats:**
   - Heuristic used
   - Number of moves (= `len(path) − 1`)
   - **Time complexity** — total states ever popped from the open set
   - **Size complexity** — `max(|open| + |closed|)` observed during the search
   - Wall-clock solve time

For unsolvable puzzles, it prints `This puzzle is unsolvable.`, displays the
input, and exits with status `1` — no crash.

---

## Algorithm: A\*

A\* finds the shortest path from start to goal using

```
f(s) = g(s) + h(s)
```

where `g(s)` is the actual cost from start to `s` and `h(s)` is a heuristic
estimate of the remaining cost. At each step, A\* expands the open-set node
with the lowest `f`. With an admissible heuristic, A\* finds an optimal
(minimum-move) solution.

This implementation follows the subject's appendix pseudocode, including the
**reopening** rule: if a cheaper path is found to a state already in the
closed set, it is moved back to the open set with the new cost. Reopening
never triggers in practice when the heuristic is consistent (Manhattan and
linear conflict both are), but the code handles it for correctness.

### Stale-entry handling

Python's `heapq` does not support a decrease-key operation. When a cheaper
path is found to a state already in the open heap, the new `PuzzleState` is
pushed and the older entry is left in place. When that older entry eventually
pops, an identity check (`open_dict[board] is current`) detects it and skips
it.

---

## Heuristics

Three admissible heuristics are provided. Admissible = never overestimates
the true cost. With an admissible `h`, A\* is guaranteed optimal.

### 1. Manhattan distance (default, mandatory)

For each non-blank tile, sum `|row − goal_row| + |col − goal_col|`.

**Admissible because** each tile must slide at least its taxicab distance to
reach its goal. Tiles can only move one orthogonal step at a time; any
interference from other tiles can only increase the real cost.

### 2. Misplaced tiles (Hamming distance)

Count the number of non-blank tiles not in their goal position.

**Admissible because** every wrong tile needs at least one move. Trivial
lower bound. Weakest of the three — A\* explores more states.

### 3. Linear conflict

```
linear_conflict = manhattan + 2 × (row_conflicts + col_conflicts)
```

A *row conflict* occurs when two tiles are both in their correct goal row,
both currently sit in row `r`, but their relative column order is reversed
versus the goal. Column conflicts are the symmetric case.

**Admissible because** Manhattan alone undercounts: each linear conflict
forces at least two extra moves (one tile must temporarily leave the row,
let the other pass, then return). These extra moves are not counted by
Manhattan, so adding 2 per conflict still yields a lower bound on true cost.

Strongest of the three — A\* explores far fewer states. On `puzzles/hard_3x3.txt`:

| Heuristic | Time complexity | Solve time |
|-----------|----------------:|----------:|
| linear_conflict | 170 states | 0.004 s |
| manhattan | ≈ 1 000 states | ≈ 0.01 s |
| misplaced | 2 915 states | 0.023 s |

All three return `moves = 20` (admissibility guarantees same optimal path
length; only exploration count differs).

---

## Data Structures

| Set | Structure | Why |
|-----|-----------|-----|
| **Open** | `heapq` min-heap on `f`, plus parallel `dict[board → state]` | Heap gives O(log n) push and pop of the lowest-`f` state. Parallel dict gives O(1) "is this board already in the open set?" lookup, which `heapq` alone cannot answer. |
| **Closed** | `dict[board → state]` | O(1) "have I already expanded this state?" — essential to avoid re-expanding billions of duplicates. |

Boards are stored as **tuples of tuples** (immutable, hashable, faster than
`copy.deepcopy`, lower memory than lists). This is what makes the dict-based
closed/open lookups possible.

These choices match the rubric's top tier (5/5) for both open- and closed-set
categories.

---

## Solvability Check

Not every permutation can reach the goal — exactly half can. The program
checks before invoking A\* (otherwise the search would explore the entire
reachable half before terminating).

### Method: permutation parity vs. blank Manhattan parity

1. Build a permutation `P` mapping each goal index to the position where that
   tile currently sits in the initial state.
2. Count inversions in `P` (pairs `i < j` with `P[i] > P[j]`).
3. Compute the blank's Manhattan distance between its initial and goal
   positions.
4. The puzzle is **solvable iff** `inversions % 2 == manhattan_distance % 2`.

### Why this works

Each legal slide move is a single transposition of the blank with one of its
neighbors, which flips permutation parity exactly once. The blank moves on a
grid; its number of moves between two positions always has the same parity
as the taxicab distance between them (any extra detours come in pairs). So
the permutation parity must match the blank's Manhattan-distance parity.

### Why a custom check (not the textbook formula)

The standard "count inversions ignoring the blank, compare with row of
blank" formula assumes the goal is `[1, 2, …, N²−1, 0]`. Our goal is the
**snail spiral**, a different permutation. This implementation builds the
actual permutation between initial and snail goal, so it works for any goal
shape.

---

## Snail Goal Generation

The snail goal is filled by walking the grid in a clockwise spiral, placing
`1, 2, …, N²−1` along the path and `0` (blank) in the final cell.

Algorithm (`src/goal.py`):

```
directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]   # right, down, left, up
row, col, dir_idx = 0, 0, 0
for num in 1 .. N²-1:
    place num, mark visited
    next = current + directions[dir_idx]
    if next is in-bounds and unvisited:
        move to next
    else:
        dir_idx = (dir_idx + 1) % 4   # turn clockwise
        move
last cell ← 0
```

For N = 3:

```
1 2 3
8 0 4
7 6 5
```

---

## Examples

```bash
# Solve a small puzzle
python3 src/main.py -f puzzles/easy_3x3.txt

# Solve a hard one with the strongest heuristic
python3 src/main.py -f puzzles/hard_3x3.txt -H linear_conflict

# Detect an unsolvable puzzle
python3 src/main.py -f puzzles/example_4x4.txt

# Generate a random solvable puzzle and solve it
python3 src/main.py -s 4 -H linear_conflict

# Use the subject-provided generator and pipe into the solver
python3 tools/npuzzle-gen.py 3 -s > /tmp/p.txt
python3 src/main.py -f /tmp/p.txt
```

---

## Tests

142 unit tests covering the parser, goal generator, solvability check,
state model, heuristics, and the A\* search itself.

```bash
make test                    # full suite
make test T=heuristics       # one file
```

---

## Defense Notes

Quick reference for peer evaluation:

- **A\* variant** — standard A\* with reopening, per subject pseudocode.
- **Why A\***: optimal with admissible heuristic, simpler than IDA\* while
  fast enough for the grading targets.
- **Open set** — `heapq` priority queue + parallel dict. Heap for O(log n)
  min retrieval; dict for O(1) membership.
- **Closed set** — `dict` keyed on board tuple. O(1) lookup avoids repeated
  expansion.
- **Heuristics** — three admissible: Manhattan (mandatory), misplaced tiles
  (weakest, useful for comparison), linear conflict (strongest).
- **Admissibility** — none of the three ever overestimate true cost, so A\*
  always returns the shortest solution.
- **Unsolvable detection** — permutation parity vs. blank Manhattan parity,
  generalized to the snail goal.
- **Solution validity** — each step in the path comes from `get_neighbors()`,
  which only swaps the blank with one orthogonal neighbor, so the path is
  guaranteed to be a valid sequence of legal moves.

---

## License

Educational project. No license attached.
