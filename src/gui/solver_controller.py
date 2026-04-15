import asyncio
import threading
import time
from typing import List, Tuple, Optional, Any, Callable
import multiprocessing
import queue

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


def _mp_worker(algorithm, size, grid, h_constraints, v_constraints, q):
    try:
        if algorithm == 'backtrack':
            from src.algorithm.comparing_algorithms.brute_force_and_backtrack.backtrack import BacktrackSolver
            s = BacktrackSolver(size, grid, (h_constraints, v_constraints))
            s.solve_with_history(stream_queue=q)
        elif algorithm == 'brute_force':
            from src.algorithm.comparing_algorithms.brute_force_and_backtrack.brute_force import BruteForceSolver
            s = BruteForceSolver(size, grid, (h_constraints, v_constraints))
            s.solve_with_history(stream_queue=q)
        elif algorithm.startswith('astar_ac3_h'):
            from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
            heuristic = algorithm.split('_')[2]
            s = AStarFutoshiki(size, grid, (h_constraints, v_constraints), heuristic=heuristic)
            s.solve_with_history(stream_queue=q)
        elif algorithm == 'astar_ac3':
            from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
            s = AStarFutoshiki(size, grid, (h_constraints, v_constraints))
            s.solve_with_history(stream_queue=q)
        elif algorithm.startswith('astar_h'):
            from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
            heuristic = algorithm.split('_')[1]
            s = PureAStarSolver(size, grid, (h_constraints, v_constraints), heuristic=heuristic)
            s.solve_with_history(stream_queue=q)
        elif algorithm == 'astar':
            from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
            s = PureAStarSolver(size, grid, (h_constraints, v_constraints))
            s.solve_with_history(stream_queue=q)
        elif algorithm == 'backward_chaining':
            from src.algorithm.first_order_logic.backward_chaining import backward_chaining
            s = backward_chaining(size, grid, (h_constraints, v_constraints))
            s.solve_with_history(stream_queue=q)
        elif algorithm == 'backward_chaining_with_ac3':
            from src.algorithm.first_order_logic.backward_chaining_with_ac3 import backward_chaining_with_ac3
            s = backward_chaining_with_ac3(size, grid, (h_constraints, v_constraints))
            s.solve_with_history(stream_queue=q)
        elif algorithm == 'bc_no_backtrack':
            from src.algorithm.first_order_logic.bc_no_backtrack import bc_no_backtrack
            s = bc_no_backtrack(size, grid, (h_constraints, v_constraints))
            s.solve_with_history(stream_queue=q)
        elif algorithm == 'forward_chaining':
            from src.algorithm.first_order_logic.forward_chaining import fc_no_backtrack
            s = fc_no_backtrack(size, grid, (h_constraints, v_constraints))
            s.solve_with_history(stream_queue=q)
        elif algorithm == 'fc_with_backtrack':
            from src.algorithm.first_order_logic.fc_with_backtrack import forward_chaining
            s = forward_chaining(size, grid, (h_constraints, v_constraints))
            s.solve_with_history(stream_queue=q)
        elif algorithm == 'dancing_links':
            from src.algorithm.comparing_algorithms.dancing_links.dlx_futoshiki import DLXFutoshiki
            s = DLXFutoshiki(size, grid, (h_constraints, v_constraints))
            s.solve_with_history(stream_queue=q)
        else:
            from src.algorithm.comparing_algorithms.brute_force_and_backtrack.backtrack import BacktrackSolver
            s = BacktrackSolver(size, grid, (h_constraints, v_constraints))
            s.solve_with_history(stream_queue=q)
    except Exception as e:
        import traceback
        traceback.print_exc()
        q.put(('done', None, {}))


class SolverController:
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._result = None
        self._lock = asyncio.Lock()

    async def run_full(self, size: int, grid: List[List[int]], h_constraints: List[List[int]], v_constraints: List[List[int]], callback=None, algorithm: str = 'backtrack'):
        async def target():
            try:
                def sync_solve():
                    if algorithm == 'backtrack':
                        s = BacktrackSolverSimple(size, grid, (h_constraints, v_constraints))
                        return s.solve()
                    elif algorithm.startswith('astar_h'):
                        from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
                        heuristic = algorithm.split('_')[1]
                        s = PureAStarSolver(size, grid, (h_constraints, v_constraints), heuristic=heuristic)
                        solution = s.solve()
                        stats = s.get_stats()
                        return solution.tolist() if solution is not None else None, stats
                    elif algorithm == 'astar':
                        from src.algorithm.comparing_algorithms.a_star.a_star import PureAStarSolver
                        s = PureAStarSolver(size, grid, (h_constraints, v_constraints))
                        solution = s.solve()
                        stats = s.get_stats()
                        return solution.tolist() if solution is not None else None, stats
                    elif algorithm == 'astar_ac3':
                        from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
                        s = AStarFutoshiki(size, grid, (h_constraints, v_constraints))
                        solution, nodes_expanded, nodes_generated = s.solve_with_ac3()
                        return solution.tolist() if solution is not None else None, {'nodes_expanded': nodes_expanded, 'nodes_generated': nodes_generated}
                    elif algorithm == 'backward_chaining_with_ac3':
                        from src.algorithm.first_order_logic.backward_chaining_with_ac3 import backward_chaining_with_ac3
                        s = backward_chaining_with_ac3(size, grid, (h_constraints, v_constraints))
                        s.solve()
                        return s.solution, {'nodes_expanded': 0, 'nodes_generated': 0}
                    elif algorithm == 'dancing_links':
                        from src.algorithm.comparing_algorithms.dancing_links.dlx_futoshiki import DLXFutoshiki
                        s = DLXFutoshiki(size, grid, (h_constraints, v_constraints))
                        solution = s.solve()
                        return solution, {'nodes_expanded': 0, 'nodes_generated': 0}
                    else:
                        s = BacktrackSolverSimple(size, grid, (h_constraints, v_constraints))
                        return s.solve()

                solution, stats = await asyncio.to_thread(sync_solve)
            except Exception as e:
                import sys
                print(f"ERROR in run_full target: {e}", file=sys.stderr)
                solution, stats = None, {}

            async with self._lock:
                self._result = (solution, stats)
            if callback:
                if asyncio.iscoroutinefunction(callback):
                    await callback(solution, stats)
                else:
                    callback(solution, stats)

        self._task = asyncio.create_task(target())
        return self._task

    async def run_with_history(self, size: int, grid: List[List[int]], h_constraints: List[List[int]], v_constraints: List[List[int]], callback=None, algorithm: str = 'backtrack', step_player=None):
        """Run solver and stream events to step_player via multiprocessing.
        """
        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=_mp_worker, args=(algorithm, size, grid, h_constraints, v_constraints, q))
        p.daemon = True
        p.start()

        async def consumer():
            while True:
                try:
                    # Blocking call in thread to avoid event loop block
                    step = await asyncio.to_thread(q.get, timeout=0.05)
                    if step[0] == 'done':
                        if callback:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(step[1], step[2], [])
                            else:
                                callback(step[1], step[2], [])
                        break
                    if step_player:
                        step_player.push_event(step)
                except queue.Empty:
                    if not p.is_alive():
                        if callback:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(None, {}, [])
                            else:
                                callback(None, {}, [])
                        break
                except Exception:
                    break
        
        self._task = asyncio.create_task(consumer())
        return p

    async def get_result(self) -> Optional[Tuple[List[List[int]], dict]]:
        async with self._lock:
            return self._result
