import sys
from pathlib import Path

# Add project root to sys.path to allow running as script or importing
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from ..futoshiki_solver import futoshiki_solver
from .kb import FutoshikiKB
import copy

class forward_chaining(futoshiki_solver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
        h_constraints, v_constraints = constraint[0], constraint[1]
        self.kb = FutoshikiKB.from_input(size, grid, h_constraints, v_constraints)

    def forward_chain(self):
        """Thực hiện lan truyền ràng buộc cho đến khi không thể thu hẹp thêm."""
        changed = True
        while changed:
            changed = False
            changed |= self.kb.apply_a3_a4_uniqueness()
            changed |= self.kb.apply_a5_to_a8_constraints()
        
        # Kiểm tra mâu thuẫn (có ô nào rỗng domain không)
        for i in range(self.kb.n):
            for j in range(self.kb.n):
                if len(self.kb.domains[i][j]) == 0:
                    return False # Mâu thuẫn
        return True # Hợp lệ (nhưng có thể chưa xong)

    def backtrack(self):
        """Tìm kiếm quay lui kết hợp suy luận tiến."""
        # 1. Chạy Forward Chaining để rút gọn miền giá trị
        if not self.forward_chain():
            return False # Nhánh này vô nghiệm, quay lui

        # 2. Kiểm tra xem đã giải xong chưa
        is_solved = all(len(self.kb.domains[i][j]) == 1 for i in range(self.kb.n) for j in range(self.kb.n))
        if is_solved:
            return True

        # 3. Chọn một ô để "đoán"
        # Heuristic: Minimum Remaining Values (MRV) - Chọn ô có ít khả năng nhất để giảm rẽ nhánh
        min_options = float('inf')
        best_cell = None
        for i in range(self.kb.n):
            for j in range(self.kb.n):
                d_len = len(self.kb.domains[i][j])
                if 1 < d_len < min_options:
                    min_options = d_len
                    best_cell = (i, j)

        if not best_cell:
            return False # Không tìm được ô hợp lệ (mặc dù chưa giải xong)

        r, c = best_cell

        # 4. Thử từng giá trị trong domain của ô đã chọn
        for val in list(self.kb.domains[r][c]):
            # LƯU TRẠNG THÁI: Rất quan trọng, dùng deepcopy để không hỏng dữ liệu khi quay lui
            saved_domains = copy.deepcopy(self.kb.domains)

            # Thử gán giá trị
            self.kb.domains[r][c] = {val}

            # Đệ quy đi tiếp
            if self.backtrack():
                return True

            # QUAY LUI: Khôi phục lại trạng thái cũ nếu việc gán 'val' dẫn đến ngõ cụt
            self.kb.domains = saved_domains

        return False # Tất cả các nhánh phỏng đoán đều sai

    def solve(self):
        self.kb.apply_a9_enforce_clues()
        
        # Gọi hàm backtrack thay vì gọi thẳng forward_chain
        success = self.backtrack()
        
        if success:
            self.solution = [[list(self.kb.domains[i][j])[0] for j in range(self.size)] for i in range(self.size)]
            return "Solved", self.kb.domains
        else:
            return "Contradiction", self.kb.domains