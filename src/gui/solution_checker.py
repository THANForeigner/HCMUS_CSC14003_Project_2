from z3 import Int, Solver, Distinct, And, Or
from typing import List, Tuple


def _make_vars(n: int):
    return [[Int(f"c_{r}_{c}") for c in range(n)] for r in range(n)]


def _add_basic_constraints(solver: Solver, vars_grid, n: int, initial_grid: List[List[int]]):
    # Domain constraints and fixed cells
    for r in range(n):
        for c in range(n):
            solver.add(vars_grid[r][c] >= 1, vars_grid[r][c] <= n)
            if initial_grid[r][c] != 0:
                solver.add(vars_grid[r][c] == initial_grid[r][c])

    # Row and column distinctness
    for r in range(n):
        solver.add(Distinct([vars_grid[r][c] for c in range(n)]))
    for c in range(n):
        solver.add(Distinct([vars_grid[r][c] for r in range(n)]))


def _add_inequalities(solver: Solver, vars_grid, h_constraints: List[List[int]], v_constraints: List[List[int]]):
    n = len(vars_grid)
    # Horizontal: h_constraints is n x (n-1)
    for r in range(n):
        for c in range(n - 1):
            v = h_constraints[r][c]
            if v == 1:
                solver.add(vars_grid[r][c] < vars_grid[r][c + 1])
            elif v == -1:
                solver.add(vars_grid[r][c] > vars_grid[r][c + 1])
    # Vertical: v_constraints is (n-1) x n
    for r in range(n - 1):
        for c in range(n):
            v = v_constraints[r][c]
            if v == 1:
                solver.add(vars_grid[r][c] < vars_grid[r + 1][c])
            elif v == -1:
                solver.add(vars_grid[r][c] > vars_grid[r + 1][c])


def is_solvable(initial_grid: List[List[int]], h_constraints: List[List[int]], v_constraints: List[List[int]]) -> bool:
    n = len(initial_grid)
    vars_grid = _make_vars(n)
    s = Solver()
    _add_basic_constraints(s, vars_grid, n, initial_grid)
    _add_inequalities(s, vars_grid, h_constraints, v_constraints)
    return s.check().r == 1


def is_unique_solution(initial_grid: List[List[int]], h_constraints: List[List[int]], v_constraints: List[List[int]]) -> bool:
    """Return True if the puzzle has exactly one solution."""
    n = len(initial_grid)
    vars_grid = _make_vars(n)
    s = Solver()
    _add_basic_constraints(s, vars_grid, n, initial_grid)
    _add_inequalities(s, vars_grid, h_constraints, v_constraints)

    if s.check().r != 1:
        return False
    model = s.model()
    # Build blocking clause: at least one cell differs from model
    diffs = []
    for r in range(n):
        for c in range(n):
            val = model[vars_grid[r][c]].as_long()
            diffs.append(vars_grid[r][c] != val)
    s.add(Or(*diffs))
    return s.check().r == 0


def validate_complete_solution(candidate_grid: List[List[int]], h_constraints: List[List[int]], v_constraints: List[List[int]]) -> bool:
    """Validate a full candidate grid against Futoshiki rules and inequalities."""
    n = len(candidate_grid)
    # Basic domain and uniqueness checks
    for r in range(n):
        row = candidate_grid[r]
        if sorted(row) != list(range(1, n + 1)):
            return False
    for c in range(n):
        col = [candidate_grid[r][c] for r in range(n)]
        if sorted(col) != list(range(1, n + 1)):
            return False
    # Inequalities
    for r in range(n):
        for c in range(n - 1):
            h = h_constraints[r][c]
            if h == 1 and not (candidate_grid[r][c] < candidate_grid[r][c + 1]):
                return False
            if h == -1 and not (candidate_grid[r][c] > candidate_grid[r][c + 1]):
                return False
    for r in range(n - 1):
        for c in range(n):
            v = v_constraints[r][c]
            if v == 1 and not (candidate_grid[r][c] < candidate_grid[r + 1][c]):
                return False
            if v == -1 and not (candidate_grid[r][c] > candidate_grid[r + 1][c]):
                return False
    return True
