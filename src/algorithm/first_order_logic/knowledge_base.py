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

        # Ràng buộc: Mọi giá trị v phải xuất hiện đúng một lần trong mỗi Hàng (Luật duy nhất trong Hàng)
        # Nếu N-1 ô trong hàng không chứa giá trị v -> ô còn lại mang giá trị v
        for r in range(self.n):
            for v in range(1, self.n + 1):
                for target_c in range(self.n):
                    premises = []
                    for c in range(self.n):
                        if c != target_c:
                            premises.append(("NotValue", r, c, v))
                    self.rules.append((premises, ("Value", r, target_c, v)))
                    
        # Ràng buộc: Mọi giá trị v phải xuất hiện đúng một lần trong mỗi Cột (Luật duy nhất trong Cột)
        for c in range(self.n):
            for v in range(1, self.n + 1):
                for target_r in range(self.n):
                    premises = []
                    for r in range(self.n):
                        if r != target_r:
                            premises.append(("NotValue", r, c, v))
                    self.rules.append((premises, ("Value", target_r, c, v)))

        # Rule: Bất đẳng thức (Inequalities)
        def enforce_less(r1, c1, r2, c2):
            # Nếu r1, c1 < r2, c2 thì r1, c1 không thể là Max, r2, c2 không thể là Min
            self.facts.append(("NotValue", r1, c1, self.n))
            self.facts.append(("NotValue", r2, c2, 1))
            
            # Nếu val(r1, c1) = v1, thì val(r2, c2) không thể <= v1
            for v1 in range(1, self.n + 1):
                for v2 in range(1, v1 + 1):
                    self.rules.append(([("Value", r1, c1, v1)], ("NotValue", r2, c2, v2)))

            # Nếu (r2, c2) KHÔNG THỂ nhận bất kỳ giá trị nào > v, thì (r1, c1) không thể là v
            for v in range(1, self.n):
                premises = [("NotValue", r2, c2, v_prime) for v_prime in range(v + 1, self.n + 1)]
                self.rules.append((premises, ("NotValue", r1, c1, v)))

            # Nếu (r1, c1) KHÔNG THỂ nhận bất kỳ giá trị nào < v, thì (r2, c2) không thể là v
            for v in range(2, self.n + 1):
                premises = [("NotValue", r1, c1, v_prime) for v_prime in range(1, v)]
                self.rules.append((premises, ("NotValue", r2, c2, v)))

            # Nếu val(r2, c2) = v2, thì val(r1, c1) không thể >= v2
            for v2 in range(1, self.n + 1):
                for v1 in range(v2, self.n + 1):
                    self.rules.append(([("Value", r2, c2, v2)], ("NotValue", r1, c1, v1)))
        
        for r, c in self.less_h:
            enforce_less(r, c, r, c + 1) # (r, c) < (r, c+1)
        for r, c in self.greater_h:
            enforce_less(r, c + 1, r, c) # (r, c) > (r, c+1) <=> (r, c+1) < (r, c)
        
        for r, c in self.less_v:
            enforce_less(r, c, r + 1, c) # (r, c) < (r+1, c)
        for r, c in self.greater_v:
            enforce_less(r + 1, c, r, c) # (r, c) > (r+1, c) <=> (r+1, c) < (r, c)
        
        # 1. Empty Domain (Miền giá trị rỗng): 
        # Nếu một ô bị loại trừ tất cả các số từ 1 đến N -> Mâu thuẫn
        for r in range(self.n):
            for c in range(self.n):
                premises = [("NotValue", r, c, v) for v in range(1, self.n + 1)]
                self.rules.append((premises, ("Contradiction",)))
                
        # 2. No Place (Hết chỗ trống):
        # Nếu một số v không thể đặt vào bất kỳ ô nào trên HÀNG r -> Mâu thuẫn
        for r in range(self.n):
            for v in range(1, self.n + 1):
                premises = [("NotValue", r, c, v) for c in range(self.n)]
                self.rules.append((premises, ("Contradiction",)))
                
        # Nếu một số v không thể đặt vào bất kỳ ô nào trên CỘT c -> Mâu thuẫn
        for c in range(self.n):
            for v in range(1, self.n + 1):
                premises = [("NotValue", r, c, v) for r in range(self.n)]
                self.rules.append((premises, ("Contradiction",)))

        # 3. Direct Conflict (Xung đột trực tiếp):
        # Vừa là Value vừa là NotValue ở cùng một ô
        for r in range(self.n):
            for c in range(self.n):
                for v in range(1, self.n + 1):
                    self.rules.append(([("Value", r, c, v), ("NotValue", r, c, v)], ("Contradiction",)))
                    
        # Một ô chứa 2 giá trị Value khác nhau
        for r in range(self.n):
            for c in range(self.n):
                for v1 in range(1, self.n + 1):
                    for v2 in range(1, self.n + 1):
                        if v1 != v2:
                            self.rules.append(([("Value", r, c, v1), ("Value", r, c, v2)], ("Contradiction",)))

        # 4. Inequality Contradiction (Vi phạm bất đẳng thức):
        # Hàm kiểm tra: Nếu A < B mà thực tế Value(A) >= Value(B) -> Mâu thuẫn
        def enforce_inequality_contradiction(r1, c1, r2, c2):
            for v1 in range(1, self.n + 1):
                for v2 in range(1, self.n + 1):
                    if v1 >= v2:
                        self.rules.append(([("Value", r1, c1, v1), ("Value", r2, c2, v2)], ("Contradiction",)))

        for r, c in self.less_h:
            enforce_inequality_contradiction(r, c, r, c + 1)
        for r, c in self.greater_h:
            enforce_inequality_contradiction(r, c + 1, r, c)
        for r, c in self.less_v:
            enforce_inequality_contradiction(r, c, r + 1, c)
        for r, c in self.greater_v:
            enforce_inequality_contradiction(r + 1, c, r, c)