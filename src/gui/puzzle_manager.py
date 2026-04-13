import random
from typing import List, Tuple


class PuzzleManager:
    """Simple puzzle manager that can generate a fully solved Futoshiki board.

    This is intentionally lightweight for Phase 1 scaffold: it produces a
    completed Latin-square (rows and columns contain 1..n) and empty inequality
    constraints. Later phases will add constraint-aware generation and removals
    to produce playable puzzles.
    """

    def __init__(self, seed: int | None = None):
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def _is_safe(self, grid: List[List[int]], r: int, c: int, val: int) -> bool:
        n = len(grid)
        # Row check
        if val in grid[r]:
            return False
        # Column check
        for i in range(n):
            if grid[i][c] == val:
                return False
        return True

    def _solve_backtrack(self, grid: List[List[int]], r: int, c: int) -> bool:
        n = len(grid)
        if r == n:
            return True
        nr, nc = (r, c+1) if (c+1) < n else (r+1, 0)

        # If already filled (shouldn't happen for generation), skip
        if grid[r][c] != 0:
            return self._solve_backtrack(grid, nr, nc)

        # Try numbers in random order for variability
        nums = list(range(1, n+1))
        random.shuffle(nums)
        for v in nums:
            if self._is_safe(grid, r, c, v):
                grid[r][c] = v
                if self._solve_backtrack(grid, nr, nc):
                    return True
                grid[r][c] = 0
        return False

    def generate_solved(self, n: int) -> Tuple[List[List[int]], List[List[int]], List[List[int]]]:
        """Generate a solved n x n Futoshiki grid and empty constraints.

        Returns (grid, h_constraints, v_constraints)
        - grid: list of n lists each with n integers (1..n)
        - h_constraints: n x (n-1) matrix of 0 (no inequality)
        - v_constraints: (n-1) x n matrix of 0 (no inequality)
        """
        if n < 2:
            raise ValueError("Size must be >= 2")

        grid = [[0 for _ in range(n)] for _ in range(n)]
        success = self._solve_backtrack(grid, 0, 0)
        if not success:
            raise RuntimeError("Failed to generate solved grid")

        h_constraints = [[0 for _ in range(n-1)] for _ in range(n)]
        v_constraints = [[0 for _ in range(n)] for _ in range(n-1)]
        return grid, h_constraints, v_constraints
