import numpy as np
from .dancing_links import DancingLink, Node, ColumnNode
from ...futoshiki_solver import futoshiki_solver

class DLXFutoshiki(futoshiki_solver, DancingLink):
    def __init__(self, size, grid, constraint):
        futoshiki_solver.__init__(self, size, grid, constraint)
        DancingLink.__init__(self)
        self.n = self.m = self.size = size
        matrix, self.row_ids = self.build_matrix(size, grid)
        self.insert(matrix)
        self.adj_constraints = self.build_adj_constraints(size, constraint)
        self.current_board = [[0] * size for _ in range(size)]

    def build_matrix(self, size, matrix):
        # Tổng số cột: N*N (Ô) + N*N (Hàng) + N*N (Cột)
        num_cols = 3 * (size * size)
        ans = []
        row_ids = []
        for r in range(size):
            for c in range(size):
                if matrix[r][c] != 0:
                    row = [0] * num_cols
                    i = matrix[r][c]
                    row_ids.append(f"R{r}_C{c}_V{i}")
                    row[r * size + c] = 1
                    row[size * size + r * size + (i - 1)] = 1
                    row[2 * size * size + c * size + (i - 1)] = 1
                    ans.append(row)
                    continue
                for i in range(1, size + 1):
                    # giải quyết trạng thái tại ô (r, c) với việc điền số i vào thì điều gì xảy ra
                    row_ids.append(f"R{r}_C{c}_V{i}")
                    row = [0] * num_cols

                    # tai o (r, c) dien i
                    row[r * size + c] = 1

                    # hang c da co o i
                    # di qua size * size(o), r * size: moi hang dung size index.
                    row[size * size + r * size + (i - 1)] = 1

                    # tuong tu cho cot
                    row[2 * size * size + c * size + (i - 1)] = 1
                    ans.append(row)

        return ans, row_ids

    def build_adj_constraints(self, size, constraint):
        h_constraints = constraint[0]
        v_constraints = constraint[1]
        lt_pairs = []
        for r in range(size):
            for c in range(size - 1):
                val = h_constraints[r][c]
                if val == 1:
                    # Trái < Phải
                    lt_pairs.append((r, c, r, c + 1))
                elif val == -1:
                    # Trái > Phải  =>  Phải < Trái
                    lt_pairs.append((r, c + 1, r, c))
        for r in range(size - 1):
            for c in range(size):
                val = v_constraints[r][c]
                if val == 1:
                    # Trên < Dưới
                    lt_pairs.append((r, c, r + 1, c))
                elif val == -1:
                    # Trên > Dưới  =>  Dưới < Trên
                    lt_pairs.append((r + 1, c, r, c))
        adj_constraints = {}
        for r1, c1, r2, c2 in lt_pairs:
            adj_constraints.setdefault((r1, c1), []).append((r2, c2, 1))
            adj_constraints.setdefault((r2, c2), []).append((r1, c1, -1))

        return adj_constraints

    def check_futoshiki(self, stack):
        last_node = stack[-1]

        if not hasattr(last_node, 'rcv'):
            parts = last_node.row_id.split('_')
            last_node.rcv = (int(parts[0][1:]), int(parts[1][1:]), int(parts[2][1:]))
        r, c, v = last_node.rcv

        for r_p, c_p, op in self.adj_constraints.get((r, c), []):
            v_p = self.current_board[r_p][c_p]
            if v_p != 0:
                if op == 1 and not (v < v_p): return False
                if op == -1 and not (v > v_p): return False

        self.current_board[r][c] = v
        return True

    def uncheck_futoshiki(self, node):
        if hasattr(node, 'rcv'):
            r, c, _ = node.rcv
            self.current_board[r][c] = 0

    def print_smart_solution(self, solution_nodes):
        self.solution = np.zeros((self.size, self.size), dtype=int)
        for node in solution_nodes:
            if hasattr(node, 'rcv'):
                r, c, v = node.rcv
            else:
                parts = node.row_id.split('_')
                r, c, v = int(parts[0][1:]), int(parts[1][1:]), int(parts[2][1:])
            self.solution[r, c] = v
        raise StopIteration

    def solve(self):
        self.solution = None
        try:
            self.search(0, [])
        except StopIteration:
            pass
        return self.solution