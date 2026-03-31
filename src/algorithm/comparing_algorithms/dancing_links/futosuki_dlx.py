from dancing_links import DancingLink, Node, ColumnNode

def build_matrix(matrix):
    n = len(matrix)
    # Tổng số cột: N*N (Ô) + N*N (Hàng) + N*N (Cột)
    num_cols = 3 * (n * n)
    ans = []
    row_ids = []
    for r in range(n):
        for c in range(n):
            if matrix[r][c] != 0:
                row = [0] * num_cols
                i = matrix[r][c]
                row_ids.append(f"R{r}_C{c}_V{i}")
                row[r * n + c] = 1
                row[n * n + r * n + (i - 1)] = 1
                row[2 * n * n + c * n + (i - 1)] = 1
                ans.append(row)
                continue
            for i in range(1, n + 1):
                # giải quyết trạng thái tại ô (r, c) với việc điền số i vào thì điều gì xảy ra
                row_ids.append(f"R{r}_C{c}_V{i}")
                row = [0] * num_cols

                #tai o (r, c) dien i
                index = r * n + c
                row[index] = 1

                #hang c da co o i
                # di qua n * n(o), r * n: moi hang dung n index.
                index = n * n + r * n + (i - 1)
                row[index] = 1

                #tuong tu cho cot
                index = 2 * n * n + c * n + (i - 1)
                row[index] = 1
                ans.append(row)

    return ans, row_ids

if __name__ == "__main__":
    matrix_default = [
        [3, 0, 0],
        [0, 3, 0],
        [0, 2, 0]
    ]
    root = DancingLink()
    matrix, root.row_ids = build_matrix(matrix_default)
    root.insert(matrix)
    # root.debugTree()
    stack = []
    root.search(0, stack)