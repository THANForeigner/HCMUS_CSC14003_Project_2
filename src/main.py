import os
import sys
from pathlib import Path
import numpy as np

from algorithm.comparing_algorithms.dancing_links.dlx_futoshiki import DLXFutoshiki
from io_handler import read_input, write_output

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from algorithm.comparing_algorithms.artificial_bee_colony import ABC


def read_input(input_file):
    """
    Read Futoshiki puzzle input from file.
    
    Input format:
    - Line 1: N (grid size)
    - Lines 2 to N+1: Initial grid (N x N) with 0 for empty, 1..N for pre-filled
    - Next N lines: Horizontal constraints (N-1 values each: 0=none, 1='<', -1='>')
    - Next N-1 lines: Vertical constraints (N values each: 0=none, 1='<', -1='>')
    
    Args:
        input_file: Path to input file
    
    Returns:
        Tuple of (size, grid, [h_constraints, v_constraints])
    """
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]
    
    size = int(lines[0])
    
    grid = []
    for i in range(1, size + 1):
        row = list(map(int, lines[i].replace(' ', '').split(',')))
        grid.append(row)
    
    h_constraints = []
    for i in range(size):
        row = list(map(int, lines[size + 1 + i].replace(' ', '').split(',')))
        h_constraints.append(row)
    
    v_constraints = []
    for i in range(size - 1):
        row = list(map(int, lines[size + 1 + size + i].replace(' ', '').split(',')))
        v_constraints.append(row)
    
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


def main():
    # Get input file from command line or use default
    if len(sys.argv) > 1:
        puzzle_id = sys.argv[1]
    else:
        puzzle_id = "01"
    
    # Construct file paths
    base_path = Path(__file__).parent.parent
    input_file = base_path / "inputs" / f"input-{puzzle_id}.txt"
    output_file = base_path / "outputs" / f"output-{puzzle_id}.txt"
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Reading puzzle from {input_file}")
    
    # Read input
    size, grid, constraint = read_input(input_file)
    
    print(f"Puzzle size: {size}x{size}")
    print(f"Initial grid:\n{np.array(grid)}")
    
    # Solve using ABC algorithm
    # print("\nSolving with Artificial Bee Colony algorithm...")
    # solver = ABC(size, grid, constraint, swarm_size=500, limit=10, max_iteration=10000)
    # solution = solver.solve()

    # Solve using GA algorithm
    # print("\nSolving with Genetic Algorithm...")
    # solver = GA(size, grid, constraint, pop_size=200, mutation_rate=0.1, crossover_rate=0.9, elite_size=10, tournament_size=3, max_iteration=1000)
    # solution = solver.solve()
    solver = DLXFutoshiki(size, grid, constraint)
    solution = solver.solve()
    
    print(f"Solution:\n{solution}")
    
    # Format and write output
    print(f"\nWriting solution to {output_file}")
    write_output(output_file, solution, constraint[0], constraint[1])

    print("Done!")


if __name__ == "__main__":
    main()
