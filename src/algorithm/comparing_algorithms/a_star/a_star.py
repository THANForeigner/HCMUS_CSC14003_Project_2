import heapq
import numpy as np
from typing import Tuple, Optional, Dict, List, Set
from ...futoshiki_solver import FutoshikiSolver, FutoshikiState


class PureAStarSolver(FutoshikiSolver):
    def __init__(self, size: int, grid, constraint, heuristic: str = 'h3'):
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
            row_vals = [v for v in state.grid[i, :] if v != 0]
            if len(row_vals) != len(set(row_vals)):
                return True
            
            col_vals = [v for v in state.grid[:, i] if v != 0]
            if len(col_vals) != len(set(col_vals)):
                return True
        
        return self.check_constraints(state) > 0
    
    def h1_hamming(self, state: FutoshikiState) -> int:
        return len(state.get_blank_positions())
    
    def h2_constraint_violations(self, state: FutoshikiState) -> int:
        return self.check_constraints(state)
    
    def h3_mrv_domain_size(self, state: FutoshikiState) -> int:
        blanks = state.get_blank_positions()
        if not blanks:
            return 0
        
        min_domain = float('inf')
        for row, col in blanks:
            row_used = set(state.grid[row, :])
            col_used = set(state.grid[:, col])
            domain_size = self.size - len(row_used | col_used)
            if domain_size == 0:
                return float('inf')
            if domain_size < min_domain:
                min_domain = domain_size
        
        return min_domain
    
    def find_best_blank(self, state: FutoshikiState) -> Tuple[int, int]:
        blanks = state.get_blank_positions()
        if not blanks:
            return -1, -1
        
        best_pos = blanks[0]
        min_domain = float('inf')
        
        for row, col in blanks:
            row_used = set(state.grid[row, :])
            col_used = set(state.grid[:, col])
            domain_size = self.size - len(row_used | col_used)
            
            if domain_size < min_domain:
                min_domain = domain_size
                best_pos = (row, col)
                if min_domain == 1:
                    break
        
        return best_pos
    
    def get_successors(self, state: FutoshikiState, use_mrv: bool = True, steps: list = None) -> List[FutoshikiState]:
        successors = []
        self.nodes_expanded += 1
        
        blanks = state.get_blank_positions()
        if not blanks:
            return successors
        
        if use_mrv:
            row, col = self.find_best_blank(state)
        else:
            row, col = blanks[0]
        
        if row == -1:
            return successors

        # indicate expansion of this variable
        if steps is not None:
            steps.append(('expand', row, col, 0))
        
        row_used = set(state.grid[row, :])
        col_used = set(state.grid[:, col])
        used = row_used | col_used
        
        for value in range(1, self.size + 1):
            if value not in used:
                new_state = state.copy()
                new_state.grid[row, col] = value
                successors.append(new_state)
                self.nodes_generated += 1
                if steps is not None:
                    steps.append(('gen', row, col, value))
        
        return successors
    
    def solve(self) -> Optional[np.ndarray]:
        solution, _, _ = self.solve_astar()
        return solution
    
    def solve_astar(self, max_nodes: int = 500000) -> Tuple[Optional[np.ndarray], int, int]:
        self.nodes_expanded = 0
        self.nodes_generated = 0
        
        heuristic_map = {
            'h1': (self.h1_hamming, False),
            'h2': (self.h2_constraint_violations, True),
            'h3': (self.h3_mrv_domain_size, True)
        }
        
        heuristic_fn, use_mrv = heuristic_map[self.heuristic]
        
        initial_state = FutoshikiState(self.grid)
        initial_state.set_constraints(self.h_constraints, self.v_constraints)
        
        if np.all(self.grid != 0):
            if self.check_constraints(initial_state) == 0:
                return self.grid, 0, 1
        
        if self.has_conflict(initial_state):
            return None, 0, 1
        
        open_set = []
        g_cost = 0
        h_cost = heuristic_fn(initial_state)
        f_cost = g_cost + h_cost
        
        counter = 0
        heapq.heappush(open_set, (f_cost, g_cost, h_cost, counter, initial_state))
        
        closed_set = set()
        closed_set.add(hash(initial_state))
        
        while open_set:
            if self.nodes_expanded > max_nodes:
                return None, self.nodes_expanded, self.nodes_generated
            
            f, g, h, _, current_state = heapq.heappop(open_set)
            
            if len(current_state.get_blank_positions()) == 0:
                if self.check_constraints(current_state) == 0:
                    return current_state.grid, self.nodes_expanded, self.nodes_generated
            
            if self.has_conflict(current_state):
                continue
            
            for successor in self.get_successors(current_state, use_mrv):
                if self.has_conflict(successor):
                    continue
                
                state_hash = hash(successor)
                
                if state_hash not in closed_set:
                    new_g = g + 1
                    new_h = heuristic_fn(successor)
                    new_f = new_g + new_h
                    
                    counter += 1
                    heapq.heappush(open_set, (new_f, new_g, new_h, counter, successor))
                    closed_set.add(state_hash)
        
        return None, self.nodes_expanded, self.nodes_generated

    def solve_with_history(self, max_nodes: int = 500000, stream_queue=None):
        """Run A* while recording step events. Returns (solution, stats, steps)
        """
        # reuse existing algorithm but collect steps via get_successors
        self.nodes_expanded = 0
        self.nodes_generated = 0
        
        class StreamList(list):
            def __init__(self, q):
                self.q = q
            def append(self, item):
                if self.q:
                    self.q.put(item)
                else:
                    super().append(item)
                    
        steps = StreamList(stream_queue)

        heuristic_map = {
            'h1': (self.h1_hamming, False),
            'h2': (self.h2_constraint_violations, True),
            'h3': (self.h3_mrv_domain_size, True)
        }
        
        heuristic_fn, use_mrv = heuristic_map[self.heuristic]
        
        initial_state = FutoshikiState(self.grid)
        initial_state.set_constraints(self.h_constraints, self.v_constraints)
        
        if np.all(self.grid != 0):
            if self.check_constraints(initial_state) == 0:
                stats = {'nodes_expanded': 0, 'nodes_generated': 1}
                if stream_queue: stream_queue.put(('done', self.grid, stats))
                return self.grid, stats, steps
        
        if self.has_conflict(initial_state):
            stats = {'nodes_expanded': 0, 'nodes_generated': 1}
            if stream_queue: stream_queue.put(('done', None, stats))
            return None, stats, steps
        
        open_set = []
        g_cost = 0
        h_cost = heuristic_fn(initial_state)
        f_cost = g_cost + h_cost
        
        counter = 0
        heapq.heappush(open_set, (f_cost, g_cost, h_cost, counter, initial_state))
        
        closed_set = set()
        closed_set.add(hash(initial_state))
        
        while open_set:
            if self.nodes_expanded > max_nodes:
                stats = {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated}
                if stream_queue: stream_queue.put(('done', None, stats))
                return None, stats, steps
                
            f, g, h, _, current_state = heapq.heappop(open_set)
            
            # record expansion (use find_best_blank to indicate location)
            row, col = self.find_best_blank(current_state)
            steps.append(('expand', row, col, 0))

            if len(current_state.get_blank_positions()) == 0:
                if self.check_constraints(current_state) == 0:
                    steps.append(('final', -1, -1, 0))
                    stats = {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated}
                    if stream_queue: stream_queue.put(('done', current_state.grid, stats))
                    return current_state.grid, stats, steps
            
            if self.has_conflict(current_state):
                continue
            
            successors = self.get_successors(current_state, use_mrv, steps)
            for successor in successors:
                if self.has_conflict(successor):
                    continue
                
                state_hash = hash(successor)
                
                if state_hash not in closed_set:
                    new_g = g + 1
                    new_h = heuristic_fn(successor)
                    new_f = new_g + new_h
                    
                    counter += 1
                    heapq.heappush(open_set, (new_f, new_g, new_h, counter, successor))
                    closed_set.add(state_hash)
        
        stats = {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated}
        if stream_queue: stream_queue.put(('done', None, stats))
        return None, stats, steps

    def get_stats(self) -> Dict:
        return {
            'nodes_expanded': self.nodes_expanded,
            'nodes_generated': self.nodes_generated,
            'heuristic': self.heuristic
        }
