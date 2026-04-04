class FutoshikiKB:
    def __init__(self, n, given_clues, less_h, greater_h, less_v, greater_v):
        self.n = n
        self.domains = [[set(range(1, n + 1)) for _ in range(n)] for _ in range(n)]
        self.given_clues = given_clues
        self.less_h = less_h
        self.greater_h = greater_h
        self.less_v = less_v
        self.greater_v = greater_v

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

    def apply_a9_enforce_clues(self):
        for i, j, v in self.given_clues:
            self.domains[i][j] = {v}

    def apply_a3_a4_uniqueness(self):
        changed = False
        for i in range(self.n):
            for j in range(self.n):
                if len(self.domains[i][j]) == 1:
                    val = list(self.domains[i][j])[0]
                    for k in range(self.n):
                        if k != j and val in self.domains[i][k]:
                            self.domains[i][k].remove(val)
                            changed = True
                    for k in range(self.n):
                        if k != i and val in self.domains[k][j]:
                            self.domains[k][j].remove(val)
                            changed = True
        return changed

    def enforce_inequality(self, r1, c1, r2, c2):
        changed = False
        dom_A = self.domains[r1][c1]
        dom_B = self.domains[r2][c2]

        if not dom_A or not dom_B:
            return False

        max_B = max(dom_B)
        min_A = min(dom_A)

        to_remove_A = {v for v in dom_A if v >= max_B}
        if to_remove_A:
            self.domains[r1][c1] = dom_A - to_remove_A
            changed = True

        to_remove_B = {v for v in dom_B if v <= min_A}
        if to_remove_B:
            self.domains[r2][c2] = dom_B - to_remove_B
            changed = True

        return changed

    def apply_a5_to_a8_constraints(self):
        changed = False
        for i, j in self.less_h:
            changed |= self.enforce_inequality(i, j, i, j + 1)
        for i, j in self.greater_h:
            changed |= self.enforce_inequality(i, j + 1, i, j)
        for i, j in self.less_v:
            changed |= self.enforce_inequality(i, j, i + 1, j)
        for i, j in self.greater_v:
            changed |= self.enforce_inequality(i + 1, j, i, j)
        return changed

    def forward_chain(self):
        self.apply_a9_enforce_clues()
        changed = True
        while changed:
            changed = False
            changed |= self.apply_a3_a4_uniqueness()
            changed |= self.apply_a5_to_a8_constraints()

        is_solved = all(len(self.domains[i][j]) == 1 for i in range(self.n) for j in range(self.n))
        is_valid = all(len(self.domains[i][j]) > 0 for i in range(self.n) for j in range(self.n))

        if not is_valid:
            return "Contradiction", self.domains
        return "Solved" if is_solved else "Incomplete", self.domains

    def format_output(self, h_constraints, v_constraints):
        output_lines = []
        for row_idx in range(self.n):
            row_str = ""
            for col_idx in range(self.n):
                val = list(self.domains[row_idx][col_idx])[0] if len(self.domains[row_idx][col_idx]) == 1 else 0
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


if __name__ == "__main__":
    from main import read_input
    from pathlib import Path
    import sys

    if len(sys.argv) > 1:
        puzzle_id = sys.argv[1]
    else:
        puzzle_id = "01"

    base_path = Path(__file__).parent.parent
    input_file = base_path / "inputs" / f"input-{puzzle_id}.txt"

    size, grid, constraint = read_input(input_file)
    h_constraints, v_constraints = constraint[0], constraint[1]

    kb = FutoshikiKB.from_input(size, grid, h_constraints, v_constraints)
    status, domains = kb.forward_chain()

    print(f"Status: {status}")
    print(kb.format_output(h_constraints, v_constraints))
