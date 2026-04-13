from ...futoshiki_solver import futoshiki_solver
class BacktrackSolver(futoshiki_solver.FutoshikiSolver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
    
    def check_row_column(self, row, col, num):
        # Check if num is not in the current row and column
        for i in range(self.size):
            if self.grid[row][i] == num or self.grid[i][col] == num:
                return False
        
        # Check horizontal constraints
        if col > 0 and self.constraint[0][row][col - 1] != 0:
            if self.constraint[0][row][col - 1] == 1 and num <= self.grid[row][col - 1]:
                return False
            if self.constraint[0][row][col - 1] == -1 and num >= self.grid[row][col - 1]:
                return False
        
        if col < self.size - 1 and self.constraint[0][row][col] != 0:
            if self.constraint[0][row][col] == 1 and num >= self.grid[row][col + 1]:
                return False
            if self.constraint[0][row][col] == -1 and num <= self.grid[row][col + 1]:
                return False
        
        # Check vertical constraints
        if row > 0 and self.constraint[1][row - 1][col] != 0:
            if self.constraint[1][row - 1][col] == 1 and num <= self.grid[row - 1][col]:
                return False
            if self.constraint[1][row - 1][col] == -1 and num >= self.grid[row - 1][col]:
                return False
        
        if row < self.size - 1 and self.constraint[1][row][col] != 0:
            if self.constraint[1][row][col] == 1 and num >= self.grid[row + 1][col]:
                return False
            if self.constraint[1][row][col] == -1 and num <= self.grid[row + 1][col]:
                return False
        
        return True

    def check_contraints(self, row, col, num, constraint):
        if not self.check_row_column(row, col, num):
            return False
        h_constraints, v_constraints = constraint[0], constraint[1]
        if col > 0 and h_constraints[row][col - 1] != 0:
            if h_constraints[row][col - 1] == 1 and num <= self.grid[row][col - 1]:
                return False
            if h_constraints[row][col - 1] == -1 and num >= self.grid[row][col - 1]:
                return False
        if row < self.size - 1 and v_constraints[row][col] != 0:
            if v_constraints[row][col] == 1 and num >= self.grid[row + 1][col]:
                return False
            if v_constraints[row][col] == -1 and num <= self.grid[row + 1][col]:
                return False
        return True
        
    def backtrack(self, row, col, steps=None):
        if steps is None:
            steps = None
        if self.solution[row][col] != 0:
            next_col = col + 1 if col + 1 < self.size else 0
            next_row = row + (col + 1) // self.size
            self.backtrack(next_row, next_col, steps)
            return
        for num in range(1, self.size + 1):
            if steps is not None:
                steps.append(('check', row, col, num))
            safe = self.check_contraints(row, col, num, self.constraint)
            if safe:
                self.solution[row][col] = num
                if steps is not None:
                    steps.append(('assign', row, col, num))
                if row == self.size - 1 and col == self.size - 1:
                    return
                next_row = row + (col + 1) // self.size
                next_col = (col + 1) % self.size
                self.backtrack(next_row, next_col, steps)
                if self.solution[self.size - 1][self.size - 1] != 0:
                    return
                self.solution[row][col] = 0
                if steps is not None:
                    steps.append(('backtrack', row, col, 0))
                
    def solve_with_history(self):
        """Run the solver while recording a list of step events.

        Returns: (solution or None, stats dict, steps list)
        """
        # reset stats
        self.nodes_expanded = 0
        self.nodes_generated = 0
        start = time.time()
        steps = []
        self.backtrack(0, 0, steps)
        duration = time.time() - start
        stats = {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated, 'time': duration}
        return (self.solution, stats, steps)

    def solve(self):
        """Backward-compatible solve(): returns solution only as before."""
        return self.solution