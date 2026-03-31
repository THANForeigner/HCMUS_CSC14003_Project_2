def read_input(input_file):
    """
    Read Futoshiki puzzle input from file.

    Input format:
    - Line 1: n (grid size)
    - Lines 2 to n+1: Initial grid (n x n) with 0 for empty cells
    - Next lines: Horizontal constraints (length n-1) and Vertical constraints (length n)

    Args:
        input_file: Path to input file

    Returns:
        Tuple of (size, grid, [h_constraints, v_constraints])
    """

    def get_clean_lines(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                yield line.replace(',', ' ')

    # Khởi tạo generator đọc file
    lines_gen = get_clean_lines(input_file)

    try:
        # Parse grid size
        size = int(next(lines_gen))

        # Parse initial grid
        grid = []
        for _ in range(size):
            row = list(map(int, next(lines_gen).split()))
            grid.append(row)

        # Parse constraints flexibly based on line lengths
        h_constraints_raw = []
        v_constraints_raw = []

        # Đọc tất cả các dòng dữ liệu sạch còn lại
        for line in lines_gen:
            row = list(map(int, line.split()))
            if len(row) == size - 1:
                h_constraints_raw.append(row)
            elif len(row) == size:
                v_constraints_raw.append(row)

    except StopIteration:
        # Xử lý trường hợp file bị thiếu dòng so với dự kiến
        pass

    # Ensure h_constraints has exactly `size` rows
    h_constraints = []
    for r in range(size):
        if r < len(h_constraints_raw):
            h_constraints.append(h_constraints_raw[r])
        else:
            # Lưu ý: Horizontal constraints có độ dài là (size - 1)
            h_constraints.append([0] * (size - 1))

            # Ensure v_constraints has exactly `size - 1` rows
    v_constraints = []
    for r in range(size - 1):
        if r < len(v_constraints_raw):
            v_constraints.append(v_constraints_raw[r])
        else:
            v_constraints.append([0] * size)

    constraint = [h_constraints, v_constraints]

    return size, grid, constraint

def format_output(solution, h_constraints, v_constraints):
    n = len(solution)
    output_lines = []

    for row_idx in range(n):
        # Add the grid row with horizontal constraints
        row_str = ""
        for col_idx in range(n):
            row_str += str(solution[row_idx, col_idx])

            # Add horizontal constraint if not the last column
            if col_idx < n - 1:
                constraint = h_constraints[row_idx][col_idx]
                if constraint == 1:
                    row_str += " < "
                elif constraint == -1:
                    row_str += " > "
                else:
                    row_str += "   "

        output_lines.append(row_str)

        # Add vertical constraints row if not the last row
        if row_idx < n - 1:
            v_row_str = ""
            for col_idx in range(n):
                constraint = v_constraints[row_idx][col_idx]
                if constraint == 1:
                    v_row_str += "^"
                elif constraint == -1:
                    v_row_str += "v"
                else:
                    v_row_str += " "

                # Add spacing between constraint positions
                if col_idx < n - 1:
                    v_row_str += "   "

            output_lines.append(v_row_str)

    return "\n".join(output_lines)


def write_output(output_file, solution, h_constraints, v_constraints):
    formatted = format_output(solution, h_constraints, v_constraints)

    with open(output_file, 'w') as f:
        f.write(formatted)
