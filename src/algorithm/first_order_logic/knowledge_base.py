class FutoshikiKB:
    def __init__(self, n, given_clues, less_h, greater_h, less_v, greater_v):
        self.n = n
        self.given_clues = given_clues
        self.less_h = less_h
        self.greater_h = greater_h
        self.less_v = less_v
        self.greater_v = greater_v
        
        self.facts = []
        self.rules = []
        
        self._ground_rules_and_facts()

    @staticmethod
    def from_input(size, grid, h_constraints, v_constraints):
        given_clues = []
        for i in range(size):
            for j in range(size):
                if grid[i][j] != 0:
                    given_clues.append((i, j, grid[i][j]))

        less_h = []
        greater_h = []
        for i in range(size):
            for j in range(size - 1):
                if h_constraints[i][j] == 1:
                    less_h.append((i, j))
                elif h_constraints[i][j] == -1:
                    greater_h.append((i, j))

        less_v = []
        greater_v = []
        for i in range(size - 1):
            for j in range(size):
                if v_constraints[i][j] == 1:
                    less_v.append((i, j))
                elif v_constraints[i][j] == -1:
                    greater_v.append((i, j))

        return FutoshikiKB(size, given_clues, less_h, greater_h, less_v, greater_v)

    def _ground_rules_and_facts(self):
        # 1. Khởi tạo Facts ban đầu (từ các lưới đã cho)
        for r, c, v in self.given_clues:
            self.facts.append(("Value", r, c, v))
            
        # 2. Khởi tạo Rules (Luật Horn)
        # Mỗi luật là một tuple: (premises, conclusion)
        # premises là 1 list các atom, conclusion là 1 atom. Atom: ("Value", r, c, v) hoặc ("NotValue", r, c, v)
        
        # Rule: Ràng buộc giá trị độc nhất trong Hàng (Row Uniqueness)
        # Nếu ô (r, c1) có giá trị v -> ô (r, c2) sẽ Không có giá trị v
        for r in range(self.n):
            for v in range(1, self.n + 1):
                for c1 in range(self.n):
                    for c2 in range(self.n):
                        if c1 != c2:
                            self.rules.append(([("Value", r, c1, v)], ("NotValue", r, c2, v)))
                            
        # Rule: Ràng buộc giá trị độc nhất trong Cột (Col Uniqueness)
        # Nếu ô (r1, c) có giá trị v -> ô (r2, c) sẽ Không có giá trị v
        for c in range(self.n):
            for v in range(1, self.n + 1):
                for r1 in range(self.n):
                    for r2 in range(self.n):
                        if r1 != r2:
                            self.rules.append(([("Value", r1, c, v)], ("NotValue", r2, c, v)))

        # Rule: Tối đa một giá trị mỗi ô (Cell uniqueness)
        # Nếu ô (r, c) có giá trị v1 -> ô (r, c) sẽ Không có giá trị v2
        for r in range(self.n):
            for c in range(self.n):
                for v1 in range(1, self.n + 1):
                    for v2 in range(1, self.n + 1):
                        if v1 != v2:
                            self.rules.append(([("Value", r, c, v1)], ("NotValue", r, c, v2)))
                            
        # Rule: Tối thiểu một giá trị mỗi ô 
        # Nếu N-1 giá trị đều là NotValue -> giá trị còn lại phải là Value
        for r in range(self.n):
            for c in range(self.n):
                for target_v in range(1, self.n + 1):
                    premises = []
                    for other_v in range(1, self.n + 1):
                        if other_v != target_v:
                            premises.append(("NotValue", r, c, other_v))
                    self.rules.append((premises, ("Value", r, c, target_v)))

        # Rule: Bất đẳng thức (Inequalities)
        def enforce_less(r1, c1, r2, c2):
            # Nếu val(r1, c1) = v1, thì val(r2, c2) không thể <= v1 (vì val(r1, c1) phải nhỏ hơn)
            for v1 in range(1, self.n + 1):
                for v2 in range(1, v1 + 1):
                    self.rules.append(([("Value", r1, c1, v1)], ("NotValue", r2, c2, v2)))
                    
        for r, c in self.less_h:
            enforce_less(r, c, r, c + 1)
        for r, c in self.greater_h:
            enforce_less(r, c + 1, r, c) # (r, c) > (r, c+1) <=> (r, c+1) < (r, c)
        
        for r, c in self.less_v:
            enforce_less(r, c, r + 1, c)
        for r, c in self.greater_v:
            enforce_less(r + 1, c, r, c)

    def format_output(self, h_constraints, v_constraints, grid=None):
        output_lines = []
        for row_idx in range(self.n):
            row_str = ""
            for col_idx in range(self.n):
                val = grid[row_idx][col_idx] if grid else 0
                row_str += str(val)
                if col_idx < self.n - 1:
                    constraint = h_constraints[row_idx][col_idx]
                    if constraint == 1:
                        row_str += " < "
                    elif constraint == -1:
                        row_str += " > "
                    else:
                        row_str += "   "
            output_lines.append(row_str)
            if row_idx < self.n - 1:
                v_row_str = ""
                for col_idx in range(self.n):
                    constraint = v_constraints[row_idx][col_idx]
                    if constraint == 1:
                        v_row_str += "^   "
                    elif constraint == -1:
                        v_row_str += "v   "
                    else:
                        v_row_str += "    "
                output_lines.append(v_row_str)
        return "\n".join(output_lines)
