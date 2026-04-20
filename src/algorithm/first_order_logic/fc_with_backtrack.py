import sys
import time
from pathlib import Path
import copy

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from .knowledge_base import FutoshikiKB
from ..futoshiki_solver import futoshiki_solver

class forward_chaining(futoshiki_solver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
        h_constraints, v_constraints = constraint[0], constraint[1]
        self.kb = FutoshikiKB.from_input(size, grid, h_constraints, v_constraints)
        self.solved = False

    def forward_chain(self, current_facts, stream_queue=None):
        """
        Forward Chaining algorithm applies inference mechanism on Horn clause set.
        Uses fact_set (Python set) to achieve O(1) lookup, instead of iterating through a List.
        Loop continues until no new facts are derived from the ruleset.
        """
        fact_set = set(current_facts)
        changed = True
        
        while changed:
            self.nodes_expanded += 1
            changed = False
            for rule in self.kb.rules:
                premises, conclusion = rule
                
                # Quick check if conclusion already exists
                if conclusion not in fact_set:
                    # Check if ALL conditions are satisfied 
                    all_premises_met = True
                    for premise in premises:
                        if premise not in fact_set:
                            all_premises_met = False
                            break
                            
                    # If all premises are true -> Derive the consequence
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
                        
        # Check for any logical contradictions
        for fact in current_facts:
            if fact[0] == "Value":
                _, r, c, v = fact
                if ("NotValue", r, c, v) in fact_set:
                    return False, current_facts # Logical conflict occurred!
                    
        return True, current_facts

    def is_solved_check(self, facts):
        count = 0
        for fact in facts:
            if fact[0] == "Value":
                count += 1
        # Puzzle successfully solved when the number of completed marks equals total cells (N x N)
        return count == self.size * self.size

    def backtrack(self, current_facts, stream_queue=None):
        self.nodes_expanded += 1
        # Perform Forward Chaining inference on current state
        success, derived_facts = self.forward_chain(current_facts, stream_queue)
        if not success:
            return False, derived_facts
            
        if self.is_solved_check(derived_facts):
            return True, derived_facts
            
        # Map cells that have been assigned values
        fact_set = set(derived_facts)
        assigned_cells = set()
        for fact in derived_facts:
            if fact[0] == "Value":
                _, r, c, v = fact
                assigned_cells.add((r, c))
                
        # Select a target cell (Minimum Remaining Values - MRV)
        best_cell = None
        min_options = float('inf')
        valid_options_for_best = []
        
        for r in range(self.size):
            for c in range(self.size):
                if (r, c) not in assigned_cells:
                    options = []
                    for v in range(1, self.size + 1):
                        # A valid possibility is if the rule doesn't forbid it (no NotValue yet)
                        if ("NotValue", r, c, v) not in fact_set:
                            options.append(v)
                    
                    if len(options) == 0:
                        return False, derived_facts # This cell has no possibilities due to contradiction
                        
                    if len(options) < min_options:
                        min_options = len(options)
                        best_cell = (r, c)
                        valid_options_for_best = options

        if not best_cell:
            return False, derived_facts

        r, c = best_cell
        
        # Guess and run a new branch based on FC 
        for val in valid_options_for_best:
            # COPY the environment variables so Backtracking doesn't ruin the current state of DFS
            if stream_queue:
                stream_queue.put(('assign', r, c, val))
            new_facts = derived_facts.copy() 
            new_facts.append(("Value", r, c, val))
            self.nodes_generated += 1
            
            success, final_facts = self.backtrack(new_facts, stream_queue)
            if success:
                return True, final_facts
            
            if stream_queue:
                stream_queue.put(('backtrack', r, c, 0))
                
        return False, derived_facts

    def solve_with_history(self, stream_queue=None):
        import time
        start = time.time()
        self.nodes_expanded = 0
        self.nodes_generated = 0
        initial_facts = self.kb.facts.copy()
        success, final_facts = self.backtrack(initial_facts, stream_queue)
        self.solution = [[0 for _ in range(self.size)] for _ in range(self.size)]
        if success:
            for fact in final_facts:
                if fact[0] == "Value":
                    _, r, c, v = fact
                    self.solution[r][c] = v
        stats = {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated, 'time': time.time() - start}
        if stream_queue:
            stream_queue.put(('done', self.solution, stats))
        return self.solution, stats, []

    def solve(self):
        # Call the engine starting from the initial events of the Base (from the puzzle grid)
        self.nodes_expanded = 0
        self.nodes_generated = 0
        initial_facts = self.kb.facts.copy()
        
        success, final_facts = self.backtrack(initial_facts)
        
        # Package the results for the Main module interface
        final_domains = [[set() for _ in range(self.size)] for _ in range(self.size)]
        self.solution = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        if success:
            for fact in final_facts:
                if fact[0] == "Value":
                    _, r, c, v = fact
                    self.solution[r][c] = v
                    final_domains[r][c].add(v)
            return "Solved", final_domains
        else:
            for fact in final_facts:
                if fact[0] == "Value":
                    _, r, c, v = fact
                    final_domains[r][c].add(v)
            return "Contradiction", final_domains
