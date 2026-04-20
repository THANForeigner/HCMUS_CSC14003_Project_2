import sys
import time
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

    def forward_chain(self, current_facts, stream_queue=None):
        """
        Pure Forward Chaining algorithm without backtracking logic.
        Applies inference mechanism on Horn clause set.
        """
        fact_set = set(current_facts)
        changed = True
        
        while changed:
            self.nodes_expanded += 1
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
                        if conclusion == ("Contradiction",):
                            return False, current_facts
                        fact_set.add(conclusion)
                        current_facts.append(conclusion)
                        self.nodes_generated += 1
                        if stream_queue and conclusion[0] == "Value":
                            _, r, c, v = conclusion
                            stream_queue.put(('assign', r, c, v))
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

    def solve_with_history(self, stream_queue=None):
        start = time.time()
        self.nodes_expanded = 0
        self.nodes_generated = 0
        initial_facts = self.kb.facts.copy()
        success, final_facts = self.forward_chain(initial_facts, stream_queue)
        self.solution = [[0 for _ in range(self.size)] for _ in range(self.size)]
        for fact in final_facts:
            if fact[0] == "Value":
                _, r, c, v = fact
                self.solution[r][c] = v
        stats = {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated, 'time': time.time() - start}
        if stream_queue:
            stream_queue.put(('done', self.solution, stats))
        return self.solution, stats, []

    def solve(self):
        self.nodes_expanded = 0
        self.nodes_generated = 0
        initial_facts = self.kb.facts.copy()
        
        # Run original Forward Chaining only
        success, final_facts = self.forward_chain(initial_facts)
        
        # BUG FIX: Initialize initial domain containing all values from 1 to size
        final_domains = [[set(range(1, self.size + 1)) for _ in range(self.size)] for _ in range(self.size)]
        self.solution = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        # Update Domain based on obtained facts
        for fact in final_facts:
            #breakpoint()
            if fact[0] == "NotValue":
                _, r, c, v = fact
                # Remove value v from the domain of cell (r, c)
                if v in final_domains[r][c]:
                    final_domains[r][c].remove(v)
            elif fact[0] == "Value":
                _, r, c, v = fact
                self.solution[r][c] = v
                # If a Value is certain, the domain contains only that value
                final_domains[r][c] = {v}

        if success:
            if self.is_solved_check(final_facts):
                return "Solved", final_domains
            else:
                return "Unresolved (Needs Backtracking)", final_domains
        else:
            return "Contradiction", final_domains
