import sys
from pathlib import Path
import copy

# Add project root to sys.path to allow running as script or importing
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from .knowledge_base import FutoshikiKB
from ..futoshiki_solver import futoshiki_solver

class forward_chaining(futoshiki_solver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
        h_constraints, v_constraints = constraint[0], constraint[1]
        self.kb = FutoshikiKB.from_input(size, grid, h_constraints, v_constraints)
        self.solved = False

    def forward_chain(self, current_facts):
        """
        Thuật toán Forward Chaining áp dụng cơ chế suy diễn trên tập luật Horn.
        Sử dụng fact_set (kiểu set của Python) để đạt O(1) tra cứu, thay vì duyệt List.
        Vòng lặp tiếp tục cho đến khi không có Fact mới nào được suy diễn từ bộ luật.
        """
        fact_set = set(current_facts)
        changed = True
        
        while changed:
            changed = False
            for rule in self.kb.rules:
                premises, conclusion = rule
                
                # Kiểm tra nhanh conclusion đã tồn tại chưa (tránh duyệt premises tốn thời gian)
                if conclusion not in fact_set:
                    # Kiểm tra xem TẤT CẢ các điều kiện (premises) đã được thỏa mãn (có sẵn) chưa
                    all_premises_met = True
                    for premise in premises:
                        if premise not in fact_set:
                            all_premises_met = False
                            break
                            
                    # Áp dụng Modus Ponens: Nếu tất cả Vế Trái đúng -> Rút ra hệ quả Vế Phải
                    if all_premises_met:
                        fact_set.add(conclusion)
                        current_facts.append(conclusion)
                        changed = True
                        
        # POST-CHECK: Kiểm tra xem có sinh ra mâu thuẫn logic nào không
        # Mâu thuẫn khi ô (r,c) cùng xuất hiện cả ("Value", r, c, v) và ("NotValue", r, c, v)
        for fact in current_facts:
            if fact[0] == "Value":
                _, r, c, v = fact
                if ("NotValue", r, c, v) in fact_set:
                    return False, current_facts # Xung đột logic phát sinh!
                    
        return True, current_facts

    def is_solved_check(self, facts):
        count = 0
        for fact in facts:
            if fact[0] == "Value":
                count += 1
        # Lưới giải thành công khi số lượng mốc hoàn thành đúng bằng tổng số ô (N x N)
        return count == self.size * self.size

    def backtrack(self, current_facts):
        """
        Logic Backtracking kết hợp Forward Chaining.
        Nều FC tắc (chưa ra kết quả cuối nhưng hết luật suy diễn), ta đoán 1 biến và chạy FC tiếp.
        """
        # Bước 1: Suy diễn Forward Chaining trên thực tại đang có
        success, derived_facts = self.forward_chain(current_facts)
        if not success:
            return False, derived_facts
            
        if self.is_solved_check(derived_facts):
            return True, derived_facts
            
        # Lập bản đồ các ô đã được gán giá trị
        fact_set = set(derived_facts)
        assigned_cells = set()
        for fact in derived_facts:
            if fact[0] == "Value":
                _, r, c, v = fact
                assigned_cells.add((r, c))
                
        # Bước 2: Chọn một ô mục tiêu (Minimum Remaining Values - MRV)
        best_cell = None
        min_options = float('inf')
        valid_options_for_best = []
        
        for r in range(self.size):
            for c in range(self.size):
                if (r, c) not in assigned_cells:
                    options = []
                    for v in range(1, self.size + 1):
                        # Khả năng hợp lệ là nếu quy luật không cấm nó (chưa có NotValue)
                        if ("NotValue", r, c, v) not in fact_set:
                            options.append(v)
                    
                    if len(options) == 0:
                        return False, derived_facts # Ô này không có khả năng nào do Contradiction
                        
                    if len(options) < min_options:
                        min_options = len(options)
                        best_cell = (r, c)
                        valid_options_for_best = options

        if not best_cell:
            return False, derived_facts

        r, c = best_cell
        
        # Bước 3: Phỏng đoán và chạy nhánh mới dựa trên FC 
        for val in valid_options_for_best:
            # COPY môi trường biến để Backtracking không phá hỏng thực tại cũ cùa DFS
            new_facts = derived_facts.copy() 
            new_facts.append(("Value", r, c, val))
            
            success, final_facts = self.backtrack(new_facts)
            if success:
                return True, final_facts
                
        return False, derived_facts

    def solve(self):
        # Gọi engine bắt nguồn từ các sự kiện ban đầu của Base (từ lưới câu đố)
        initial_facts = self.kb.facts.copy()
        
        success, final_facts = self.backtrack(initial_facts)
        
        # Đóng gói kết quả cho giao diện Main module
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