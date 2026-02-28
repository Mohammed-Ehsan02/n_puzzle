# ============================================================================ #
#                              N-PUZZLE SOLVER                                 #
# ============================================================================ #

PYTHON	= python3
SRC_DIR	= src
NAME	= n_puzzle

# Colors
GREEN	= \033[1;32m
CYAN	= \033[1;36m
YELLOW	= \033[1;33m
RED		= \033[1;31m
BOLD	= \033[1m
DIM		= \033[2m
RESET	= \033[0m

# Source files
SRC		= $(SRC_DIR)/main.py \
		  $(SRC_DIR)/parser.py \
		  $(SRC_DIR)/state.py \
		  $(SRC_DIR)/goal.py \
		  $(SRC_DIR)/solvability.py \
		  $(SRC_DIR)/solver/a_star.py \
		  $(SRC_DIR)/solver/heuristics.py \
		  $(SRC_DIR)/solver/utils.py

# --------------------------------------------------------------------------- #
#  Default: show help                                                          #
# --------------------------------------------------------------------------- #

all: check
	@printf "$(GREEN)✓ $(NAME) compiled successfully.$(RESET)\n"

# --------------------------------------------------------------------------- #
#  Help — shown when you type just `make` or `make help`                       #
# --------------------------------------------------------------------------- #

help:
	@printf "\n"
	@printf "$(BOLD)╔══════════════════════════════════════════════════════════╗$(RESET)\n"
	@printf "$(BOLD)║              N-PUZZLE SOLVER — COMMANDS                 ║$(RESET)\n"
	@printf "$(BOLD)╠══════════════════════════════════════════════════════════╣$(RESET)\n"
	@printf "$(BOLD)║                                                        ║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)  $(GREEN)make all$(RESET)          Compile-check all source files      $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)  $(GREEN)make solve S=<n>$(RESET)   Solve a random NxN puzzle          $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)  $(GREEN)make file F=<path>$(RESET) Solve a puzzle from a file         $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)  $(GREEN)make gen S=<size>$(RESET)  Generate a random puzzle (print)   $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)  $(GREEN)make test$(RESET)         Run all tests (pytest)              $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)  $(GREEN)make test T=<name>$(RESET) Run a specific test file           $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)  $(GREEN)make check$(RESET)        Syntax-check all .py files          $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)  $(GREEN)make clean$(RESET)        Remove __pycache__ and .pyc files   $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)  $(GREEN)make re$(RESET)           Clean + recompile                   $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)  $(GREEN)make help$(RESET)         Show this help message              $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║                                                        ║$(RESET)\n"
	@printf "$(BOLD)╠══════════════════════════════════════════════════════════╣$(RESET)\n"
	@printf "$(BOLD)║$(RESET)  $(DIM)Examples:$(RESET)                                              $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)    $(CYAN)make solve S=3$(RESET)                                      $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)    $(CYAN)make solve S=3 H=linear_conflict$(RESET)                   $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)    $(CYAN)make file F=puzzles/example_4x4.txt$(RESET)                 $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║$(RESET)    $(CYAN)make test T=goal$(RESET)                                    $(BOLD)║$(RESET)\n"
	@printf "$(BOLD)║                                                        ║$(RESET)\n"
	@printf "$(BOLD)╚══════════════════════════════════════════════════════════╝$(RESET)\n"
	@printf "\n"

# --------------------------------------------------------------------------- #
#  Core targets                                                                #
# --------------------------------------------------------------------------- #

# Default heuristic
H ?= manhattan

solve:
ifndef S
	@printf "$(RED)Error: specify a size with S=<number>$(RESET)\n"
	@printf "$(DIM)  Example: make solve S=3$(RESET)\n"
	@printf "$(DIM)  Options: H=manhattan|misplaced|linear_conflict$(RESET)\n"
	@exit 1
endif
	@printf "$(CYAN)Solving random $(S)x$(S) puzzle with $(H)...$(RESET)\n"
	@$(PYTHON) $(SRC_DIR)/main.py -s $(S) -H $(H)

file:
ifndef F
	@printf "$(RED)Error: specify a file with F=<path>$(RESET)\n"
	@printf "$(DIM)  Example: make file F=puzzles/example_4x4.txt$(RESET)\n"
	@printf "$(DIM)  Options: H=manhattan|misplaced|linear_conflict$(RESET)\n"
	@exit 1
endif
	@printf "$(CYAN)Solving puzzle from: $(F) with $(H)...$(RESET)\n"
	@$(PYTHON) $(SRC_DIR)/main.py -f $(F) -H $(H)

gen:
ifndef S
	@printf "$(RED)Error: specify a size with S=<number>$(RESET)\n"
	@printf "$(DIM)  Example: make gen S=3$(RESET)\n"
	@exit 1
endif
	@printf "$(CYAN)Generating solvable $(S)x$(S) puzzle...$(RESET)\n"
	@$(PYTHON) tools/npuzzle-gen.py $(S) -s

# --------------------------------------------------------------------------- #
#  Testing                                                                     #
# --------------------------------------------------------------------------- #

test:
ifdef T
	@printf "$(CYAN)Running tests matching: $(T)$(RESET)\n"
	@$(PYTHON) -m pytest tests/test_$(T).py -v
else
	@printf "$(CYAN)Running all tests...$(RESET)\n"
	@$(PYTHON) -m pytest tests/ -v
endif

# --------------------------------------------------------------------------- #
#  Build & clean                                                               #
# --------------------------------------------------------------------------- #

check:
	@printf "$(CYAN)Checking syntax...$(RESET)\n"
	@for f in $(SRC); do \
		$(PYTHON) -m py_compile $$f && \
		printf "  $(GREEN)✓$(RESET) $$f\n"; \
	done

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@printf "$(YELLOW)Cleaned cache files.$(RESET)\n"

re: clean all

.PHONY: all help solve file gen test check clean re
