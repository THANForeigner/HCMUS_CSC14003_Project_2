import heapq
import numpy as np
from typing import Tuple, Optional, Dict, List, Set
from collections import deque
from ...futoshiki_solver import FutoshikiSolver, FutoshikiState


class AC3Solver:
    def __init__(
        self,
        size: int,
        grid: np.ndarray,
        h_constraints: np.ndarray,
        v_constraints: np.ndarray,
        initial_domains: Optional[Dict] = None,
    ):
        self.size = size
        self.grid = np.array(grid)
        self.h_constraints = np.array(h_constraints)
        self.v_constraints = np.array(v_constraints)

        # Tối ưu: Nếu đã truyền domain vào thì dùng luôn, không cần tính lại từ đầu
        if initial_domains is not None:
            self.domains = {k: v.copy() for k, v in initial_domains.items()}
        else:
            self.domains: Dict[Tuple[int, int], Set[int]] = {}
            self._init_domains()

    def _init_domains(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i, j] != 0:
                    self.domains[(i, j)] = {self.grid[i, j]}
                else:
                    self.domains[(i, j)] = set(range(1, self.size + 1))
                    row_used = set(self.grid[i, :]) - {0}
                    col_used = set(self.grid[:, j]) - {0}
                    self.domains[(i, j)] -= row_used | col_used

    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        # Tối ưu: Dùng Set để tránh việc neighbor bị thêm vào 2 lần
        neighbors = set()
        for j in range(self.size):
            if j != col:
                neighbors.add((row, j))
        for i in range(self.size):
            if i != row:
                neighbors.add((i, col))
        return list(neighbors)

    def revise(self, x: Tuple[int, int], y: Tuple[int, int]) -> bool:
        revised = False
        constraint_type = self._get_constraint(x, y)

        if constraint_type == 0:
            return False

        to_remove = set()
        for val_x in self.domains[x]:
            valid = False
            for val_y in self.domains[y]:
                if constraint_type == 1 and val_x < val_y:
                    valid = True
                    break
                elif constraint_type == -1 and val_x > val_y:
                    valid = True
                    break
                elif constraint_type == 2 and val_x != val_y:
                    valid = True
                    break

            if not valid:
                to_remove.add(val_x)
                revised = True

        if revised:
            self.domains[x] -= to_remove
        return revised

    def _get_constraint(self, x: Tuple[int, int], y: Tuple[int, int]) -> int:
        r1, c1 = x
        r2, c2 = y

        # Kiểm tra ràng buộc Lớn/Bé (chỉ áp dụng cho 2 ô kề nhau)
        if r1 == r2 and abs(c1 - c2) == 1:
            left, right = min(c1, c2), max(c1, c2)
            if self.h_constraints[r1, left] != 0:
                constraint = self.h_constraints[r1, left]
                if c1 > c2:
                    constraint = -constraint
                return constraint

        if c1 == c2 and abs(r1 - r2) == 1:
            top, bottom = min(r1, r2), max(r1, r2)
            if self.v_constraints[top, c1] != 0:
                constraint = self.v_constraints[top, c1]
                if r1 > r2:
                    constraint = -constraint
                return constraint

        # Mọi ô cùng hàng hoặc cột ĐỀU PHẢI KHÁC NHAU (Constraint = 2)
        if r1 == r2 or c1 == c2:
            return 2

        return 0

    def ac3(self) -> bool:
        queue = deque()
        for i in range(self.size):
            for j in range(self.size):
                if (
                    len(self.domains[(i, j)]) > 1
                ):  # Tối ưu: Chỉ enqueue các ô chưa chắc chắn
                    for ni, nj in self.get_neighbors(i, j):
                        queue.append(((i, j), (ni, nj)))

        while queue:
            (x, y) = queue.popleft()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False  # Xung đột, ngõ cụt
                for xi, xj in self.get_neighbors(*x):
                    if (xi, xj) != y:
                        queue.append(((xi, xj), x))
        return True


class AStarFutoshiki(FutoshikiSolver):
    def __init__(
        self, size: int, grid, constraint, heuristic: str = "h3", mode: str = "ac3"
    ):
        super().__init__(size, grid, constraint)
        self.heuristic = heuristic
        self.mode = mode  # 'ac3' hoặc 'astar'
        self.nodes_expanded = 0
        self.nodes_generated = 0

    def is_valid_move(
        self, state: FutoshikiState, row: int, col: int, value: int
    ) -> bool:
        # Tối ưu siêu tốc để thay thế state.copy() bừa bãi trong A*
        if value in state.grid[row, :]:
            return False
        if value in state.grid[:, col]:
            return False

        if col > 0 and self.h_constraints[row, col - 1] != 0:
            left_val = state.grid[row, col - 1]
            if left_val != 0:
                if self.h_constraints[row, col - 1] == 1 and not (left_val < value):
                    return False
                if self.h_constraints[row, col - 1] == -1 and not (left_val > value):
                    return False

        if col < self.size - 1 and self.h_constraints[row, col] != 0:
            right_val = state.grid[row, col + 1]
            if right_val != 0:
                if self.h_constraints[row, col] == 1 and not (value < right_val):
                    return False
                if self.h_constraints[row, col] == -1 and not (value > right_val):
                    return False

        if row > 0 and self.v_constraints[row - 1, col] != 0:
            top_val = state.grid[row - 1, col]
            if top_val != 0:
                if self.v_constraints[row - 1, col] == 1 and not (top_val < value):
                    return False
                if self.v_constraints[row - 1, col] == -1 and not (top_val > value):
                    return False

        if row < self.size - 1 and self.v_constraints[row, col] != 0:
            bottom_val = state.grid[row + 1, col]
            if bottom_val != 0:
                if self.v_constraints[row, col] == 1 and not (value < bottom_val):
                    return False
                if self.v_constraints[row, col] == -1 and not (value > bottom_val):
                    return False

        return True

    def find_best_blank(
        self, state: FutoshikiState, domains: Optional[Dict] = None
    ) -> Tuple[int, int]:
        blanks = state.get_blank_positions()
        if not blanks:
            return -1, -1

        best_pos = blanks[0]
        min_domain = float("inf")

        for r, c in blanks:
            if domains:
                domain_size = len(domains[(r, c)])
            else:
                row_used = set(state.grid[r, :])
                col_used = set(state.grid[:, c])
                domain_size = self.size - len((row_used | col_used) - {0})

            if domain_size == 0:
                return -1, -1
            if domain_size < min_domain:
                min_domain = domain_size
                best_pos = (r, c)
                if min_domain == 1:
                    break

        return best_pos

    def solve(self) -> Optional[np.ndarray]:
        if self.mode == "ac3":
            solution, _, _ = self.solve_with_ac3()
        else:
            solution, _, _ = self.solve_astar()
        return solution

    def solve_astar(
        self, max_nodes: int = 500000
    ) -> Tuple[Optional[np.ndarray], int, int]:
        self.nodes_expanded = 0
        self.nodes_generated = 0
        initial_state = FutoshikiState(self.grid)

        open_set = []
        # -0 để ép A* đi sâu xuống theo chiều dọc
        heapq.heappush(open_set, (0, -0, 0, 0, initial_state))
        counter = 0

        while open_set:
            if self.nodes_expanded > max_nodes:
                return None, self.nodes_expanded, self.nodes_generated

            f, neg_g, h, _, current_state = heapq.heappop(open_set)
            g = -neg_g

            if len(current_state.get_blank_positions()) == 0:
                return current_state.grid, self.nodes_expanded, self.nodes_generated

            self.nodes_expanded += 1
            row, col = self.find_best_blank(current_state)
            if row == -1:
                continue

            for value in range(1, self.size + 1):
                if self.is_valid_move(current_state, row, col, value):
                    new_state = current_state.copy()
                    new_state.grid[row, col] = value
                    self.nodes_generated += 1

                    new_g = g + 1
                    # Hàm h3 (MRV) ước tính
                    new_h = self.size - new_g
                    counter += 1
                    heapq.heappush(
                        open_set, (new_g + new_h, -new_g, new_h, counter, new_state)
                    )

        return None, self.nodes_expanded, self.nodes_generated

    def solve_with_ac3(
        self, max_nodes: int = 100000
    ) -> Tuple[Optional[np.ndarray], int, int]:
        self.nodes_expanded = 0
        self.nodes_generated = 0

        ac3 = AC3Solver(self.size, self.grid, self.h_constraints, self.v_constraints)
        if not ac3.ac3():
            return None, 0, 1

        initial_state = FutoshikiState(self.grid)
        for key, val_set in ac3.domains.items():
            if len(val_set) == 1:
                initial_state.grid[key] = list(val_set)[0]

        def backtrack(
            state: FutoshikiState, current_domains: Dict
        ) -> Tuple[Optional[FutoshikiState], int, int]:
            if len(state.get_blank_positions()) == 0:
                return state, self.nodes_expanded, self.nodes_generated

            self.nodes_expanded += 1
            if self.nodes_expanded > max_nodes:
                return None, self.nodes_expanded, self.nodes_generated

            row, col = self.find_best_blank(state, current_domains)
            if row == -1:
                return None, self.nodes_expanded, self.nodes_generated

            for value in list(current_domains[(row, col)]):
                if self.is_valid_move(state, row, col, value):
                    self.nodes_generated += 1
                    new_state = state.copy()
                    new_state.grid[row, col] = value

                    new_domains = {k: v.copy() for k, v in current_domains.items()}
                    new_domains[(row, col)] = {value}

                    # Truyền domain cũ vào để tái sử dụng, không cần _init_domains từ đầu
                    new_ac3 = AC3Solver(
                        self.size,
                        new_state.grid,
                        self.h_constraints,
                        self.v_constraints,
                        initial_domains=new_domains,
                    )

                    if new_ac3.ac3():
                        assigned_valid = True
                        for key, val_set in new_ac3.domains.items():
                            if len(val_set) == 1:
                                r, c = key
                                if new_state.grid[r, c] == 0:
                                    val = list(val_set)[0]
                                    if self.is_valid_move(new_state, r, c, val):
                                        new_state.grid[r, c] = val
                                    else:
                                        assigned_valid = False
                                        break
                            elif len(val_set) == 0:
                                assigned_valid = False
                                break

                        if assigned_valid:
                            result, exp, gen = backtrack(new_state, new_ac3.domains)
                            self.nodes_expanded = exp
                            self.nodes_generated = gen
                            if result is not None:
                                return result, self.nodes_expanded, self.nodes_generated

            return None, self.nodes_expanded, self.nodes_generated

        result, exp, gen = backtrack(initial_state, ac3.domains)
        return result.grid if result else None, exp, gen

    def solve_with_history(self, stream_queue=None):
        import time
        self.nodes_expanded = 0
        self.nodes_generated = 0
        start = time.time()
        
        ac3 = AC3Solver(self.size, self.grid, self.h_constraints, self.v_constraints)
        if not ac3.ac3():
            duration = time.time() - start
            stats = {'nodes_expanded': 0, 'nodes_generated': 1, 'time': duration}
            if stream_queue:
                stream_queue.put(('done', None, stats))
            return (None, stats, [])
        
        initial_state = FutoshikiState(self.grid)
        for key, val_set in ac3.domains.items():
            if len(val_set) == 1:
                initial_state.grid[key] = list(val_set)[0]
        
        if stream_queue:
            stream_queue.put(('step', initial_state.grid.tolist(), self.nodes_expanded))
        
        def backtrack(state: FutoshikiState, current_domains: Dict):
            if len(state.get_blank_positions()) == 0:
                return state
            
            self.nodes_expanded += 1
            if self.nodes_expanded > 100000:
                return None
            
            row, col = self.find_best_blank(state, current_domains)
            if row == -1:
                return None
            
            for value in list(current_domains[(row, col)]):
                if self.is_valid_move(state, row, col, value):
                    self.nodes_generated += 1
                    new_state = state.copy()
                    new_state.grid[row, col] = value
                    
                    if stream_queue:
                        stream_queue.put(('step', new_state.grid.tolist(), self.nodes_expanded))
                    
                    new_domains = {k: v.copy() for k, v in current_domains.items()}
                    new_domains[(row, col)] = {value}
                    
                    new_ac3 = AC3Solver(
                        self.size,
                        new_state.grid,
                        self.h_constraints,
                        self.v_constraints,
                        initial_domains=new_domains,
                    )
                    
                    if new_ac3.ac3():
                        assigned_valid = True
                        for key, val_set in new_ac3.domains.items():
                            if len(val_set) == 1:
                                r, c = key
                                if new_state.grid[r, c] == 0:
                                    val = list(val_set)[0]
                                    if self.is_valid_move(new_state, r, c, val):
                                        new_state.grid[r, c] = val
                                    else:
                                        assigned_valid = False
                                        break
                            elif len(val_set) == 0:
                                assigned_valid = False
                                break
                        
                        if assigned_valid:
                            result = backtrack(new_state, new_ac3.domains)
                            if result is not None:
                                return result
            
            return None
        
        result = backtrack(initial_state, ac3.domains)
        duration = time.time() - start
        stats = {'nodes_expanded': self.nodes_expanded, 'nodes_generated': self.nodes_generated, 'time': duration}
        
        sol_list = result.grid.tolist() if result is not None else None
        if stream_queue:
            stream_queue.put(('done', sol_list, stats))
        return (sol_list, stats, [])
