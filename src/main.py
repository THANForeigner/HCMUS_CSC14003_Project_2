import numpy as np
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from algorithm.comparing_algorithms.artificial_bee_colony import ABC
from algorithm.comparing_algorithms.pure_astar import PureAStarSolver
from algorithm.comparing_algorithms.astar import AStarFutoshiki


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
        values = list(map(int, lines[size + 1 + i].replace(' ', '').split(',')))
        h_constraints.append(values[:size-1])
    
    v_constraints = []
    for i in range(size - 1):
        values = list(map(int, lines[size + 1 + size + i].replace(' ', '').split(',')))
        v_constraints.append(values[:size])
    
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
    if len(sys.argv) > 1:
        puzzle_id = sys.argv[1]
    else:
        puzzle_id = "01"
    
    algorithm = sys.argv[2] if len(sys.argv) > 2 else "astar"
    heuristic = sys.argv[3] if len(sys.argv) > 3 else "h1"
    
    base_path = Path(__file__).parent.parent
    input_file = base_path / "inputs" / f"input-{puzzle_id}.txt"
    output_file = base_path / "outputs" / f"output-{puzzle_id}.txt"
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Reading puzzle from {input_file}")
    size, grid, constraint = read_input(input_file)
    
    print(f"Puzzle size: {size}x{size}")
    print(f"Initial grid:\n{np.array(grid)}")
    
    if algorithm == "astar":
        h_names = {'h1': 'Hamming (Blank Cells)', 'h2': 'Constraint Violations', 'h3': 'MRV + AC-3'}
        print(f"\nSolving with A* (Heuristic: {h_names.get(heuristic, heuristic)})...")
        solver = AStarFutoshiki(size, grid, constraint, heuristic)
        solution = solver.solve()
        stats = solver.get_stats()
        
        if solution is not None:
            print(f"Solution found!")
            print(f"Nodes expanded: {stats['nodes_expanded']}")
            print(f"Nodes generated: {stats['nodes_generated']}")
            print(f"Solution:\n{solution}")
            write_output(output_file, solution, constraint[0], constraint[1])
        else:
            print("No solution found.")
    
    elif algorithm == "abc":
        print("\nSolving with Artificial Bee Colony algorithm...")
        solver = ABC(size, grid, constraint, swarm_size=500, limit=10, max_iteration=10000)
        solution = solver.solve()
        
        print(f"\nBest fitness achieved: {solver.best_fitness:.4f}")
        print(f"Solution:\n{solution}")
        write_output(output_file, solution, constraint[0], constraint[1])
    
    print(f"\nWriting solution to {output_file}")
    print("Done!")


if __name__ == "__main__":
    main()
