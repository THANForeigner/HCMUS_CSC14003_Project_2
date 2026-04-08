import os
import sys
from pathlib import Path
import numpy as np

# Ensure src is in the system path to allow module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def read_input(input_file):
    """Read Futoshiki puzzle input from file."""
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]
    
    size = int(lines[0])
    
    grid = []
    for i in range(1, size + 1):
        row = list(map(int, lines[i].replace(',', ' ').split()))
        grid.append(row)
    
    h_constraints = []
    for i in range(size):
        row = list(map(int, lines[size + 1 + i].replace(',', ' ').split()))
        h_constraints.append(row)
    
    v_constraints = []
    for i in range(size - 1):
        row = list(map(int, lines[size + 1 + size + i].replace(',', ' ').split()))
        v_constraints.append(row)
    
    constraint = [h_constraints, v_constraints]
    
    return size, grid, constraint

def format_output(solution, h_constraints, v_constraints):
    n = len(solution)
    output_lines = []
    
    for row_idx in range(n):
        row_str = ""
        for col_idx in range(n):
            row_str += str(solution[row_idx][col_idx])
            
            if col_idx < n - 1:
                constraint = h_constraints[row_idx][col_idx]
                if constraint == 1:
                    row_str += " < "
                elif constraint == -1:
                    row_str += " > "
                else:
                    row_str += "   "
        
        output_lines.append(row_str)
        
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
                
                if col_idx < n - 1:
                    v_row_str += "   "
            
            output_lines.append(v_row_str)
    
    return "\n".join(output_lines)

def write_output(output_file, solution, h_constraints, v_constraints):
    formatted = format_output(solution, h_constraints, v_constraints)
    with open(output_file, 'w') as f:
        f.write(formatted)

def main():
    if len(sys.argv) > 1:
        puzzle_id = sys.argv[1]
    else:
        puzzle_id = "01"
    
    base_path = Path(__file__).parent.parent
    input_file = base_path / "inputs" / f"input-{puzzle_id}.txt"
    output_file = base_path / "outputs" / f"output-{puzzle_id}.txt"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Reading puzzle from {input_file}")
    size, grid, constraint = read_input(input_file)
    
    print(f"Puzzle size: {size}x{size}")
    print(f"Initial grid:\n{np.array(grid)}")
    
    from algorithm.first_order_logic.forward_chaining import forward_chaining
    from algorithm.first_order_logic.fc_no_backtrack import fc_no_backtrack
    from algorithm.first_order_logic.backward_chaining import backward_chaining
    import time
    from algorithm.first_order_logic.bc_no_backtrack import bc_no_backtrack

    print("\n--- No Backtrack Time Comparison ---")
    
    print("\nSolving with Forward Chaining (No Backtrack)...")
    start_time = time.time()
    solver_fc = forward_chaining(size, grid, constraint)
    status_fc, _ = solver_fc.solve()
    time_fc = time.time() - start_time
    print(f"Status: {status_fc}")
    print(f"Execution Time (FC No Backtrack): {time_fc:.4f} seconds")

    print("\nSolving with Backward Chaining (No Backtrack)...")
    start_time = time.time()
    solver_bc = backward_chaining(size, grid, constraint)
    status_bc, _ = solver_bc.solve()
    time_bc = time.time() - start_time
    print(f"Status: {status_bc}")
    print(f"Execution Time (BC No Backtrack): {time_bc:.4f} seconds")
    
    print(f"\nTime difference: {abs(time_fc - time_bc):.4f} seconds")

    status = status_bc
    solver = solver_bc
    
    print(f"Status: {status}")
    
    solution = np.array(solver.solution)
    
    print(f"Solution:\n{solution}")
    
    print(f"\nWriting solution to {output_file}")
    write_output(output_file, solution, constraint[0], constraint[1])
    print("Done!")

if __name__ == "__main__":
    main()
