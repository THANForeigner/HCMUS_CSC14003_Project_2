import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from .knowledge_base import FutoshikiKB
from ..futoshiki_solver import futoshiki_solver

class backward_chaining(futoshiki_solver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
        h_constraints, v_constraints = constraint[0], constraint[1]
        self.kb = FutoshikiKB.from_input(size, grid, h_constraints, v_constraints)

    def prove(self, goal, current_facts, visited=None, memo=None):
        self.nodes_expanded += 1
        if visited is None:
            visited = set()
        if memo is None:
            memo = {}
            
        if goal in current_facts:
            return True
            
        if goal in memo:
            return memo[goal]
            
        if goal in visited:
            return False 
            
        visited.add(goal)
        
        # Traverse each rule in the Knowledge Base 
        for premises, conclusion in self.kb.rules:
            if conclusion == goal:
                all_premises_proven = True
                for premise in premises:
                    if not self.prove(premise, current_facts, visited, memo):
                        all_premises_proven = False
                        break
                if all_premises_proven:
                    visited.remove(goal)
                    memo[goal] = True
                    return True
        visited.remove(goal)
        memo[goal] = False
        return False

    def sld_backtrack(self, current_facts, stream_queue=None):
        # Depth First Search (DFS) 
        assigned_count = sum(1 for fact in current_facts if fact[0] == "Value")
        if assigned_count == self.size * self.size:
            return True, current_facts
            
        assigned_cells = set()
        for fact in current_facts:
            if fact[0] == "Value":
                _, r, c, v = fact
                assigned_cells.add((r, c))
                
        # Heuristic to find the best cell (MRV) to boost Prolog search speed
        target_cell = None
        min_options = float('inf')
        valid_options_for_target = []
        
        for r in range(self.size):
            for c in range(self.size):
                if (r, c) not in assigned_cells:
                    
                    valid_vals = []
                    for v in range(1, self.size + 1):
                        # Prolog NAF (Negation As Failure)
                        if stream_queue:
                            stream_queue.put(('check', r, c, v))
                        if not self.prove(("NotValue", r, c, v), current_facts):
                            valid_vals.append(v)
                            
                    if len(valid_vals) == 0:
                        return False, current_facts # Return false early to cut the error branch
                        
                    if len(valid_vals) < min_options:
                        min_options = len(valid_vals)
                        target_cell = (r, c)
                        valid_options_for_target = valid_vals

        if not target_cell:
            return False, current_facts

        r, c = target_cell
        
        # Try asserting a new Fact and recurse down the DFS branch
        for val in valid_options_for_target:
            if stream_queue:
                stream_queue.put(('assign', r, c, val))
            new_facts = current_facts.copy()
            new_facts.append(("Value", r, c, val))
            self.nodes_generated += 1
            
            success, final_facts = self.sld_backtrack(new_facts, stream_queue)
            if success:
                return True, final_facts
                
            if stream_queue:
                stream_queue.put(('backtrack', r, c, 0))
                
        return False, current_facts

    def solve_with_history(self, stream_queue=None):
        start = time.time()
        self.nodes_expanded = 0
        self.nodes_generated = 0
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(old_limit, 100000))
        
        try:
            success, final_facts = self.sld_backtrack(self.kb.facts, stream_queue)
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
        finally:
            sys.setrecursionlimit(old_limit)

    def solve(self):
        self.nodes_expanded = 0
        self.nodes_generated = 0
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(old_limit, 5000)) # Increase recursion limit
        
        try:
            success, final_facts = self.sld_backtrack(self.kb.facts)
            
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
        finally:
            sys.setrecursionlimit(old_limit)
