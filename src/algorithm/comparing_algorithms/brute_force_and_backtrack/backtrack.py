import time
from ...futoshiki_solver import FutoshikiSolver

class BacktrackSolver(FutoshikiSolver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
        self.solution = self.grid.copy()
    
    def check_row_column(self, row, col, num):
        # Check if num is not in the current row and column of the solution
        for i in range(self.size):
            if self.solution[row][i] == num or self.solution[i][col] == num:
                return False
        
        # Check horizontal constraints
        h_constraints = self.constraint[0]
        if col > 0 and h_constraints[row][col - 1] != 0:
            if h_constraints[row][col - 1] == 1 and self.solution[row][col - 1] != 0 and num <= self.solution[row][col - 1]:
                return False
            if h_constraints[row][col - 1] == -1 and self.solution[row][col - 1] != 0 and num >= self.solution[row][col - 1]:
                return False
        
        if col < self.size - 1 and h_constraints[row][col] != 0:
            if h_constraints[row][col] == 1 and self.solution[row][col + 1] != 0 and num >= self.solution[row][col + 1]:
                return False
            if h_constraints[row][col] == -1 and self.solution[row][col + 1] != 0 and num <= self.solution[row][col + 1]:
                return False
        
        # Check vertical constraints
        v_constraints = self.constraint[1]
        if row > 0 and v_constraints[row - 1][col] != 0:
            if v_constraints[row - 1][col] == 1 and self.solution[row - 1][col] != 0 and num <= self.solution[row - 1][col]:
                return False
            if v_constraints[row - 1][col] == -1 and self.solution[row - 1][col] != 0 and num >= self.solution[row - 1][col]:
                return False
        
        if row < self.size - 1 and v_constraints[row][col] != 0:
            if v_constraints[row][col] == 1 and self.solution[row + 1][col] != 0 and num >= self.solution[row + 1][col]:
                return False
            if v_constraints[row][col] == -1 and self.solution[row + 1][col] != 0 and num <= self.solution[row + 1][col]:
                return False
        
        return True

    def check_constraints(self, row, col, num):
        return self.check_row_column(row, col, num)
        
    def backtrack(self, row, col, stream_queue=None):
        if row == self.size:
            return True
        
        next_row = row + (col + 1) // self.size
        next_col = (col + 1) % self.size
        
        if self.grid[row][col] != 0:
            return self.backtrack(next_row, next_col, stream_queue)
        
        for num in range(1, self.size + 1):
            self.nodes_generated += 1
            if stream_queue:
                stream_queue.put(('check', row, col, num))
            
            if self.check_constraints(row, col, num):
                self.solution[row][col] = num
                self.nodes_expanded += 1
                if stream_queue:
                    stream_queue.put(('assign', row, col, num))
                
                if self.backtrack(next_row, next_col, stream_queue):
                    return True
                
                self.solution[row][col] = 0
                if stream_queue:
                    stream_queue.put(('backtrack', row, col, 0))
        
        return False
                
    def solve_with_history(self, stream_queue=None):
        """Run the solver while recording a list of step events.
        """
        self.nodes_expanded = 0
        self.nodes_generated = 0
        self.solution = self.grid.copy()
        start = time.time()
        ok = self.backtrack(0, 0, stream_queue)
        duration = time.time() - start
        stats = {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated, 'time': duration}
        
        sol_list = self.solution.tolist() if ok else None
        if stream_queue:
            stream_queue.put(('done', sol_list, stats))
        return (sol_list, stats, [])

    def solve(self):
        """Backward-compatible solve(): returns solution only as before."""
        self.solution = self.grid.copy()
        if self.backtrack(0, 0):
            return self.solution
        return None
