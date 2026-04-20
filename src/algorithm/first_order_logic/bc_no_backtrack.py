import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from .knowledge_base import FutoshikiKB
from ..futoshiki_solver import futoshiki_solver

class bc_no_backtrack(futoshiki_solver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
        h_constraints, v_constraints = constraint[0], constraint[1]
        self.kb = FutoshikiKB.from_input(size, grid, h_constraints, v_constraints)
        self.rule_index = {}
        for premises, conclusion in self.kb.rules:
            if conclusion not in self.rule_index:
                self.rule_index[conclusion] = []
            self.rule_index[conclusion].append(premises)

    def backtracking_fallback(self, stream_queue=None):
        from .backward_chaining_with_ac3 import backward_chaining_with_ac3
        solver = backward_chaining_with_ac3(
            self.size,
            self.grid.tolist(),
            [self.h_constraints.tolist(), self.v_constraints.tolist()]
        )
        self._fallback_solver = solver
        if stream_queue:
            solution, stats, history = solver.solve_with_history(stream_queue)
            self.nodes_expanded += stats.get('nodes_expanded', solver.nodes_expanded)
            self.nodes_generated += stats.get('nodes_generated', solver.nodes_generated)
            self.solution = solver.solution
            return ("Solved" if solution else "Contradiction"), history
        status, domains = solver.solve()
        self.nodes_expanded += solver.nodes_expanded
        self.nodes_generated += solver.nodes_generated
        self.solution = solver.solution
        return status, domains

    def prove(self, goal, current_facts, table=None):
        """
        SLG Resolution (Tabling / Memoization) Engine combined with CLP.
        """
        self.nodes_expanded += 1
        if table is None:
            table = {}
            
        if goal in current_facts:
            return True

        if goal in table:
            if table[goal] == "Evaluating":
                return False 
            return table[goal]
            
        table[goal] = "Evaluating"
        
        if goal in self.rule_index:
            for premises in self.rule_index[goal]:
                all_premises_proven = True
                
                for premise in premises:
                    if not self.prove(premise, current_facts, table):
                        all_premises_proven = False
                        break
                        
                if all_premises_proven:
                    table[goal] = True
                    return True
                    
        table[goal] = False
        return False

    def sld_no_backtrack(self, current_facts, stream_queue=None):
        import concurrent.futures
        
        while True:
            self.nodes_expanded += 1
            assigned_count = sum(1 for fact in current_facts if fact[0] == "Value")
            if assigned_count == self.size * self.size:
                return "Solved", current_facts
                
            assigned_cells = set()
            for fact in current_facts:
                if fact[0] == "Value":
                    _, r, c, v = fact
                    assigned_cells.add((r, c))
                    
            empty_cells = [(r, c) for r in range(self.size) for c in range(self.size) if (r, c) not in assigned_cells]
            
            def get_valid_vals(cell):
                r, c = cell
                valid = []
                for v in range(1, self.size + 1):
                    if not self.prove(("NotValue", r, c, v), current_facts):
                        valid.append(v)
                return r, c, valid
                
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(get_valid_vals, empty_cells))
                
            target_cell = None
            min_options = float('inf')
            valid_options_for_target = []
            
            for r, c, valid_vals in results:
                if stream_queue:
                    for v in valid_vals:
                        stream_queue.put(('check', r, c, v))
                if len(valid_vals) == 0:
                    return "Contradiction", current_facts
                    
                if len(valid_vals) < min_options:
                    min_options = len(valid_vals)
                    target_cell = (r, c)
                    valid_options_for_target = valid_vals

            if min_options == 1:
                r, c = target_cell
                val = valid_options_for_target[0]
                current_facts.add(("Value", r, c, val))
                self.nodes_generated += 1
                if stream_queue:
                    stream_queue.put(('assign', r, c, val))
            else:
                return "Unresolved (Needs Backtracking)", current_facts

    def solve_with_history(self, stream_queue=None):
        start = time.time()
        self.nodes_expanded = 0
        self.nodes_generated = 0
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(old_limit, 100000))
        try:
            current_facts_set = set(self.kb.facts)
            status, final_facts = self.sld_no_backtrack(current_facts_set, stream_queue)
            if status == "Unresolved (Needs Backtracking)":
                status, _ = self.backtracking_fallback(stream_queue)
                stats = {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated, 'time': time.time() - start}
                if stream_queue:
                    stream_queue.put(('done', self.solution, stats))
                return self.solution, stats, []
            self.solution = [[0 for _ in range(self.size)] for _ in range(self.size)]
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
        sys.setrecursionlimit(max(old_limit, 100000))
        
        try:
            current_facts_set = set(self.kb.facts)
            status, final_facts = self.sld_no_backtrack(current_facts_set)
            if status == "Unresolved (Needs Backtracking)":
                return self.backtracking_fallback()
            
            # Packaging
            final_domains = [[set() for _ in range(self.size)] for _ in range(self.size)]
            self.solution = [[0 for _ in range(self.size)] for _ in range(self.size)]
            
            if status == "Solved":
                for fact in final_facts:
                    if fact[0] == "Value":
                        _, r, c, v = fact
                        self.solution[r][c] = v
                        final_domains[r][c].add(v)
                return status, final_domains
            else:
                for fact in final_facts:
                    if fact[0] == "Value":
                        _, r, c, v = fact
                        self.solution[r][c] = v
                        final_domains[r][c].add(v)
                return status, final_domains
        finally:
            sys.setrecursionlimit(old_limit)
