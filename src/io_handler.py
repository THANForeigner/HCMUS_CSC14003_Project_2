import os
import re

data = {
    4: {
        'trivial': {
                1: "test/input/size4_trivial_1.txt",
                2: "test/input/size4_trivial_2.txt",
                3: "test/input/size4_trivial_3.txt",
            },
        'easy':
            {
                1: "test/input/size4_easy_1.txt",
                2: "test/input/size4_easy_2.txt",
                3: "test/input/size4_easy_3.txt",
            },
        'tricky': {
                1: "test/input/size4_tricky_1.txt",
                2: "test/input/size4_tricky_2.txt",
                3: "test/input/size4_tricky_3.txt",
            },
        'extreme': {
                1: "test/input/size4_extreme_1.txt",
                2: "test/input/size4_extreme_2.txt",
                3: "test/input/size4_extreme_3.txt",
            }
    },
    5:{
        'trivial': {
                1: "test/input/size5_trivial_1.txt",
                2: "test/input/size5_trivial_2.txt",
                3: "test/input/size5_trivial_3.txt",
            },
        'easy': {
                1: "test/input/size5_easy_1.txt",
                2: "test/input/size5_easy_2.txt",
                3: "test/input/size5_easy_3.txt",
            },
        'tricky': {
                1: "test/input/size5_tricky_1.txt",
                2: "test/input/size5_tricky_2.txt",
                3: "test/input/size5_tricky_3.txt",
            },
        'extreme': {
                1: "test/input/size5_extreme_1.txt",
                2: "test/input/size5_extreme_2.txt",
                3: "test/input/size5_extreme_3.txt",
            }
    },
    6: {
        'trivial': {
                1: "test/input/size6_trivial_1.txt",
                2: "test/input/size6_trivial_2.txt",
                3: "test/input/size6_trivial_3.txt",
            },
        'easy': {
                1: "test/input/size6_easy_1.txt",
                2: "test/input/size6_easy_2.txt",
                3: "test/input/size6_easy_3.txt",
            },
        'tricky': {
                1: "test/input/size6_tricky_1.txt",
                2: "test/input/size6_tricky_2.txt",
                3: "test/input/size6_tricky_3.txt",
            },
        'extreme': {
                1: "test/input/size6_extreme_1.txt",
                2: "test/input/size6_extreme_2.txt",
                3: "test/input/size6_extreme_3.txt",
            }
    },
    7: {
        'trivial': {
                1: "test/input/size7_trivial_1.txt",
                2: "test/input/size7_trivial_2.txt",
                3: "test/input/size7_trivial_3.txt",
            },
        'easy': {
                1: "test/input/size7_easy_1.txt",
                2: "test/input/size7_easy_2.txt",
                3: "test/input/size7_easy_3.txt",
            },
        'tricky': {
                1: "test/input/size7_tricky_1.txt",
                2: "test/input/size7_tricky_2.txt",
                3: "test/input/size7_tricky_3.txt",
            },
        'extreme': {
                1: "test/input/size7_extreme_1.txt",
                2: "test/input/size7_extreme_2.txt",
                3: "test/input/size7_extreme_3.txt",
            }
    },
    8: {
        'trivial': {
                1: "test/input/size8_trivial_1.txt",
                2: "test/input/size8_trivial_2.txt",
                3: "test/input/size8_trivial_3.txt",
            },
        'easy': {
                1: "test/input/size8_easy_1.txt",
                2: "test/input/size8_easy_2.txt",
                3: "test/input/size8_easy_3.txt",
            },
        'tricky': {
                1: "test/input/size8_tricky_1.txt",
                2: "test/input/size8_tricky_2.txt",
                3: "test/input/size8_tricky_3.txt",
            },
        'extreme': {
                1: "test/input/size8_extreme_1.txt",
                2: "test/input/size8_extreme_2.txt",
                3: "test/input/size8_extreme_3.txt",
            }
    },
    9: {
        'trivial': {
                1: "test/input/size9_trivial_1.txt",
                2: "test/input/size9_trivial_2.txt",
                3: "test/input/size9_trivial_3.txt",
            },
        'easy': {
                1: "test/input/size9_easy_1.txt",
                2: "test/input/size9_easy_2.txt",
                3: "test/input/size9_easy_3.txt",
            },
        'tricky': {
                1: "test/input/size9_tricky_1.txt",
                2: "test/input/size9_tricky_2.txt",
                3: "test/input/size9_tricky_3.txt",
            },
        'extreme': {
                1: "test/input/size9_extreme_1.txt",
                2: "test/input/size9_extreme_2.txt",
                3: "test/input/size9_extreme_3.txt",
            }
    }
}

def get_test_inputs():
    return data

def get_input_filename(size, difficulty, puzzle_id):
    """
    Get filename from data dictionary based on components.
    """
    try:
        path = data[int(size)][difficulty][int(puzzle_id)]
        return os.path.basename(path)
    except (KeyError, TypeError, ValueError):
        return f"size{size}_{difficulty}_{puzzle_id}.txt"

def get_input_path(base_dir, size, difficulty, puzzle_id):
    """
    Get full path from data dictionary.
    """
    try:
        rel_path = data[int(size)][difficulty][int(puzzle_id)]
        return os.path.join(base_dir, rel_path)
    except (KeyError, TypeError, ValueError):
        filename = f"size{size}_{difficulty}_{puzzle_id}.txt"
        return os.path.join(base_dir, "test", "input", filename)

def read_input(input_file):

    def get_clean_lines(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                yield line.replace(',', ' ')

    # Initialize file reading generator
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

        # Read all remaining clean data lines
        for line in lines_gen:
            row = list(map(int, line.split()))
            if len(row) == size - 1:
                h_constraints_raw.append(row)
            elif len(row) == size:
                v_constraints_raw.append(row)

    except StopIteration:
        # Handle case where file has fewer lines than expected
        pass

    # Ensure h_constraints has exactly `size` rows
    h_constraints = []
    for r in range(size):
        if r < len(h_constraints_raw):
            h_constraints.append(h_constraints_raw[r])
        else:
            # Note: Horizontal constraints have a length of (size - 1)
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
            row_str += str(solution[row_idx][col_idx])

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
