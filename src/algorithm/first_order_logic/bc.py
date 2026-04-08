import sys
from pathlib import Path
import copy

# Add project root to sys.path to allow running as script or importing
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from ..futoshiki_solver import futoshiki_solver
from .kb import FutoshikiKB

class backward_chaining(futoshiki_solver):
    def __init__(self, size, grid, constraint):
        futoshiki_solver.__init__(self, size, grid, constraint)
        h_constraints, v_constraints = constraint[0], constraint[1]
        self.kb = FutoshikiKB.from_input(size, grid, h_constraints, v_constraints)

    def is_valid_assignment(self,r, c, val):
        for k in range(self.kb.n):
            # Check row
            if k != c and len(self.kb.domains[r][k]) == 1:
                if list(self.kb.domains[r][k])[0] == val:
                    return False
            # Check column
            if k != r and len(self.kb.domains[k][c]) == 1:
                if list(self.kb.domains[k][c])[0] == val:
                    return False

        # Check A5 & A6 
        if (r, c) in self.kb.less_h: 
            if len(self.kb.domains[r][c+1]) == 1 and not (val < list(self.kb.domains[r][c+1])[0]):
                return False
        if (r, c-1) in self.kb.less_h: 
            if len(self.kb.domains[r][c-1]) == 1 and not (list(self.kb.domains[r][c-1])[0] < val):
                return False

        if (r, c) in self.kb.greater_h: 
            if len(self.kb.domains[r][c+1]) == 1 and not (val > list(self.kb.domains[r][c+1])[0]):
                return False
        if (r, c-1) in self.kb.greater_h: 
            if len(self.kb.domains[r][c-1]) == 1 and not (list(self.kb.domains[r][c-1])[0] > val):
                return False

        # Check A7 & A8 
        if (r, c) in self.kb.less_v: 
            if len(self.kb.domains[r+1][c]) == 1 and not (val < list(self.kb.domains[r+1][c])[0]):
                return False
        if (r-1, c) in self.kb.less_v: 
            if len(self.kb.domains[r-1][c]) == 1 and not (list(self.kb.domains[r-1][c])[0] < val):
                return False

        if (r, c) in self.kb.greater_v:
            if len(self.kb.domains[r+1][c]) == 1 and not (val > list(self.kb.domains[r+1][c])[0]):
                return False
        if (r-1, c) in self.kb.greater_v:
            if len(self.kb.domains[r-1][c]) == 1 and not (list(self.kb.domains[r-1][c])[0] > val):
                return False

        return True

    def backward_chain(self):
        min_len = self.kb.n + 1
        min_cell = None
        for i in range(self.kb.n):
            for j in range(self.kb.n):
                if len(self.kb.domains[i][j]) > 1 and len(self.kb.domains[i][j]) < min_len:
                    min_len = len(self.kb.domains[i][j])
                    min_cell = (i, j)
                    break
            if min_cell:
                break
                    
        if min_cell is None:
            return True
            
        r, c = min_cell
        domain_values = list(self.kb.domains[r][c])
        saved_domains = copy.deepcopy(self.kb.domains)
        
        # Try guessing numbers and verifying the path
        for val in domain_values:
            if self.is_valid_assignment(r, c, val):
                saved_domain = self.kb.domains[r][c]
                self.kb.domains[r][c] = {val}
                if self.backward_chain():
                    return True
                self.kb.domains[r][c] = saved_domain
            
        return False

    def solve(self):
        # Enforce initial grid clues ONCE when solving begins
        self.kb.apply_a9_enforce_clues()
        
        success = self.backward_chain()
        if success:
            self.solution = [[list(self.kb.domains[i][j])[0] for j in range(self.size)] for i in range(self.size)]
            return "Solved", self.kb.domains
        else:
            return "Contradiction", self.kb.domains
