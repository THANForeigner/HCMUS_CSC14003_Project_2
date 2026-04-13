import heapq
import numpy as np
from typing import Tuple, Optional, Dict, List, Set
from collections import deque
from ...futoshiki_solver import FutoshikiSolver, FutoshikiState


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
    
    def revise(self, x: Tuple[int, int], y: Tuple[int, int], steps: list = None) -> bool:
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
        
        if revised:
            # report revised domain removal
            if steps is not None:
                # pass list of removed values as the value field
                steps.append(('revise', x[0], x[1], list(to_remove)))
        
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
            
            if self.revise(x, y, None):
                if len(self.domains[x]) == 0:
                    return False
                
                for (xi, xj) in self.get_neighbors(*x):
                    if (xi, xj) != y:
                        queue.append(((xi, xj), x))
        
        return True


class AStarFutoshiki(FutoshikiSolver):
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
        if self.heuristic == 'h3':
            solution, _, _ = self.solve_with_ac3()
        else:
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
    
    def solve_with_ac3(self, max_nodes: int = 100000) -> Tuple[Optional[np.ndarray], int, int]:
        self.nodes_expanded = 0
        self.nodes_generated = 0
        
        ac3 = AC3Solver(self.size, self.grid, self.h_constraints, self.v_constraints)
        
        if not ac3.ac3():
            return None, 0, 1
        
        initial_domains = {k: v.copy() for k, v in ac3.domains.items()}
        initial_state = FutoshikiState(self.grid, initial_domains)
        initial_state.set_constraints(self.h_constraints, self.v_constraints)
        
        for key in list(initial_state.domains.keys()):
            if len(initial_state.domains[key]) == 1:
                val = list(initial_state.domains[key])[0]
                r, c = key
                if self.grid[r, c] == 0:
                    initial_state.grid[r, c] = val
        
        def backtrack(state: FutoshikiState, domains: Dict) -> Tuple[Optional[FutoshikiState], int, int]:
            if len(state.get_blank_positions()) == 0:
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
                    
                    if assigned and len(new_state.get_blank_positions()) == 0:
                        if self.check_constraints(new_state) == 0:
                            return new_state, self.nodes_expanded, self.nodes_generated
                    
                    result, exp, gen = backtrack(new_state, new_ac3.domains)
                    self.nodes_expanded = exp
                    self.nodes_generated = gen
                    if result is not None:
                        return result, self.nodes_expanded, self.nodes_generated
            
            return None, self.nodes_expanded, self.nodes_generated
        
        if len(initial_state.get_blank_positions()) == 0:
            if self.check_constraints(initial_state) == 0:
                return initial_state.grid, 0, 1
        
        result, exp, gen = backtrack(initial_state, ac3.domains)
        
        if result is not None:
            return result.grid, exp, gen
        return None, exp, gen

    def solve_with_history(self, max_nodes: int = 100000):
        """Run the AC3+backtrack or plain A* while recording step events.

        Returns: (solution, stats, steps)
        """
        steps = []
        # if heuristic h3 prefer AC3 variant
        if self.heuristic == 'h3':
            # instrumented version of solve_with_ac3
            self.nodes_expanded = 0
            self.nodes_generated = 0

            ac3 = AC3Solver(self.size, self.grid, self.h_constraints, self.v_constraints)
            # we won't instrument deep AC3 steps for now
            if not ac3.ac3():
                return None, {'nodes_expanded': 0, 'nodes_generated': 1}, steps

            initial_domains = {k: v.copy() for k, v in ac3.domains.items()}
            initial_state = FutoshikiState(self.grid, initial_domains)
            initial_state.set_constraints(self.h_constraints, self.v_constraints)

            for key in list(initial_state.domains.keys()):
                if len(initial_state.domains[key]) == 1:
                    val = list(initial_state.domains[key])[0]
                    r, c = key
                    if self.grid[r, c] == 0:
                        initial_state.grid[r, c] = val
                        steps.append(('assign', r, c, val))

            def backtrack(state: FutoshikiState, domains: Dict) -> Tuple[Optional[FutoshikiState], int, int]:
                if len(state.get_blank_positions()) == 0:
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
                    steps.append(('assign', row, col, value))
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
                                    steps.append(('assign', r, c, val))
                            elif len(new_state.domains[key]) == 0:
                                assigned = False
                                break

                        if assigned and len(new_state.get_blank_positions()) == 0:
                            if self.check_constraints(new_state) == 0:
                                return new_state, self.nodes_expanded, self.nodes_generated

                        result, exp, gen = backtrack(new_state, new_ac3.domains)
                        self.nodes_expanded = exp
                        self.nodes_generated = gen
                        if result is not None:
                            return result, self.nodes_expanded, self.nodes_generated

                    # backtrack from this assignment
                    steps.append(('backtrack', row, col, 0))

                return None, self.nodes_expanded, self.nodes_generated

            if len(initial_state.get_blank_positions()) == 0:
                if self.check_constraints(initial_state) == 0:
                    return initial_state.grid, {'nodes_expanded': 0, 'nodes_generated': 1}, steps

            result, exp, gen = backtrack(initial_state, ac3.domains)

            if result is not None:
                return result.grid, {'nodes_expanded': exp, 'nodes_generated': gen}, steps
            return None, {'nodes_expanded': exp, 'nodes_generated': gen}, steps
        else:
            # use A* flow instrumented
            sol, stats, steps_astar = self._solve_astar_with_steps(max_nodes=max_nodes)
            return sol, stats, steps_astar

    def _solve_astar_with_steps(self, max_nodes: int = 500000):
        # reuse code from solve_astar but collect steps
        self.nodes_expanded = 0
        self.nodes_generated = 0
        steps = []

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
                return self.grid, {'nodes_expanded': 0, 'nodes_generated': 1}, steps

        if self.has_conflict(initial_state):
            return None, {'nodes_expanded': 0, 'nodes_generated': 1}, steps

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
                return None, {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated}, steps

            f, g, h, _, current_state = heapq.heappop(open_set)
            row, col = self.find_best_blank(current_state)
            steps.append(('expand', row, col, 0))

            if len(current_state.get_blank_positions()) == 0:
                if self.check_constraints(current_state) == 0:
                    steps.append(('final', -1, -1, 0))
                    return current_state.grid, {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated}, steps

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

        return None, {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated}, steps

    def get_stats(self) -> Dict:
        return {
            'nodes_expanded': self.nodes_expanded,
            'nodes_generated': self.nodes_generated,
            'heuristic': self.heuristic
        }
