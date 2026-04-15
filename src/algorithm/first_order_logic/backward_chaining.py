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

    def prove(self, goal, current_facts, visited=None, memo=None):
        """
        Prolog-style Backward Chaining engine (SLD Resolution).
        """
        if visited is None:
            visited = set()
        if memo is None:
            memo = {}
            
        # Base case: Goal is literally a known Fact
        if goal in current_facts:
            return True
            
        if goal in memo:
            return memo[goal]
            
        # Phòng chống lặp vô hạn (Infinite Recursion cycle detection) trong luật
        if goal in visited:
            return False 
            
        visited.add(goal)
        
        # Duyệt từng luật trong Knowledge Base (đã được tạo dưới dạng tuple: Premises -> Conclusion)
        for premises, conclusion in self.kb.rules:
            # Thuật toán SLD: Nếu luật này có hệ quả = Goal ta đang tìm
            if conclusion == goal:
                all_premises_proven = True
                
                # Thì ta thiết lập Goal mới là phải đi chứng minh toàn bộ các tiền đề (Premises)
                for premise in premises:
                    if not self.prove(premise, current_facts, visited, memo):
                        all_premises_proven = False
                        break
                        
                # Chỉ cần 1 rule với toàn bộ conditions = True, Atom được tính là Proven!
                if all_premises_proven:
                    visited.remove(goal)
                    memo[goal] = True
                    return True
                    
        # Nếu duyệt hết các luật mà không có nhánh nào chứng minh được
        visited.remove(goal)
        memo[goal] = False
        return False

    def sld_backtrack(self, current_facts):
        """
        Cấu trúc Depth First Search (DFS) đại diện cho nhánh rẽ cây lựa chọn của Prolog giải toàn bộ bài toán.
        """
        assigned_count = sum(1 for fact in current_facts if fact[0] == "Value")
        if assigned_count == self.size * self.size:
            return True, current_facts
            
        assigned_cells = set()
        for fact in current_facts:
            if fact[0] == "Value":
                _, r, c, v = fact
                assigned_cells.add((r, c))
                
        # Heuristic tìm ô phù hợp nhất (MRV) để đẩy Prolog search speed
        target_cell = None
        min_options = float('inf')
        valid_options_for_target = []
        
        for r in range(self.size):
            for c in range(self.size):
                if (r, c) not in assigned_cells:
                    
                    valid_vals = []
                    for v in range(1, self.size + 1):
                        # Prolog NAF (Negation As Failure):
                        # Gán `NotValue` làm Goal. Lệnh prove() sẽ dò lại Knowledge Base.
                        # Nếu Hàm prove KHÔNG THỂ chứng minh `NotValue` là đúng -> nó Hợp lệ để thử điền!
                        if not self.prove(("NotValue", r, c, v), current_facts):
                            valid_vals.append(v)
                            
                    if len(valid_vals) == 0:
                        return False, current_facts # Trả về false sớm cắt nhánh lỗi
                        
                    if len(valid_vals) < min_options:
                        min_options = len(valid_vals)
                        target_cell = (r, c)
                        valid_options_for_target = valid_vals

        if not target_cell:
            return False, current_facts

        r, c = target_cell
        
        # Prolog Branching: Thử Assert Fact mới và đệ quy xuống nhánh DFS
        for val in valid_options_for_target:
            new_facts = current_facts.copy()
            new_facts.append(("Value", r, c, val))
            
            success, final_facts = self.sld_backtrack(new_facts)
            if success:
                return True, final_facts
                
        return False, current_facts

    def solve(self):
        # Thiết lập giới hạn đệ quy cao hơn để chứa SLD Resolution Tree
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(old_limit, 5000))
        
        try:
            # Khởi tạo SLD Resolution Engine từ Given clues a9
            success, final_facts = self.sld_backtrack(self.kb.facts)
            
            # Đóng gói
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
