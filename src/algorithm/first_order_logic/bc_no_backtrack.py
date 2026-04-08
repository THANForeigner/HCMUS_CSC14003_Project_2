import sys
from pathlib import Path

# Add project root to sys.path to allow running as script or importing
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from .knowledge_base import FutoshikiKB
from ..futoshiki_solver import futoshiki_solver

class bc_no_backtrack(futoshiki_solver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
        h_constraints, v_constraints = constraint[0], constraint[1]
        self.kb = FutoshikiKB.from_input(size, grid, h_constraints, v_constraints)
        
        # CLP / First-Argument Indexing (Tối ưu tìm luật O(1))
        self.rule_index = {}
        for premises, conclusion in self.kb.rules:
            if conclusion not in self.rule_index:
                self.rule_index[conclusion] = []
            self.rule_index[conclusion].append(premises)

    def prove(self, goal, current_facts, table=None):
        """
        SLG Resolution (Tabling / Memoization) Engine kết hợp CLP.
        """
        if table is None:
            table = {}
            
        # Base case: Fact đã có sẵn (O(1) vì current_facts là Set)
        if goal in current_facts:
            return True
            
        # Lookup trong Table (Tabling mechanism)
        if goal in table:
            if table[goal] == "Evaluating":
                # Cyclic dependency (Re-entrant call phát hiện bởi SLG)
                return False 
            return table[goal]
            
        # Đánh dấu Goal đang được đánh giá (đưa vào Tabling)
        table[goal] = "Evaluating"
        
        # Duyệt luật O(1) bằng First-Argument Indexing thay vì vòng lặp O(N)
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
                    
        # Bác bỏ Goal nếu mọi nhánh đều thất bại
        table[goal] = False
        return False

    def sld_no_backtrack(self, current_facts):
        """
        Chạy Backward Chaining (SLD/SLG) liên tục chỉ khi TÌM ĐƯỢC CHẮC CHẮN NGIỆM (options = 1).
        Không có Branching/Backtracking. Gặp ngõ cụt sẽ dừng ngay lập tức.
        """
        import concurrent.futures
        
        while True:
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
                    # Gọi self.prove song song
                    if not self.prove(("NotValue", r, c, v), current_facts):
                        valid.append(v)
                return r, c, valid
                
            # Tối ưu: Chạy song song self.prove cho toàn bộ các ô trống bằng ThreadPool
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(get_valid_vals, empty_cells))
                
            target_cell = None
            min_options = float('inf')
            valid_options_for_target = []
            
            for r, c, valid_vals in results:
                if len(valid_vals) == 0:
                    return "Contradiction", current_facts
                    
                if len(valid_vals) < min_options:
                    min_options = len(valid_vals)
                    target_cell = (r, c)
                    valid_options_for_target = valid_vals

            # --- NO BACKTRACKING LOGIC ---
            if min_options == 1:
                # Khẳng định Fact chắc chắn duy nhất 
                r, c = target_cell
                val = valid_options_for_target[0]
                current_facts.add(("Value", r, c, val))
                # Tiếp tục vòng lặp While với current_facts mới
            else:
                # Nhiều hơn 1 lựa chọn -> Cần rẽ nhánh, nhưng ta không dùng backtracking ở mode này.
                return "Unresolved (Needs Backtracking)", current_facts

    def solve(self):
        # Thiết lập giới hạn đệ quy cao hơn để chứa SLD Resolution Tree
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(old_limit, 100000))
        
        try:
            # Đưa list facts về set để O(1)
            current_facts_set = set(self.kb.facts)
            status, final_facts = self.sld_no_backtrack(current_facts_set)
            
            # Đóng gói
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
