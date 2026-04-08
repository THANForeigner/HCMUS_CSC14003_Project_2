import sys
from pathlib import Path

# Add project root to sys.path to allow running as script or importing
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from .knowledge_base import FutoshikiKB
from ..futoshiki_solver import futoshiki_solver

class fc_no_backtrack(futoshiki_solver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
        h_constraints, v_constraints = constraint[0], constraint[1]
        self.kb = FutoshikiKB.from_input(size, grid, h_constraints, v_constraints)

    def forward_chain(self, current_facts):
        """
        Thuật toán Forward Chaining thuần túy không có logic quay lui (backtracking).
        Áp dụng cơ chế suy diễn trên tập luật Horn.
        """
        fact_set = set(current_facts)
        changed = True
        
        while changed:
            changed = False
            for rule in self.kb.rules:
                premises, conclusion = rule
                
                if conclusion not in fact_set:
                    all_premises_met = True
                    for premise in premises:
                        if premise not in fact_set:
                            all_premises_met = False
                            break
                            
                    if all_premises_met:
                        fact_set.add(conclusion)
                        current_facts.append(conclusion)
                        changed = True
                        
        for fact in current_facts:
            if fact[0] == "Value":
                _, r, c, v = fact
                if ("NotValue", r, c, v) in fact_set:
                    return False, current_facts 
                    
        return True, current_facts

    def is_solved_check(self, facts):
        count = 0
        for fact in facts:
            if fact[0] == "Value":
                count += 1
        return count == self.size * self.size

    def solve(self):
        initial_facts = self.kb.facts.copy()
        
        # Chỉ chạy Forward Chaining nguyên bản
        success, final_facts = self.forward_chain(initial_facts)
        
        final_domains = [[set() for _ in range(self.size)] for _ in range(self.size)]
        self.solution = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        if success:
            for fact in final_facts:
                if fact[0] == "Value":
                    _, r, c, v = fact
                    self.solution[r][c] = v
                    final_domains[r][c].add(v)
            
            if self.is_solved_check(final_facts):
                return "Solved", final_domains
            else:
                return "Unresolved (Needs Backtracking)", final_domains
        else:
            for fact in final_facts:
                if fact[0] == "Value":
                    _, r, c, v = fact
                    final_domains[r][c].add(v)
            return "Contradiction", final_domains
