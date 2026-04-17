class Node:
    def __init__(self):
        self.L = self
        self.R = self
        self.U = self
        self.D = self
        self.C = None
        self.row_id = None

class ColumnNode(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.C = self
        self.sum = 0

class DancingLink:
    def __init__(self):
        self.root = ColumnNode("Root")
        self.row_ids = []
        self.lt_pairs = None
        self.n = 0
        self.m = 0

    def insert(self, matrix):
        n = self.n = len(matrix)
        m = self.m = len(matrix[0])
        colum = []
        for i in range(m):
            col = ColumnNode(f"C{i + 1}")
            col.L = self.root.L
            col.R = self.root
            self.root.L.R = col
            self.root.L = col
            colum.append(col)

        for i in range(n):
            FirstNodeInRow = None
            for j in range(m):
                col_header = colum[j]
                if matrix[i][j] == 0:
                    continue
                newNode = Node()
                newNode.row_id = self.row_ids[i]
                newNode.C = colum[j]

                # Cập nhật Up/Down
                newNode.U = col_header.U
                newNode.D = col_header
                col_header.U.D = newNode
                col_header.U = newNode
                col_header.sum += 1

                # Cập nhật Left/Right
                if FirstNodeInRow is None:
                    FirstNodeInRow = newNode
                else:
                    newNode.L = FirstNodeInRow.L
                    newNode.R = FirstNodeInRow
                    FirstNodeInRow.L.R = newNode
                    FirstNodeInRow.L = newNode

    def cover(self, ColumRemove):
        ColumRemove.R.L = ColumRemove.L
        ColumRemove.L.R = ColumRemove.R

        col = ColumRemove.D
        while col != ColumRemove:
            row = col.R
            while row != col:
                row.D.U = row.U
                row.U.D = row.D
                row.C.sum -= 1
                row = row.R
            col = col.D

    def uncover(self, ColumRemove):
        col = ColumRemove.U
        while col != ColumRemove:
            row = col.L
            while row != col:
                row.C.sum += 1
                row.D.U = row
                row.U.D = row
                row = row.L
            col = col.U
        ColumRemove.R.L = ColumRemove
        ColumRemove.L.R = ColumRemove

    def choose_column(self):
        col = self.root.R
        ans = col
        while col != self.root:
            if ans.sum > col.sum:
                ans = col
            col = col.R
        return ans

    def search(self, k, stack):
        if self.root.R == self.root:
            self.print_smart_solution(stack)
            return

        if hasattr(self, 'nodes_expanded'):
            self.nodes_expanded += 1
        c = self.choose_column()
        self.cover(c)
        col = c.D
        while col != c:
            if hasattr(self, 'nodes_generated'):
                self.nodes_generated += 1
            stack.append(col)

            # Kiểm tra class DLXFutoshiki có hàm 'check_futoshiki' không và kiểm tra điều kiện cộng thêm này
            if hasattr(self, 'check_futoshiki') and getattr(self, 'check_futoshiki')(stack) == False:
                stack.pop()
                col = col.D
                continue

            row = col.R
            while row != col:
                self.cover(row.C)
                row = row.R

            self.search(k + 1, stack)

            last_node = stack.pop()
            if hasattr(self, 'uncheck_futoshiki'):
                getattr(self, 'uncheck_futoshiki')(last_node)

            row = col.L
            while row != col:
                self.uncover(row.C)
                row = row.L

            col = col.D
        self.uncover(c)

    def print_smart_solution(self, solution_nodes):
        print("\n🎉 TÌM THẤY ĐÁP ÁN:")

        labels = [node.row_id for node in solution_nodes]
        print(f"Các hàng được chọn để Exact Cover: {', '.join(labels)}")

        is_board_format = all('_' in label for label in labels)

        if is_board_format:
            try:
                max_r = max_c = 0
                parsed_cells = []

                # Phân tích từng chuỗi
                for label in labels:
                    parts = label.split('_')
                    r = int(parts[0][1:])
                    c = int(parts[1][1:])
                    v = int(parts[2][1:])
                    parsed_cells.append((r, c, v))
                    if r > max_r: max_r = r
                    if c > max_c: max_c = c

                # Tạo bàn cờ theo kích thước linh hoạt
                board = [[0] * (max_c + 1) for _ in range(max_r + 1)]
                for r, c, v in parsed_cells:
                    board[r][c] = v

                # In ra màn hình
                print("\nBàn cờ chi tiết:")
                separator = "-" * ((max_c + 1) * 4 + 1)
                print(separator)
                for row in board:
                    row_str = " | ".join(str(val) for val in row)
                    print(f"| {row_str} |")
                    print(separator)
            except Exception as e:
                print(f"Không thể vẽ bàn cờ do lỗi format: {e}")
        else:
            # SỬA TẠI ĐÂY: Khôi phục và in ra ma trận 2D
            print("\nMa trận 2D của nghiệm (các hàng được chọn):")
            solution_matrix = [[0] * self.m for _ in range(self.n)]

            for node in solution_nodes:
                r_idx = int(node.row_id[1:]) - 1  # Lấy số hàng từ "R1", "R2"...
                curr = node
                while True:
                    c_idx = int(curr.C.name[1:]) - 1  # Lấy số cột từ "C1", "C2"...
                    solution_matrix[r_idx][c_idx] = 1
                    curr = curr.R
                    if curr == node:
                        break

            # In ma trận
            for row in solution_matrix:
                print(row)

    def debug_print_columns(self):
        print("\n=== DEBUG: CÁC CỘT (CHIỀU DỌC) ===")
        curr_col = self.root.R
        if curr_col == self.root:
            print("Lưới đang trống!")
            return

        while curr_col != self.root:
            print(f"Cột {curr_col.name} (sum={curr_col.sum}): ", end="")
            curr_node = curr_col.D
            while curr_node != curr_col:
                print(f"[{curr_node.row_id}] ", end="")
                curr_node = curr_node.D
            print()
            curr_col = curr_col.R

    def debug_print_rows(self):
        print("\n=== DEBUG: CÁC HÀNG (CHIỀU NGANG) ===")
        visited_rows = set()

        curr_col = self.root.R
        while curr_col != self.root:
            curr_node = curr_col.D
            while curr_node != curr_col:
                if curr_node.row_id not in visited_rows:
                    visited_rows.add(curr_node.row_id)
                    print(f"Hàng {curr_node.row_id} chứa các Node tại: ", end="")

                    start_node = curr_node
                    print(f"[{start_node.C.name}] ", end="")

                    step_node = start_node.R
                    while step_node != start_node:
                        print(f"[{step_node.C.name}] ", end="")
                        step_node = step_node.R
                    print()
                curr_node = curr_node.D
            curr_col = curr_col.R

    def debugTree(self):
        self.debug_print_columns()
        self.debug_print_rows()

if __name__ == "__main__":
    # Ma trận tiệc Potluck (5 Hàng, 4 Cột)
    matrix1 = [
        [1, 0, 0, 1],  # R1
        [1, 0, 0, 0],  # R2
        [0, 1, 1, 0],  # R3
        [0, 1, 0, 1],  # R4
        [0, 0, 1, 0]  # R5
    ]

    # 1. Xây lưới
    root = DancingLink()
    root.insert(matrix1)

    # 2. Chạy thuật toán
    stack = []
    root.search(0, stack)
