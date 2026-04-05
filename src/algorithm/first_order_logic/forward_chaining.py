import sys
from pathlib import Path

# Add project root to sys.path to allow running as script or importing
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.algorithm.futoshiki_solver import futoshiki_solver
from src.algorithm.first_order_logic.kb import FutoshikiKB

class forward_chainning(futoshiki_solver):
    def __init__(self, size, grid, constraint):
        super().__init__(size, grid, constraint)
        h_constraints, v_constraints = constraint[0], constraint[1]
        self.kb = FutoshikiKB.from_input(size, grid, h_constraints, v_constraints)

    def forward_chain(self):
        self.kb.apply_a9_enforce_clues()
        changed = True
        while changed:
            changed = False
            changed |= self.kb.apply_a3_a4_uniqueness()
            changed |= self.kb.apply_a5_to_a8_constraints()

        is_solved = all(len(self.kb.domains[i][j]) == 1 for i in range(self.kb.n) for j in range(self.kb.n))
        is_valid = all(len(self.kb.domains[i][j]) > 0 for i in range(self.kb.n) for j in range(self.kb.n))

        if not is_valid:
            status = "Contradiction"
        elif is_solved:
            status = "Solved"
        else:
            status = "Incomplete"
            
        return status, self.kb.domains

    def solve(self):
        status, domains = self.forward_chain()
        if status == "Solved":
            self.solution = [[list(self.kb.domains[i][j])[0] for j in range(self.size)] for i in range(self.size)]
        return status, domains

if __name__ == "__main__":
    from src.main import read_input

    if len(sys.argv) > 1:
        puzzle_id = sys.argv[1]
    else:
        puzzle_id = "01"

    base_path = Path(__file__).parent.parent.parent.parent
    input_file = base_path / "inputs" / f"input-{puzzle_id}.txt"

    size, grid, constraint = read_input(input_file)
    h_constraints, v_constraints = constraint[0], constraint[1]

    solver = forward_chainning(size, grid, constraint)
    status, domains = solver.solve()

    print(f"Status: {status}")
    print(solver.kb.format_output(h_constraints, v_constraints))
