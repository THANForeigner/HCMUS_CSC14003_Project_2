import threading
import time
from typing import List, Tuple, Optional

class BacktrackSolverSimple:
    def __init__(self, size: int, grid: List[List[int]], constraint: Tuple[List[List[int]], List[List[int]]]):
        self.size = size
        # make a copy
        self.grid = [row[:] for row in grid]
        self.h_constraints, self.v_constraints = constraint
        self.solution = [row[:] for row in self.grid]
        self.nodes_expanded = 0
        self.nodes_generated = 0

    def _is_safe(self, r, c, num):
        # row and column
        for i in range(self.size):
            if self.solution[r][i] == num or self.solution[i][c] == num:
                return False
        # horizontal
        if c > 0 and self.h_constraints[r][c-1] != 0:
            if self.h_constraints[r][c-1] == 1 and num <= self.solution[r][c-1]:
                return False
            if self.h_constraints[r][c-1] == -1 and num >= self.solution[r][c-1]:
                return False
        if c < self.size - 1 and self.h_constraints[r][c] != 0:
            if self.h_constraints[r][c] == 1 and num >= self.solution[r][c+1]:
                return False
            if self.h_constraints[r][c] == -1 and num <= self.solution[r][c+1]:
                return False
        # vertical
        if r > 0 and self.v_constraints and r-1 < len(self.v_constraints) and self.v_constraints[r-1][c] != 0:
            if self.v_constraints[r-1][c] == 1 and num <= self.solution[r-1][c]:
                return False
            if self.v_constraints[r-1][c] == -1 and num >= self.solution[r-1][c]:
                return False
        if r < self.size - 1 and self.v_constraints and r < len(self.v_constraints) and self.v_constraints[r][c] != 0:
            if self.v_constraints[r][c] == 1 and num >= self.solution[r+1][c]:
                return False
            if self.v_constraints[r][c] == -1 and num <= self.solution[r+1][c]:
                return False
        return True

    def _find_next(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.solution[r][c] == 0:
                    return r, c
        return None

    def _backtrack(self):
        loc = self._find_next()
        if loc is None:
            return True
        r, c = loc
        for num in range(1, self.size + 1):
            self.nodes_generated += 1
            if self._is_safe(r, c, num):
                self.solution[r][c] = num
                self.nodes_expanded += 1
                if self._backtrack():
                    return True
                self.solution[r][c] = 0
        return False

    def solve(self):
        start = time.time()
        ok = self._backtrack()
        duration = time.time() - start
        return (self.solution if ok else None, {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated, 'time': duration})


class SolverController:
    def __init__(self):
        self._thread = None
        self._result = None
        self._lock = threading.Lock()

    def run_full(self, size: int, grid: List[List[int]], h_constraints: List[List[int]], v_constraints: List[List[int]], callback=None, algorithm: str = 'backtrack'):
        def target():
            try:
                if algorithm == 'backtrack':
                    s = BacktrackSolverSimple(size, grid, (h_constraints, v_constraints))
                    solution, stats = s.solve()
                elif algorithm == 'astar':
                    from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
                    s = PureAStarSolver(size, grid, (h_constraints, v_constraints))
                    solution, nodes_expanded, nodes_generated = s.solve_astar()
                    stats = {'nodes_expanded': nodes_expanded, 'nodes_generated': nodes_generated}
                elif algorithm == 'astar_h1':
                    from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
                    s = PureAStarSolver(size, grid, (h_constraints, v_constraints), heuristic='h1')
                    solution, nodes_expanded, nodes_generated = s.solve_astar()
                    stats = {'nodes_expanded': nodes_expanded, 'nodes_generated': nodes_generated}
                elif algorithm == 'astar_h2':
                    from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
                    s = PureAStarSolver(size, grid, (h_constraints, v_constraints), heuristic='h2')
                    solution, nodes_expanded, nodes_generated = s.solve_astar()
                    stats = {'nodes_expanded': nodes_expanded, 'nodes_generated': nodes_generated}
                elif algorithm == 'astar_h3':
                    from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
                    s = PureAStarSolver(size, grid, (h_constraints, v_constraints), heuristic='h3')
                    solution, nodes_expanded, nodes_generated = s.solve_astar()
                    stats = {'nodes_expanded': nodes_expanded, 'nodes_generated': nodes_generated}
                    from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
                    s = AStarFutoshiki(size, grid, (h_constraints, v_constraints))
                    solution, nodes_expanded, nodes_generated = s.solve_with_ac3()
                    stats = {'nodes_expanded': nodes_expanded, 'nodes_generated': nodes_generated}
                elif algorithm == 'astar_ac3_h1':
                    from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
                    s = AStarFutoshiki(size, grid, (h_constraints, v_constraints), heuristic='h1')
                    solution, nodes_expanded, nodes_generated = s.solve_with_ac3()
                    stats = {'nodes_expanded': nodes_expanded, 'nodes_generated': nodes_generated}
                elif algorithm == 'astar_ac3_h2':
                    from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
                    s = AStarFutoshiki(size, grid, (h_constraints, v_constraints), heuristic='h2')
                    solution, nodes_expanded, nodes_generated = s.solve_with_ac3()
                    stats = {'nodes_expanded': nodes_expanded, 'nodes_generated': nodes_generated}
                elif algorithm == 'astar_ac3_h3':
                    from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
                    s = AStarFutoshiki(size, grid, (h_constraints, v_constraints), heuristic='h3')
                    solution, nodes_expanded, nodes_generated = s.solve_with_ac3()
                    stats = {'nodes_expanded': nodes_expanded, 'nodes_generated': nodes_generated}
                elif algorithm == 'backward_chaining_with_ac3':
                    from src.algorithm.first_order_logic.backward_chaining_with_ac3 import backward_chaining_with_ac3
                    s = backward_chaining_with_ac3(size, grid, (h_constraints, v_constraints))
                    status, domains = s.solve()
                    solution = s.solution
                    stats = {'nodes_expanded': 0, 'nodes_generated': 0}
                elif algorithm == 'backward_chaining':
                    from src.algorithm.first_order_logic.backward_chaining import backward_chaining
                    s = backward_chaining(size, grid, (h_constraints, v_constraints))
                    status, domains = s.solve()
                    solution = s.solution
                    stats = {'nodes_expanded': 0, 'nodes_generated': 0}
                elif algorithm == 'bc_no_backtrack':
                    from src.algorithm.first_order_logic.bc_no_backtrack import bc_no_backtrack
                    s = bc_no_backtrack(size, grid, (h_constraints, v_constraints))
                    status, domains = s.solve()
                    solution = s.solution
                    stats = {'nodes_expanded': 0, 'nodes_generated': 0}
                elif algorithm == 'forward_chaining':
                    from src.algorithm.first_order_logic.forward_chaining import fc_no_backtrack
                    s = fc_no_backtrack(size, grid, (h_constraints, v_constraints))
                    status, domains = s.solve()
                    solution = s.solution
                    stats = {'nodes_expanded': 0, 'nodes_generated': 0}
                elif algorithm == 'fc_with_backtrack':
                    from src.algorithm.first_order_logic.fc_with_backtrack import forward_chaining
                    s = forward_chaining(size, grid, (h_constraints, v_constraints))
                    status, domains = s.solve()
                    solution = s.solution
                    stats = {'nodes_expanded': 0, 'nodes_generated': 0}
                elif algorithm == 'dancing_links':
                    from src.algorithm.comparing_algorithms.dancing_links.dlx_futoshiki import DLXFutoshiki
                    s = DLXFutoshiki(size, grid, (h_constraints, v_constraints))
                    solution = s.solve()
                    stats = {'nodes_expanded': 0, 'nodes_generated': 0}
                else:
                    # default to backtrack
                    s = BacktrackSolverSimple(size, grid, (h_constraints, v_constraints))
                    solution, stats = s.solve()
            except Exception as e:
                import sys
                print(f"ERROR in run_full target: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                solution, stats = None, {}

            with self._lock:
                self._result = (solution, stats)
            if callback:
                callback(solution, stats)
        t = threading.Thread(target=target, daemon=True)
        t.start()
        self._thread = t
        return t

    def run_with_history(self, size: int, grid: List[List[int]], h_constraints: List[List[int]], v_constraints: List[List[int]], callback=None, algorithm: str = 'backtrack'):
        """Run solver and return (solution, stats, steps) via callback when done.

        Callback signature: callback(solution, stats, steps)
        """
        def target():
            try:
                if algorithm == 'backtrack':
                    s = BacktrackSolverSimple(size, grid, (h_constraints, v_constraints))
                    solution, stats, steps = s.solve_with_history()
                elif algorithm == 'astar':
                    from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
                    s = PureAStarSolver(size, grid, (h_constraints, v_constraints))
                    solution, stats, steps = s.solve_with_history()
                elif algorithm == 'astar_h1':
                    from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
                    s = PureAStarSolver(size, grid, (h_constraints, v_constraints), heuristic='h1')
                    solution, stats, steps = s.solve_with_history()
                elif algorithm == 'astar_h2':
                    from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
                    s = PureAStarSolver(size, grid, (h_constraints, v_constraints), heuristic='h2')
                    solution, stats, steps = s.solve_with_history()
                elif algorithm == 'astar_h3':
                    from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
                    s = PureAStarSolver(size, grid, (h_constraints, v_constraints), heuristic='h3')
                    solution, stats, steps = s.solve_with_history()
                    from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
                    s = AStarFutoshiki(size, grid, (h_constraints, v_constraints))
                    solution, stats, steps = s.solve_with_history()
                elif algorithm == 'astar_ac3_h1':
                    from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
                    s = AStarFutoshiki(size, grid, (h_constraints, v_constraints), heuristic='h1')
                    solution, stats, steps = s.solve_with_history()
                elif algorithm == 'astar_ac3_h2':
                    from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
                    s = AStarFutoshiki(size, grid, (h_constraints, v_constraints), heuristic='h2')
                    solution, stats, steps = s.solve_with_history()
                elif algorithm == 'astar_ac3_h3':
                    from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
                    s = AStarFutoshiki(size, grid, (h_constraints, v_constraints), heuristic='h3')
                    solution, stats, steps = s.solve_with_history()
                elif algorithm == 'backward_chaining_with_ac3':
                    from src.algorithm.first_order_logic.backward_chaining_with_ac3 import backward_chaining_with_ac3
                    s = backward_chaining_with_ac3(size, grid, (h_constraints, v_constraints))
                    status, domains = s.solve()
                    solution = s.solution
                    stats = {'nodes_expanded': 0, 'nodes_generated': 0}
                    steps = []
                elif algorithm == 'backward_chaining':
                    from src.algorithm.first_order_logic.backward_chaining import backward_chaining
                    s = backward_chaining(size, grid, (h_constraints, v_constraints))
                    status, domains = s.solve()
                    solution = s.solution
                    stats = {'nodes_expanded': 0, 'nodes_generated': 0}
                    steps = []
                elif algorithm == 'bc_no_backtrack':
                    from src.algorithm.first_order_logic.bc_no_backtrack import bc_no_backtrack
                    s = bc_no_backtrack(size, grid, (h_constraints, v_constraints))
                    status, domains = s.solve()
                    solution = s.solution
                    stats = {'nodes_expanded': 0, 'nodes_generated': 0}
                    steps = []
                elif algorithm == 'forward_chaining':
                    from src.algorithm.first_order_logic.forward_chaining import fc_no_backtrack
                    s = fc_no_backtrack(size, grid, (h_constraints, v_constraints))
                    status, domains = s.solve()
                    solution = s.solution
                    stats = {'nodes_expanded': 0, 'nodes_generated': 0}
                    steps = []
                elif algorithm == 'fc_with_backtrack':
                    from src.algorithm.first_order_logic.fc_with_backtrack import forward_chaining
                    s = forward_chaining(size, grid, (h_constraints, v_constraints))
                    status, domains = s.solve()
                    solution = s.solution
                    stats = {'nodes_expanded': 0, 'nodes_generated': 0}
                    steps = []
                elif algorithm == 'dancing_links':
                    from src.algorithm.comparing_algorithms.dancing_links.dlx_futoshiki import DLXFutoshiki
                    s = DLXFutoshiki(size, grid, (h_constraints, v_constraints))
                    solution = s.solve()
                    stats = {'nodes_expanded': 0, 'nodes_generated': 0}
                    steps = []
                else:
                    s = BacktrackSolverSimple(size, grid, (h_constraints, v_constraints))
                    solution, stats, steps = s.solve_with_history()
            except Exception:
                solution, stats, steps = None, {}, []

            with self._lock:
                self._result = (solution, stats, steps)
            if callback:
                callback(solution, stats, steps)
        t = threading.Thread(target=target, daemon=True)
        t.start()
        self._thread = t
        return t

    def run_with_event_stream(self, size: int, grid: List[List[int]], h_constraints: List[List[int]], v_constraints: List[List[int]], event_callback=None, algorithm: str = 'backtrack'):
        """Run solver in streaming mode and forward events to event_callback(action, r, c, value).

        event_callback is called for each step as it occurs. When solver finishes, it will also call event_callback('final', -1, -1, 0).
        """
        def target():
            try:
                if algorithm == 'backtrack':
                    s = BacktrackSolverSimple(size, grid, (h_constraints, v_constraints))
                    # BacktrackSolverSimple doesn't yet support streaming; use solve_with_history and forward
                    solution, stats, steps = s.solve_with_history()
                    if event_callback:
                        for step in steps:
                            event_callback(*step)
                elif algorithm == 'astar':
                    from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
                    s = PureAStarSolver(size, grid, (h_constraints, v_constraints))
                    solution, stats, steps = s.solve_with_history()
                    if event_callback:
                        for step in steps:
                            event_callback(*step)
                elif algorithm == 'astar_ac3':
                    from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
                    s = AStarFutoshiki(size, grid, (h_constraints, v_constraints))
                    solution, stats, steps = s.solve_with_history()
                    if event_callback:
                        for step in steps:
                            event_callback(*step)
                else:
                    s = BacktrackSolverSimple(size, grid, (h_constraints, v_constraints))
                    solution, stats, steps = s.solve_with_history()
                    if event_callback:
                        for step in steps:
                            event_callback(*step)
                # final
                if event_callback:
                    event_callback('final', -1, -1, 0)
            except Exception:
                if event_callback:
                    event_callback('final', -1, -1, 0)
        t = threading.Thread(target=target, daemon=True)
        t.start()
        self._thread = t
        return t
    def get_result(self) -> Optional[Tuple[List[List[int]], dict]]:
        with self._lock:
            return self._result

    def run_step_reveal(self, solution: List[List[int]], original_grid: List[List[int]], step_callback=None, delay: float = 0.3):
        """Reveal solution values for empty cells in row-major order with delay."""
        n = len(solution)
        for r in range(n):
            for c in range(n):
                if original_grid[r][c] == 0:
                    val = solution[r][c]
                    if step_callback:
                        step_callback(r, c, val)
                    time.sleep(delay)
