import os
import sys
from pathlib import Path
import numpy as np

from algorithm.comparing_algorithms.dancing_links.dlx_futoshiki import DLXFutoshiki
from io_handler import read_input, write_output

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from algorithm.comparing_algorithms.genetic_algorithm import GA

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
