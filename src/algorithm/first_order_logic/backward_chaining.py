import sys
from pathlib import Path

# Add project root to sys.path to allow running as script or importing
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from .knowledge_base import FutoshikiKB
from ..futoshiki_solver import futoshiki_solver

class backward_chaining(futoshiki_solver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
        h_constraints, v_constraints = constraint[0], constraint[1]
        self.kb = FutoshikiKB.from_input(size, grid, h_constraints, v_constraints)

    def prove(self, goal, current_facts, visited=None):
        """
        Prolog-style Backward Chaining (SLD Resolution)
        Truy vấn ngược trên cây Luật Horn cho đến khi chạm Fact.
        """
        if visited is None:
            visited = set()
            
        if goal in current_facts:
            return True
            
        if goal in visited:
            return False 
            
        visited.add(goal)
        
        for premises, conclusion in self.kb.rules:
            if conclusion == goal:
                all_premises_proven = True
                
                for premise in premises:
                    if not self.prove(premise, current_facts, visited):
                        all_premises_proven = False
                        break
                        
                if all_premises_proven:
                    visited.remove(goal)
                    return True
                    
        visited.remove(goal)
        return False

    def sld_resolve(self, current_facts):
        """
        Phiên bản Forward-like execution của SLD Resolution ĐÃ XOÁ BACKTRACKING.
        Thuật toán duyệt hỏi (query) dần từng giá trị của các ô trống.
        Chỉ khi SLD chứng minh được n-1 giá trị là Sai (NotValue = True), 
        thì giá trị duy nhất còn lại mới được nhận định là Đúng và thêm vào Fact pool.
        """
        changed = True
        fact_set = set(current_facts)
        
        assigned_cells = set()
        for fact in current_facts:
            if fact[0] == "Value":
                assigned_cells.add((fact[1], fact[2]))
                
        while changed:
            changed = False
            for r in range(self.size):
                for c in range(self.size):
                    if (r, c) not in assigned_cells:
                        valid_vals = []
                        for v in range(1, self.size + 1):
                            # Truy vấn Prolog SLD `?- NotValue(r, c, v)`
                            if not self.prove(("NotValue", r, c, v), current_facts):
                                valid_vals.append(v)
                                
                        # Nều ô này CHỊ CÒN DUY NHẤT 1 kết quả không bị Invalid (Fail to prove NotValue)
                        if len(valid_vals) == 1:
                            val = valid_vals[0]
                            new_fact = ("Value", r, c, val)
                            if new_fact not in fact_set:
                                fact_set.add(new_fact)
                                current_facts.append(new_fact)
                                assigned_cells.add((r, c))
                                changed = True
                        # Nếu tất cả các gán trị đều Invalid -> Mâu thuẫn logic
                        elif len(valid_vals) == 0:
                            return False, current_facts

        return True, current_facts

    def solve(self):
        # Khởi tạo SLD Resolution Engine từ Given clues a9
        success, final_facts = self.sld_resolve(self.kb.facts.copy())
        
        # Kiểm tra xem có điền đủ các ô không (vì không backtrack, có thể kẹt)
        count = sum(1 for fact in final_facts if fact[0] == "Value")
        is_solved = (count == self.size * self.size)
        
        # Đóng gói kết quả
        final_domains = [[set() for _ in range(self.size)] for _ in range(self.size)]
        self.solution = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        if success:
            for fact in final_facts:
                if fact[0] == "Value":
                    _, r, c, v = fact
                    self.solution[r][c] = v
                    final_domains[r][c].add(v)
                    
            if is_solved:
                return "Solved", final_domains
            else:
                return "Unresolved (Needs Backtracking)", final_domains
        else:
            for fact in final_facts:
                if fact[0] == "Value":
                    _, r, c, v = fact
                    final_domains[r][c].add(v)
            return "Contradiction", final_domains
