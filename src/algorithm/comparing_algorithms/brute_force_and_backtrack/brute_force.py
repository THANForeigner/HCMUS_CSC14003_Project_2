import time
from ...futoshiki_solver import FutoshikiSolver

class BruteForceSolver(FutoshikiSolver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
        self.solution = self.grid.copy()
    
    def check_constraints(self, row, col, num):
        # Row check
        for j in range(self.size):
            if self.solution[row][j] == num: return False
        # Col check
        for i in range(self.size):
            if self.solution[i][col] == num: return False
            
        # Inequalities
        h_constraints = self.constraint[0]
        v_constraints = self.constraint[1]
        
        if col > 0 and h_constraints[row][col-1] != 0:
            prev = self.solution[row][col-1]
            if prev != 0:
                if h_constraints[row][col-1] == 1 and not (prev < num): return False
                if h_constraints[row][col-1] == -1 and not (prev > num): return False
        
        if col < self.size - 1 and h_constraints[row][col] != 0:
            nxt = self.solution[row][col+1]
            if nxt != 0:
                if h_constraints[row][col] == 1 and not (num < nxt): return False
                if h_constraints[row][col] == -1 and not (num > nxt): return False
                
        if row > 0 and v_constraints[row-1][col] != 0:
            above = self.solution[row-1][col]
            if above != 0:
                if v_constraints[row-1][col] == 1 and not (above < num): return False
                if v_constraints[row-1][col] == -1 and not (above > num): return False
                
        if row < self.size - 1 and v_constraints[row][col] != 0:
            below = self.solution[row+1][col]
            if below != 0:
                if v_constraints[row][col] == 1 and not (num < below): return False
                if v_constraints[row][col] == -1 and not (num > below): return False
        
        return True

    def _solve(self, row, col, stream_queue=None):
        if row == self.size: return True
        
        next_row = row + (col + 1) // self.size
        next_col = (col + 1) % self.size
        
        if self.grid[row][col] != 0:
            return self._solve(next_row, next_col, stream_queue)
        
        for num in range(1, self.size + 1):
            self.nodes_generated += 1
            if stream_queue: stream_queue.put(('check', row, col, num))
            
            if self.check_constraints(row, col, num):
                self.solution[row][col] = num
                self.nodes_expanded += 1
                if stream_queue: stream_queue.put(('assign', row, col, num))
                
                if self._solve(next_row, next_col, stream_queue):
                    return True
                
                self.solution[row][col] = 0
                if stream_queue: stream_queue.put(('backtrack', row, col, 0))
        return False

    def solve_with_history(self, stream_queue=None):
        self.nodes_expanded = 0
        self.nodes_generated = 0
        self.solution = self.grid.copy()
        start = time.time()
        ok = self._solve(0, 0, stream_queue)
        duration = time.time() - start
        stats = {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated, 'time': duration}
        
        sol_list = self.solution.tolist() if ok else None
        if stream_queue:
            stream_queue.put(('done', sol_list, stats))
        return (sol_list, stats, [])

    def solve(self):
        self.solution = self.grid.copy()
        if self._solve(0, 0):
            return self.solution
        return None
