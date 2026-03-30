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
        
    def backtrack(self, row, col):
        if self.solution[row][col] != 0:
            self.backtrack(row, col + 1 if col + 1 < self.size else 0)
            return
        for num in range(1, self.size + 1):
            safe = self.check_contraints(row, col, num, self.constraint)
            if safe:
                self.solution[row][col] = num
                if row == self.size - 1 and col == self.size - 1:
                    return
                self.backtrack(row + (col + 1) // self.size, (col + 1) % self.size)
                if self.solution[self.size - 1][self.size - 1] != 0:
                    return
                self.solution[row][col] = 0
                
    def solve(self):
        self.backtrack(0, 0)
        return self.solution