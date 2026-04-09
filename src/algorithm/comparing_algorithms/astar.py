import heapq
import numpy as np
from typing import Tuple, List, Optional, Set, Dict
from collections import deque


class FutoshikiState:
    def __init__(self, grid: np.ndarray, domains: Optional[Dict[Tuple[int, int], Set[int]]] = None):
        self.grid = grid.copy()
        self.size = len(grid)
        self.h_constraints = None
        self.v_constraints = None
        
        if domains is not None:
            self.domains = {k: v.copy() for k, v in domains.items()}
        else:
            self.domains = {}
            for i in range(self.size):
                for j in range(self.size):
                    if grid[i, j] == 0:
                        self.domains[(i, j)] = set(range(1, self.size + 1))
                    else:
                        self.domains[(i, j)] = {grid[i, j]}
    
    def set_constraints(self, h_constraints: np.ndarray, v_constraints: np.ndarray):
        self.h_constraints = h_constraints.copy()
        self.v_constraints = v_constraints.copy()
    
    def __hash__(self):
        return hash(tuple(self.grid.flatten()))
    
    def __eq__(self, other):
        return np.array_equal(self.grid, other.grid)
    
    def copy(self):
        new_state = FutoshikiState(self.grid, self.domains)
        if self.h_constraints is not None:
            new_state.set_constraints(self.h_constraints, self.v_constraints)
        return new_state
    
    def get_blank_positions(self) -> List[Tuple[int, int]]:
        return [(i, j) for i in range(self.size) 
                for j in range(self.size) if self.grid[i, j] == 0]
    
    def is_assigned(self, row: int, col: int) -> bool:
        return self.grid[row, col] != 0


class AC3Solver:
    def __init__(self, size: int, grid: np.ndarray, h_constraints: np.ndarray, v_constraints: np.ndarray):
        self.size = size
        self.grid = np.array(grid)
        self.h_constraints = np.array(h_constraints)
        self.v_constraints = np.array(v_constraints)
        self.domains: Dict[Tuple[int, int], Set[int]] = {}
        self._init_domains()
    
    def _init_domains(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i, j] != 0:
                    self.domains[(i, j)] = {self.grid[i, j]}
                else:
                    self.domains[(i, j)] = set(range(1, self.size + 1))
                    row_used = set(self.grid[i, :])
                    col_used = set(self.grid[:, j])
                    self.domains[(i, j)] -= row_used | col_used
    
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        neighbors = []
        for j in range(self.size):
            if j != col:
                neighbors.append((row, j))
        for i in range(self.size):
            if i != row:
                neighbors.append((i, col))
        
        if col > 0 and self.h_constraints[row, col - 1] != 0:
            neighbors.append((row, col - 1))
        if col < self.size - 1 and self.h_constraints[row, col] != 0:
            neighbors.append((row, col + 1))
        if row > 0 and self.v_constraints[row - 1, col] != 0:
            neighbors.append((row - 1, col))
        if row < self.size - 1 and self.v_constraints[row, col] != 0:
            neighbors.append((row + 1, col))
        
        return neighbors
    
    def revise(self, x: Tuple[int, int], y: Tuple[int, int]) -> bool:
        revised = False
        constraint_type = self._get_constraint(x, y)
        
        if constraint_type == 0:
            return False
        
        to_remove = set()
        for val_x in list(self.domains[x]):
            valid = False
            for val_y in self.domains[y]:
                if constraint_type == 1 and val_x < val_y:
                    valid = True
                    break
                elif constraint_type == -1 and val_x > val_y:
                    valid = True
                    break
                elif constraint_type == 2 and val_x != val_y:
                    valid = True
                    break
            
            if not valid:
                to_remove.add(val_x)
                revised = True
        
        self.domains[x] -= to_remove
        return revised
    
    def _get_constraint(self, x: Tuple[int, int], y: Tuple[int, int]) -> int:
        if x[0] == y[0]:
            row, c1, c2 = x[0], x[1], y[1]
            if c1 > c2:
                c1, c2 = c2, c1
                if self.h_constraints[row, c1] != 0:
                    constraint = self.h_constraints[row, c1]
                    if x[1] > y[1]:
                        constraint = -constraint
                    return constraint
            if self.h_constraints[row, c1] != 0:
                constraint = self.h_constraints[row, c1]
                if x[1] > y[1]:
                    constraint = -constraint
                return constraint
        elif x[1] == y[1]:
            col, r1, r2 = x[1], x[0], y[0]
            if r1 > r2:
                r1, r2 = r2, r1
                if self.v_constraints[r1, col] != 0:
                    constraint = self.v_constraints[r1, col]
                    if x[0] > y[0]:
                        constraint = -constraint
                    return constraint
            if self.v_constraints[r1, col] != 0:
                constraint = self.v_constraints[r1, col]
                if x[0] > y[0]:
                    constraint = -constraint
                return constraint
        
        if self.grid[x[0], x[1]] == 0 and self.grid[y[0], y[1]] == 0:
            return 2
        return 0
    
    def ac3(self) -> bool:
        queue = deque()
        
        for i in range(self.size):
            for j in range(self.size):
                for ni, nj in self.get_neighbors(i, j):
                    queue.append(((i, j), (ni, nj)))
        
        while queue:
            (x, y) = queue.popleft()
            
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                
                for (xi, xj) in self.get_neighbors(*x):
                    if (xi, xj) != y:
                        queue.append(((xi, xj), x))
        
        return True


class AStarFutoshiki:
    def __init__(self, size: int, grid: np.ndarray, constraints: Tuple[np.ndarray, np.ndarray]):
        self.size = size
        self.initial_grid = np.array(grid)
        self.h_constraints = np.array(constraints[0])
        self.v_constraints = np.array(constraints[1])
        self.nodes_expanded = 0
        self.nodes_generated = 0
        
    def is_goal(self, state: FutoshikiState) -> bool:
        return len(state.get_blank_positions()) == 0
    
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
    
    def get_successors(self, state: FutoshikiState, use_mrv: bool = True) -> List[FutoshikiState]:
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
        
        row_used = set(state.grid[row, :])
        col_used = set(state.grid[:, col])
        used = row_used | col_used
        
        for value in range(1, self.size + 1):
            if value not in used:
                new_state = state.copy()
                new_state.grid[row, col] = value
                successors.append(new_state)
                self.nodes_generated += 1
        
        return successors
    
    def solve(self, heuristic: str = 'h1', max_nodes: int = 500000) -> Tuple[Optional[np.ndarray], int, int]:
        self.nodes_expanded = 0
        self.nodes_generated = 0
        
        heuristic_map = {
            'h1': (self.h1_hamming, False),
            'h2': (self.h2_constraint_violations, True),
            'h3': (self.h3_mrv_domain_size, True)
        }
        
        if heuristic not in heuristic_map:
            raise ValueError(f"Unknown heuristic: {heuristic}")
        
        heuristic_fn, use_mrv = heuristic_map[heuristic]
        
        initial_state = FutoshikiState(self.initial_grid)
        initial_state.set_constraints(self.h_constraints, self.v_constraints)
        
        if np.all(self.initial_grid != 0):
            if self.check_constraints(initial_state) == 0:
                return self.initial_grid, 0, 1
        
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
            
            if self.is_goal(current_state):
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
    
    def solve_with_ac3(self, heuristic: str = 'h3', max_nodes: int = 100000) -> Tuple[Optional[np.ndarray], int, int]:
        self.nodes_expanded = 0
        self.nodes_generated = 0
        
        ac3 = AC3Solver(self.size, self.initial_grid, self.h_constraints, self.v_constraints)
        
        if not ac3.ac3():
            return None, 0, 1
        
        initial_domains = {k: v.copy() for k, v in ac3.domains.items()}
        initial_state = FutoshikiState(self.initial_grid, initial_domains)
        initial_state.set_constraints(self.h_constraints, self.v_constraints)
        
        for key in list(initial_state.domains.keys()):
            if len(initial_state.domains[key]) == 1:
                val = list(initial_state.domains[key])[0]
                r, c = key
                if self.initial_grid[r, c] == 0:
                    initial_state.grid[r, c] = val
        
        def backtrack(state: FutoshikiState, domains: Dict) -> Tuple[Optional[FutoshikiState], int, int]:
            if self.is_goal(state):
                return state, self.nodes_expanded, self.nodes_generated
            
            self.nodes_expanded += 1
            
            if self.nodes_expanded > max_nodes:
                return None, self.nodes_expanded, self.nodes_generated
            
            row, col = self.find_best_blank(state)
            if row == -1:
                return None, self.nodes_expanded, self.nodes_generated
            
            row_used = set(state.grid[row, :])
            col_used = set(state.grid[:, col])
            used = row_used | col_used
            
            values_to_try = [v for v in range(1, self.size + 1) if v not in used]
            
            for value in values_to_try:
                self.nodes_generated += 1
                new_state = state.copy()
                new_state.grid[row, col] = value
                new_domains = {k: v.copy() for k, v in domains.items()}
                new_domains[(row, col)] = {value}
                
                new_ac3 = AC3Solver(self.size, new_state.grid, self.h_constraints, self.v_constraints)
                new_ac3.domains = new_domains
                
                if new_ac3.ac3():
                    new_state.domains = new_ac3.domains
                    
                    assigned = True
                    for key in new_state.domains:
                        if len(new_state.domains[key]) == 1:
                            val = list(new_state.domains[key])[0]
                            r, c = key
                            if new_state.grid[r, c] == 0:
                                new_state.grid[r, c] = val
                        elif len(new_state.domains[key]) == 0:
                            assigned = False
                            break
                    
                    if assigned and self.is_goal(new_state):
                        if self.check_constraints(new_state) == 0:
                            return new_state, self.nodes_expanded, self.nodes_generated
                    
                    result, exp, gen = backtrack(new_state, new_ac3.domains)
                    self.nodes_expanded = exp
                    self.nodes_generated = gen
                    if result is not None:
                        return result, self.nodes_expanded, self.nodes_generated
            
            return None, self.nodes_expanded, self.nodes_generated
        
        if self.is_goal(initial_state):
            if self.check_constraints(initial_state) == 0:
                return initial_state.grid, 0, 1
        
        result, exp, gen = backtrack(initial_state, ac3.domains)
        
        if result is not None:
            return result.grid, exp, gen
        return None, exp, gen
    
    def solve_all_heuristics(self) -> dict:
        results = {}
        for h in ['h1', 'h2', 'h3']:
            if h == 'h3':
                solution, expanded, generated = self.solve_with_ac3(h)
            else:
                solution, expanded, generated = self.solve(h)
            results[h] = {
                'solution': solution,
                'nodes_expanded': expanded,
                'nodes_generated': generated,
                'solved': solution is not None
            }
        return results


def solve_futoshiki_astar(size: int, grid: np.ndarray, 
                          constraints: Tuple[np.ndarray, np.ndarray],
                          heuristic: str = 'h1') -> Optional[np.ndarray]:
    solver = AStarFutoshiki(size, grid, constraints)
    if heuristic == 'h3':
        solution, _, _ = solver.solve_with_ac3(heuristic)
    else:
        solution, _, _ = solver.solve(heuristic)
    return solution
