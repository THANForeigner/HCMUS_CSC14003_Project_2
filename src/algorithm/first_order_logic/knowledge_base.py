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
        # Initialize initial Facts 
        for r, c, v in self.given_clues:
            self.facts.append(("Value", r, c, v))
            
        # Initialize Rules
        # Each rule is a tuple: (premises, conclusion)
        # premises is a list of atoms, conclusion is an atom. Atom: ("Value", r, c, v) or ("NotValue", r, c, v)
        
        # Rule: Row Uniqueness constraint
        # If cell (r, c1) has value v -> cell (r, c2) will Not have value v
        for r in range(self.n):
            for v in range(1, self.n + 1):
                for c1 in range(self.n):
                    for c2 in range(self.n):
                        if c1 != c2:
                            self.rules.append(([("Value", r, c1, v)], ("NotValue", r, c2, v)))
                            
        # Rule: Column Uniqueness constraint
        # If cell (r1, c) has value v -> cell (r2, c) will Not have value v
        for c in range(self.n):
            for v in range(1, self.n + 1):
                for r1 in range(self.n):
                    for r2 in range(self.n):
                        if r1 != r2:
                            self.rules.append(([("Value", r1, c, v)], ("NotValue", r2, c, v)))

        # Rule: Cell Uniqueness (maximum one value per cell)
        # If cell (r, c) has value v1 -> cell (r, c) will Not have value v2
        for r in range(self.n):
            for c in range(self.n):
                for v1 in range(1, self.n + 1):
                    for v2 in range(1, self.n + 1):
                        if v1 != v2:
                            self.rules.append(([("Value", r, c, v1)], ("NotValue", r, c, v2)))
                            
        # Rule: Minimum one value per cell 
        # If N-1 values are all NotValue -> the remaining value must be Value
        for r in range(self.n):
            for c in range(self.n):
                for target_v in range(1, self.n + 1):
                    premises = []
                    for other_v in range(1, self.n + 1):
                        if other_v != target_v:
                            premises.append(("NotValue", r, c, other_v))
                    self.rules.append((premises, ("Value", r, c, target_v)))

        # Constraint: Every value v must appear exactly once in each Row (Row uniqueness law)
        # If N-1 cells in a row do not contain value v -> the remaining cell must have value v
        for r in range(self.n):
            for v in range(1, self.n + 1):
                for target_c in range(self.n):
                    premises = []
                    for c in range(self.n):
                        if c != target_c:
                            premises.append(("NotValue", r, c, v))
                    self.rules.append((premises, ("Value", r, target_c, v)))
                    
        # Constraint: Every value v must appear exactly once in each Column (Column uniqueness law)
        for c in range(self.n):
            for v in range(1, self.n + 1):
                for target_r in range(self.n):
                    premises = []
                    for r in range(self.n):
                        if r != target_r:
                            premises.append(("NotValue", r, c, v))
                    self.rules.append((premises, ("Value", target_r, c, v)))

        # Rule: Inequalities
        def enforce_less(r1, c1, r2, c2):
            # If (r1, c1) < (r2, c2) then (r1, c1) cannot be Max, (r2, c2) cannot be Min
            self.facts.append(("NotValue", r1, c1, self.n))
            self.facts.append(("NotValue", r2, c2, 1))
            
            # If val(r1, c1) = v1, then val(r2, c2) cannot be <= v1
            for v1 in range(1, self.n + 1):
                for v2 in range(1, v1 + 1):
                    self.rules.append(([("Value", r1, c1, v1)], ("NotValue", r2, c2, v2)))

            # If (r2, c2) CANNOT take any value > v, then (r1, c1) cannot be v
            for v in range(1, self.n):
                premises = [("NotValue", r2, c2, v_prime) for v_prime in range(v + 1, self.n + 1)]
                self.rules.append((premises, ("NotValue", r1, c1, v)))

            # If (r1, c1) CANNOT take any value < v, then (r2, c2) cannot be v
            for v in range(2, self.n + 1):
                premises = [("NotValue", r1, c1, v_prime) for v_prime in range(1, v)]
                self.rules.append((premises, ("NotValue", r2, c2, v)))

            # If val(r2, c2) = v2, then val(r1, c1) cannot be >= v2
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
        
        # 1. Empty Domain: 
        # If a cell is excluded from all numbers from 1 to N -> Contradiction
        for r in range(self.n):
            for c in range(self.n):
                premises = [("NotValue", r, c, v) for v in range(1, self.n + 1)]
                self.rules.append((premises, ("Contradiction",)))
                
        # 2. No Place:
        # If a value v cannot be placed in any cell in ROW r -> Contradiction
        for r in range(self.n):
            for v in range(1, self.n + 1):
                premises = [("NotValue", r, c, v) for c in range(self.n)]
                self.rules.append((premises, ("Contradiction",)))
                
        # If a value v cannot be placed in any cell in COLUMN c -> Contradiction
        for c in range(self.n):
            for v in range(1, self.n + 1):
                premises = [("NotValue", r, c, v) for r in range(self.n)]
                self.rules.append((premises, ("Contradiction",)))

        # 3. Direct Conflict:
        # Both Value and NotValue at the same cell
        for r in range(self.n):
            for c in range(self.n):
                for v in range(1, self.n + 1):
                    self.rules.append(([("Value", r, c, v), ("NotValue", r, c, v)], ("Contradiction",)))
                    
        # A cell contains 2 different Value values
        for r in range(self.n):
            for c in range(self.n):
                for v1 in range(1, self.n + 1):
                    for v2 in range(1, self.n + 1):
                        if v1 != v2:
                            self.rules.append(([("Value", r, c, v1), ("Value", r, c, v2)], ("Contradiction",)))

        # 4. Inequality Contradiction:
        # Check function: If A < B but actually Value(A) >= Value(B) -> Contradiction
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