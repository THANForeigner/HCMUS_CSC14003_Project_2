from ...futoshiki_solver import futoshiki_solver

class BruteForceSolver(futoshiki_solver.FutoshikiSolver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
    
    def check_row_column(self, row, col, num):
        # Check if num is not in the current row and column
        for i in range(self.size):
            if self.grid[row][i] == num or self.grid[i][col] == num:
                return False  
        return True
    
    def check_constraints(self, row, col, num, constraint):
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
    
    def solve(self):
        from itertools import permutations
        
        all_permutations = list(permutations(range(1, self.size + 1)))
        
        for perm in all_permutations:
            if self.is_valid_solution(perm):
                self.solution = perm
                break
        
        return self.solution
    