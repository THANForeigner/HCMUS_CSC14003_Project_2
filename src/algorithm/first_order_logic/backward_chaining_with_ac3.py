import sys
import time
from pathlib import Path

# Add project root to sys.path to allow running as script or importing
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from .knowledge_base import FutoshikiKB
from ..futoshiki_solver import futoshiki_solver

class backward_chaining_with_ac3(futoshiki_solver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
        h_constraints, v_constraints = constraint[0], constraint[1]
        self.kb = FutoshikiKB.from_input(size, grid, h_constraints, v_constraints)

    def get_neighbors(self, r, c):
        """Get all cells that share a constraint with (r, c)."""
        neighbors = set()
        for i in range(self.size):
            if i != c:
                neighbors.add((r, i))
            if i != r:
                neighbors.add((i, c))
        return neighbors

    def revise(self, domains, xi, xj):
        """Revise domain of xi given domain of xj."""
        revised = False
        r1, c1 = xi
        r2, c2 = xj
        
        relation = "!="
        # Check horizontal constraints
        if r1 == r2 and abs(c1 - c2) == 1:
            left, right = (c1, c2) if c1 < c2 else (c2, c1)
            h = self.h_constraints[r1][left]
            if h == 1:
                relation = "<" if c1 < c2 else ">"
            elif h == -1:
                relation = ">" if c1 < c2 else "<"
        
        # Check vertical constraints
        elif c1 == c2 and abs(r1 - r2) == 1:
            top, bottom = (r1, r2) if r1 < r2 else (r2, r1)
            v = self.v_constraints[top][c1]
            if v == 1:
                relation = "<" if r1 < r2 else ">"
            elif v == -1:
                relation = ">" if r1 < r2 else "<"

        to_remove = set()
        for x in domains[xi]:
            satisfies = False
            for y in domains[xj]:
                if relation == "!=" and x != y:
                    satisfies = True; break
                elif relation == "<" and x < y:
                    satisfies = True; break
                elif relation == ">" and x > y:
                    satisfies = True; break
            if not satisfies:
                to_remove.add(x)
        
        if to_remove:
            domains[xi] -= to_remove
            revised = True
        return revised

    def ac3(self, domains):
        """Maintains Arc Consistency."""
        queue = []
        for r1 in range(self.size):
            for c1 in range(self.size):
                xi = (r1, c1)
                for xj in self.get_neighbors(r1, c1):
                    queue.append((xi, xj))
        
        while queue:
            xi, xj = queue.pop(0)
            if self.revise(domains, xi, xj):
                if len(domains[xi]) == 0:
                    return False
                for xk in self.get_neighbors(*xi):
                    if xk != xj:
                        queue.append((xk, xi))
        return True

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

    def sld_backtrack(self, current_facts, stream_queue=None):
        """
        Cấu trúc Depth First Search (DFS) đại diện cho nhánh rẽ cây lựa chọn của Prolog giải toàn bộ bài toán.
        Sử dụng thêm AC-3 kết hợp để loại bỏ miền giá trị dư thừa siêu nhanh trước khi chạy Logic Rule Search.
        """
        assigned_count = sum(1 for fact in current_facts if fact[0] == "Value")
        if assigned_count == self.size * self.size:
            return True, current_facts
            
        assigned_cells = set()
        domains = {(r, c): set(range(1, self.size + 1)) for r in range(self.size) for c in range(self.size)}
        
        for fact in current_facts:
            if fact[0] == "Value":
                _, r, c, v = fact
                assigned_cells.add((r, c))
                domains[(r, c)] = {v}

        # 1. Chạy CSP AC-3 để lọc domains trước khi đưa vào Prolog Resolution
        if not self.ac3(domains):
            return False, current_facts
                
        # Heuristic tìm ô phù hợp nhất (MRV) để đẩy Prolog search speed
        target_cell = None
        min_options = float('inf')
        valid_options_for_target = []
        
        # Share memo cho toàn bộ step dò value trong cùng 1 context facts để không tốn thời gian chứng minh lại
        shared_memo = {}
        
        for r in range(self.size):
            for c in range(self.size):
                if (r, c) not in assigned_cells:
                    
                    # 2. Thay vì duyệt 1..self.size, chỉ duyệt tập giá trị đã qua CSP AC-3 Filter
                    ac3_filtered_vals = list(domains[(r, c)])
                    
                    if len(ac3_filtered_vals) == 0:
                        return False, current_facts # Trả về false sớm cắt nhánh lỗi
                        
                    valid_vals = []
                    for v in ac3_filtered_vals:
                        if stream_queue:
                            stream_queue.put(('check', r, c, v))
                        # Prolog NAF (Negation As Failure):
                        # Gán `NotValue` làm Goal. AC3 coi v là có thể, còn prove() là Tòa Án FOL chốt hạ.
                        if not self.prove(("NotValue", r, c, v), current_facts, memo=shared_memo):
                            valid_vals.append(v)
                            
                    if len(valid_vals) == 0:
                        return False, current_facts 
                        
                    if len(valid_vals) < min_options:
                        min_options = len(valid_vals)
                        target_cell = (r, c)
                        valid_options_for_target = valid_vals

        if not target_cell:
            return False, current_facts

        r, c = target_cell
        
        # Prolog Branching: Thử Assert Fact mới và đệ quy xuống nhánh DFS
        for val in valid_options_for_target:
            if stream_queue:
                stream_queue.put(('assign', r, c, val))
            new_facts = current_facts.copy()
            new_facts.append(("Value", r, c, val))
            
            success, final_facts = self.sld_backtrack(new_facts, stream_queue)
            if success:
                return True, final_facts
                
            if stream_queue:
                stream_queue.put(('backtrack', r, c, 0))
                
        return False, current_facts

    def solve_with_history(self, stream_queue=None):
        start = time.time()
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
            
            stats = {'nodes_expanded': 0, 'nodes_generated': 0, 'time': time.time() - start}
            if stream_queue:
                stream_queue.put(('done', self.solution, stats))
            return self.solution, stats, []
        finally:
            sys.setrecursionlimit(old_limit)

    def solve(self):
        # Thiết lập giới hạn đệ quy cao hơn để chứa SLD Resolution Tree
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(old_limit, 100000))
        
        try:
            # Khởi tạo SLD Resolution Engine từ Given clues
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
