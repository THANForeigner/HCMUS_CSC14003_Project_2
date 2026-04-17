import heapq
import numpy as np
import time
from typing import Tuple, Optional, Dict, List, Set
from ...futoshiki_solver import FutoshikiSolver, FutoshikiState


class PureAStarSolver(FutoshikiSolver):
    def __init__(self, size: int, grid, constraint, heuristic: str = "h3"):
        super().__init__(size, grid, constraint)
        self.heuristic = heuristic
        self.nodes_expanded = 0
        self.nodes_generated = 0

    def check_constraints(self, state: FutoshikiState) -> int:
        violations = 0
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.h_constraints[i, j] != 0:
                    left = state.grid[i, j]
                    right = state.grid[i, j + 1]
                    if left != 0 and right != 0:
                        if self.h_constraints[i, j] == 1 and not (left < right):
                            violations += 1
                        elif self.h_constraints[i, j] == -1 and not (left > right):
                            violations += 1

        for i in range(self.size - 1):
            for j in range(self.size):
                if self.v_constraints[i, j] != 0:
                    top = state.grid[i, j]
                    bottom = state.grid[i + 1, j]
                    if top != 0 and bottom != 0:
                        if self.v_constraints[i, j] == 1 and not (top < bottom):
                            violations += 1
                        elif self.v_constraints[i, j] == -1 and not (top > bottom):
                            violations += 1
        return violations

    def has_conflict(self, state: FutoshikiState) -> bool:
        for i in range(self.size):
            row_vals = state.grid[i, :]
            row_vals = row_vals[row_vals != 0]
            if len(row_vals) != len(set(row_vals)): return True

            col_vals = state.grid[:, i]
            col_vals = col_vals[col_vals != 0]
            if len(col_vals) != len(set(col_vals)): return True

        return self.check_constraints(state) > 0

    def is_valid_move(self, state: FutoshikiState, row: int, col: int, value: int) -> bool:
        if value in state.grid[row, :]: return False
        if value in state.grid[:, col]: return False
        
        if col > 0 and self.h_constraints[row, col - 1] != 0:
            left_val = state.grid[row, col - 1]
            if left_val != 0:
                if self.h_constraints[row, col - 1] == 1 and not (left_val < value): return False
                if self.h_constraints[row, col - 1] == -1 and not (left_val > value): return False
                
        if col < self.size - 1 and self.h_constraints[row, col] != 0:
            right_val = state.grid[row, col + 1]
            if right_val != 0:
                if self.h_constraints[row, col] == 1 and not (value < right_val): return False
                if self.h_constraints[row, col] == -1 and not (value > right_val): return False

        if row > 0 and self.v_constraints[row - 1, col] != 0:
            top_val = state.grid[row - 1, col]
            if top_val != 0:
                if self.v_constraints[row - 1, col] == 1 and not (top_val < value): return False
                if self.v_constraints[row - 1, col] == -1 and not (top_val > value): return False
                
        if row < self.size - 1 and self.v_constraints[row, col] != 0:
            bottom_val = state.grid[row + 1, col]
            if bottom_val != 0:
                if self.v_constraints[row, col] == 1 and not (value < bottom_val): return False
                if self.v_constraints[row, col] == -1 and not (value > bottom_val): return False
                
        return True

    def h1_hamming(self, state: FutoshikiState) -> int:
        return len(state.get_blank_positions())

    def h2_inequality_violations(self, state: FutoshikiState) -> int:
        violations = 0
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.h_constraints[i, j] != 0:
                    left = state.grid[i, j]
                    right = state.grid[i, j + 1]
                    if left != 0 and right != 0:
                        if self.h_constraints[i, j] == 1 and not (left < right):
                            violations += 1
                        elif self.h_constraints[i, j] == -1 and not (left > right):
                            violations += 1

        for i in range(self.size - 1):
            for j in range(self.size):
                if self.v_constraints[i, j] != 0:
                    top = state.grid[i, j]
                    bottom = state.grid[i + 1, j]
                    if top != 0 and bottom != 0:
                        if self.v_constraints[i, j] == 1 and not (top < bottom):
                            violations += 1
                        elif self.v_constraints[i, j] == -1 and not (top > bottom):
                            violations += 1
        return violations

    def h3_mrv_domain_size(self, state: FutoshikiState) -> int:
        blanks = state.get_blank_positions()
        if not blanks: return 0

        min_domain = float("inf")
        for row, col in blanks:
            row_used = set(state.grid[row, :])
            col_used = set(state.grid[:, col])
            domain_size = self.size - len((row_used | col_used) - {0})
            if domain_size == 0: return float("inf") 
            if domain_size < min_domain:
                min_domain = domain_size

        return min_domain

    def find_best_blank(self, state: FutoshikiState) -> Tuple[int, int]:
        blanks = state.get_blank_positions()
        if not blanks: return -1, -1

        best_pos = blanks[0]
        min_domain = float("inf")

        for row, col in blanks:
            row_used = set(state.grid[row, :])
            col_used = set(state.grid[:, col])
            domain_size = self.size - len((row_used | col_used) - {0})

            if domain_size == 0:
                return -1, -1 

            if domain_size < min_domain:
                min_domain = domain_size
                best_pos = (row, col)
                if min_domain == 1:
                    break

        return best_pos

    def get_successors(self, state: FutoshikiState, use_mrv: bool = True) -> List[FutoshikiState]:
        successors = []
        blanks = state.get_blank_positions()
        if not blanks: return successors

        if use_mrv: row, col = self.find_best_blank(state)
        else: row, col = blanks[0]

        if row == -1: return successors

        for value in range(1, self.size + 1):
            if self.is_valid_move(state, row, col, value):
                new_state = state.copy()
                new_state.grid[row, col] = value
                successors.append(new_state)
                self.nodes_generated += 1

        return successors

    def solve(self) -> Optional[np.ndarray]:
        sol_list, stats, _ = self.solve_with_history()
        return np.array(sol_list) if sol_list else None

    def solve_with_history(self, max_nodes: int = 500000, stream_queue=None):
        self.nodes_expanded = 0
        self.nodes_generated = 0
        start = time.time()
        
        heuristic_map = {
            "h1": (self.h1_hamming, False),
            "h2": (self.h2_inequality_violations, True),
            "h3": (self.h3_mrv_domain_size, True),
        }
        heuristic_fn, use_mrv = heuristic_map.get(self.heuristic, (self.h3_mrv_domain_size, True))
        
        initial_state = FutoshikiState(self.grid)
        initial_state.set_constraints(self.h_constraints, self.v_constraints)
        
        if np.all(self.grid != 0):
            if self.check_constraints(initial_state) == 0:
                duration = time.time() - start
                stats = {'nodes_expanded': 0, 'nodes_generated': 1, 'time': duration}
                if stream_queue:
                    stream_queue.put(('done', self.grid.tolist(), stats))
                return (self.grid.tolist(), stats, [])
        
        if self.has_conflict(initial_state):
            duration = time.time() - start
            stats = {'nodes_expanded': 0, 'nodes_generated': 1, 'time': duration}
            if stream_queue:
                stream_queue.put(('done', None, stats))
            return (None, stats, [])
        
        open_set = []
        g_cost = 0
        h_cost = heuristic_fn(initial_state)
        f_cost = g_cost + h_cost
        
        counter = 0
        heapq.heappush(open_set, (f_cost, -g_cost, h_cost, counter, initial_state))
        
        closed_set = set()
        closed_set.add(hash(initial_state))
        
        while open_set:
            if self.nodes_expanded > max_nodes:
                break
            
            f, neg_g, h, _, current_state = heapq.heappop(open_set)
            g = -neg_g
            
            if stream_queue:
                stream_queue.put(('step', current_state.grid.tolist(), self.nodes_expanded))
            
            if len(current_state.get_blank_positions()) == 0:
                if self.check_constraints(current_state) == 0:
                    duration = time.time() - start
                    stats = {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated, 'time': duration}
                    sol_list = current_state.grid.tolist()
                    if stream_queue:
                        stream_queue.put(('done', sol_list, stats))
                    return (sol_list, stats, [])
            
            self.nodes_expanded += 1
            
            for successor in self.get_successors(current_state, use_mrv):
                state_hash = hash(successor)
                
                if state_hash not in closed_set:
                    new_g = g + 1
                    new_h = heuristic_fn(successor)
                    
                    if new_h == float("inf"):
                        continue
                    
                    new_f = new_g + new_h
                    
                    counter += 1
                    heapq.heappush(open_set, (new_f, -new_g, new_h, counter, successor))
                    closed_set.add(state_hash)
        
        duration = time.time() - start
        stats = {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated, 'time': duration}
        if stream_queue:
            stream_queue.put(('done', None, stats))
        return (None, stats, [])

    def get_stats(self) -> Dict:
        return {
            "nodes_expanded": self.nodes_expanded,
            "nodes_generated": self.nodes_generated,
            "heuristic": self.heuristic,
        }
