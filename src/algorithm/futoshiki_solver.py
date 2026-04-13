import numpy as np
from typing import Tuple, Optional, Dict, List, Set


class FutoshikiSolver:
    def __init__(self, size: int, grid, constraint):
        self.size = size
        self.grid = np.array(grid)
        self.h_constraints = np.array(constraint[0])
        self.v_constraints = np.array(constraint[1])
        self.solution = None
        self.nodes_expanded = 0
        self.nodes_generated = 0
        
    def solve(self) -> Optional[np.ndarray]:
        raise NotImplementedError
    
    def get_stats(self) -> Dict:
        return {
            'nodes_expanded': self.nodes_expanded,
            'nodes_generated': self.nodes_generated
        }


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


# Alias for backward compatibility with FOL algorithms
futoshiki_solver = FutoshikiSolver
