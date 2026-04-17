import os
import sys
import time
import logging
import tracemalloc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import signal
from datetime import datetime
from collections import defaultdict

class TimeoutException(BaseException):
    pass

ACTIVE_SOLVER = None
LAST_INFERENCES = 1

def timeout_handler(signum, frame):
    global LAST_INFERENCES
    if ACTIVE_SOLVER is not None:
        nested_solver = getattr(ACTIVE_SOLVER, '_fallback_solver', None)
        nested_nodes = getattr(nested_solver, 'nodes_expanded', 0) if nested_solver is not None else 0
        LAST_INFERENCES = max(1, getattr(ACTIVE_SOLVER, 'nodes_expanded', 1) + nested_nodes)
    raise TimeoutException("Timeout")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.io_handler import read_input

def setup_logging(log_dir):
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"benchmark_{timestamp}.log")

    logger = logging.getLogger("benchmark")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

    return logger, log_file

def log(msg=""):
    logging.getLogger("benchmark").info(msg)

ALL_ALGOS = [
    "Comparing algorithms",
    "Forward Chaining",
    "Backward Chaining",
    "A* (Không kết hợp AC-3)",
    "Dancing Links",
    "A* kết hợp AC-3",
    "Forward Chaining kết hợp Backtracking",
    "Backward Chaining (bản cải tiến)",
    "Backward Chaining kết hợp AC-3",
]

ALGORITHM_GROUPS = {
    "Group 1: Basic Algorithms": [
        "Comparing algorithms",
        "Forward Chaining",
        "Backward Chaining",
        "A* (Không kết hợp AC-3)",
    ],
    "Group 2: Extended / Advanced Algorithms": [
        "Dancing Links",
        "A* kết hợp AC-3",
        "Forward Chaining kết hợp Backtracking",
        "Backward Chaining (bản cải tiến)",
        "Backward Chaining kết hợp AC-3",
    ],
}

ALGORITHM_LABELS = {
    "Comparing algorithms": "Comparing Algorithms",
    "Forward Chaining": "Forward Chaining",
    "Backward Chaining": "Backward Chaining",
    "A* (Không kết hợp AC-3)": "A* (without AC-3)",
    "Dancing Links": "Dancing Links",
    "A* kết hợp AC-3": "A* with AC-3",
    "Forward Chaining kết hợp Backtracking": "Forward Chaining + Backtracking",
    "Backward Chaining (bản cải tiến)": "Advanced Backward Chaining",
    "Backward Chaining kết hợp AC-3": "Backward Chaining + AC-3",
}

def choose_benchmark_algorithms():
    while True:
        print("\n" + "=" * 60)
        print("CHỌN THUẬT TOÁN BENCHMARK")
        print("=" * 60)

        for idx, algo in enumerate(ALL_ALGOS, start=1):
            print(f"  {idx}. {algo}")

        all_choice = len(ALL_ALGOS) + 1
        print("-" * 60)
        print(f"  {all_choice}. Chạy tất cả")
        print("=" * 60)
        print("Có thể nhập nhiều số, ví dụ: 1 3 hoặc 1,3")
        print("Bỏ trống để chạy tất cả")

        raw_choice = input("Nhập lựa chọn: ").strip()
        if not raw_choice:
            return list(ALL_ALGOS)

        choices = raw_choice.replace(",", " ").split()
        if not all(c.isdigit() for c in choices):
            print("Lựa chọn không hợp lệ. Vui lòng chỉ nhập số.")
            continue

        selected_numbers = [int(c) for c in choices]
        if all_choice in selected_numbers:
            return list(ALL_ALGOS)

        if any(n < 1 or n > len(ALL_ALGOS) for n in selected_numbers):
            print(f"Lựa chọn không hợp lệ. Vui lòng nhập số từ 1 đến {all_choice}.")
            continue

        seen = set()
        selected_algos = []
        for n in selected_numbers:
            algo = ALL_ALGOS[n - 1]
            if algo not in seen:
                seen.add(algo)
                selected_algos.append(algo)

        return selected_algos

def choose_run_mode():
    while True:
        print("\n" + "=" * 60)
        print("CHỌN CHẾ ĐỘ CHẠY")
        print("=" * 60)
        print("  1. Test thử  — chỉ chạy file có kích thước ≤ 6x6")
        print("  2. Chạy thật — chạy toàn bộ file input")
        print("=" * 60)
        raw = input("Nhập lựa chọn (mặc định 1): ").strip()
        if raw == "" or raw == "1":
            return "test"
        if raw == "2":
            return "full"
        print("Vui lòng chỉ nhập 1 hoặc 2.")


DIFFICULTIES = ["trivial", "easy", "tricky", "extreme"]

def parse_difficulty(filename):
    name = filename.lower()
    for diff in DIFFICULTIES:
        if diff in name:
            return diff
    return "unknown"

# Validate a completed grid against Latin-square and inequality constraints.
def validate_solution(size, original_grid, solved_grid, h, v):
    if solved_grid is None or len(solved_grid) != size or len(solved_grid[0]) != size:
        return False

    for i in range(size):
        row_set, col_set = set(), set()
        for j in range(size):
            val_r = solved_grid[i][j]
            val_c = solved_grid[j][i]
            if val_r < 1 or val_r > size or val_r in row_set: return False
            if val_c < 1 or val_c > size or val_c in col_set: return False
            row_set.add(val_r)
            col_set.add(val_c)
            if original_grid[i][j] != 0 and solved_grid[i][j] != original_grid[i][j]:
                return False

    for r in range(size):
        for c in range(size - 1):
            if h[r][c] == 1  and not (solved_grid[r][c] < solved_grid[r][c+1]): return False
            if h[r][c] == -1 and not (solved_grid[r][c] > solved_grid[r][c+1]): return False

    for r in range(size - 1):
        for c in range(size):
            if v[r][c] == 1  and not (solved_grid[r][c] < solved_grid[r+1][c]): return False
            if v[r][c] == -1 and not (solved_grid[r][c] > solved_grid[r+1][c]): return False

    return True

import copy

def create_futoshiki_evaluator(size, grid, h, v):
    from src.algorithm.comparing_algorithms.a_star.a_star_with_ac3 import AStarFutoshiki
    return AStarFutoshiki(size, grid, [h, v])

def call_algorithm(algo_name, size, grid, h, v):
    global ACTIVE_SOLVER, LAST_INFERENCES
    grid_copy = copy.deepcopy(grid)
    inferences = 1
    solution = None
    constraint = [h, v]
    ACTIVE_SOLVER = None
    LAST_INFERENCES = 1

    try:
        if algo_name == "Comparing algorithms":
            from src.algorithm.comparing_algorithms.brute_force_and_backtrack.backtrack import BacktrackSolver
            solver = BacktrackSolver(size, grid_copy, constraint)
            ACTIVE_SOLVER = solver
            res = solver.solve()
            if res is not None: solution = solver.solution
            inferences = getattr(solver, 'nodes_expanded', 1)
            LAST_INFERENCES = inferences

        elif algo_name == "Forward Chaining":
            from src.algorithm.first_order_logic.forward_chaining import fc_no_backtrack as FC_no_bt
            solver = FC_no_bt(size, grid_copy, constraint)
            ACTIVE_SOLVER = solver
            res = solver.solve()
            if res[0] == "Solved": solution = solver.solution
            inferences = getattr(solver, 'nodes_expanded', 1)
            LAST_INFERENCES = inferences

        elif algo_name == "Backward Chaining":
            from src.algorithm.first_order_logic.bc_no_backtrack import bc_no_backtrack as BC_std
            solver = BC_std(size, grid_copy, constraint)
            ACTIVE_SOLVER = solver
            res = solver.solve()
            if res[0] == "Solved": solution = solver.solution
            inferences = getattr(solver, 'nodes_expanded', 1)
            LAST_INFERENCES = inferences

        elif algo_name == "A* (Không kết hợp AC-3)":
            evaluator = create_futoshiki_evaluator(size, grid_copy, h, v)
            ACTIVE_SOLVER = evaluator
            sol, expanded, generated = evaluator.solve_astar()
            if sol is not None:
                solution = sol.tolist()
            inferences = expanded
            LAST_INFERENCES = inferences

        elif algo_name == "Dancing Links":
            from src.algorithm.comparing_algorithms.dancing_links.dlx_futoshiki import DLXFutoshiki
            solver = DLXFutoshiki(size, grid_copy, constraint)
            ACTIVE_SOLVER = solver
            res = solver.solve()
            solution = getattr(solver, "solution", None)
            inferences = getattr(solver, 'nodes_expanded', 1)
            LAST_INFERENCES = inferences

        elif algo_name == "A* kết hợp AC-3":
            evaluator = create_futoshiki_evaluator(size, grid_copy, h, v)
            ACTIVE_SOLVER = evaluator
            sol, expanded, generated = evaluator.solve_with_ac3()
            if sol is not None:
                solution = sol.tolist()
            inferences = expanded
            LAST_INFERENCES = inferences

        elif algo_name == "Forward Chaining kết hợp Backtracking":
            from src.algorithm.first_order_logic.fc_with_backtrack import forward_chaining as FC
            solver = FC(size, grid_copy, constraint)
            ACTIVE_SOLVER = solver
            res = solver.solve()
            if res[0] == "Solved": solution = solver.solution
            inferences = getattr(solver, 'nodes_expanded', 1)
            LAST_INFERENCES = inferences

        elif algo_name == "Backward Chaining (bản cải tiến)":
            from src.algorithm.first_order_logic.backward_chaining import backward_chaining as BC_adv
            solver = BC_adv(size, grid_copy, constraint)
            ACTIVE_SOLVER = solver
            res = solver.solve()
            if res[0] == "Solved": solution = solver.solution
            inferences = getattr(solver, 'nodes_expanded', 1)
            LAST_INFERENCES = inferences

        elif algo_name == "Backward Chaining kết hợp AC-3":
            from src.algorithm.first_order_logic.backward_chaining_with_ac3 import backward_chaining_with_ac3 as BC_AC3
            solver = BC_AC3(size, grid_copy, constraint)
            ACTIVE_SOLVER = solver
            res = solver.solve()
            if res[0] == "Solved": solution = solver.solution
            inferences = getattr(solver, 'nodes_expanded', 1)
            LAST_INFERENCES = inferences

    except RecursionError:
        pass
    except Exception:
        pass
    finally:
        ACTIVE_SOLVER = None

    return solution, inferences

MARKERS = ['o', 's', '^', 'D', 'v', 'P', 'X', '*', 'h']
LINESTYLES = ['-', '--', ':', '-.']

def plot_metrics(results_by_diff, all_algos, plot_dir):
    """Plot one chart per difficulty and metric, split by algorithm group."""
    os.makedirs(plot_dir, exist_ok=True)

    metrics = {
        "time":       "Execution Time (s)",
        "memory":     "Memory Usage (MB)",
        "accuracy":   "Accuracy (%)",
        "inferences": "Number of Inferences",
    }

    selected_groups = {
        group_name: [algo for algo in algos if algo in all_algos]
        for group_name, algos in ALGORITHM_GROUPS.items()
    }
    selected_groups = {name: algos for name, algos in selected_groups.items() if algos}

    for diff, results in results_by_diff.items():
        has_data = any(results[a]["sizes"] for a in all_algos)
        if not has_data:
            continue

        for key, ylabel in metrics.items():
            fig, axes = plt.subplots(1, len(selected_groups), figsize=(8 * len(selected_groups), 6), squeeze=False)
            fig.suptitle(
                f"[{diff.upper()}] {ylabel} vs Grid Size",
                fontsize=14, fontweight="bold"
            )

            for group_idx, (group_name, algos) in enumerate(selected_groups.items()):
                ax = axes[0][group_idx]
                drawable_algos = [
                    algo for algo in algos
                    if results[algo]["sizes"] and results[algo][key]
                ]
                drawable_algos.sort(key=lambda algo: np.mean(results[algo][key]))
                total_lines = max(1, len(drawable_algos))

                for algo_idx, algo in enumerate(drawable_algos):
                    data = results[algo]
                    linewidth = max(2.0, 6.0 - algo_idx * (4.0 / total_lines))
                    markersize = max(5.0, 9.0 - algo_idx * (4.0 / total_lines))
                    ax.plot(
                        data["sizes"], data[key],
                        marker=MARKERS[algo_idx % len(MARKERS)],
                        markersize=markersize,
                        linewidth=linewidth,
                        linestyle=LINESTYLES[algo_idx % len(LINESTYLES)],
                        alpha=0.9,
                        label=ALGORITHM_LABELS.get(algo, algo)
                    )

                ax.set_title(group_name, fontsize=11, fontweight="bold")
                ax.set_xlabel("Grid Size (N x N)")
                ax.set_ylabel(ylabel)
                if key in ("time", "inferences"):
                    ax.set_yscale("log")
                ax.grid(True, linestyle="--", alpha=0.6)
                ax.legend(fontsize=8)

            plt.tight_layout()
            save_path = os.path.join(plot_dir, f"{diff}_{key}.png")
            plt.savefig(save_path, dpi=150)
            plt.close()
            log(f"  Đã lưu: {save_path}")

def run_benchmark():
    base_dir   = os.path.dirname(__file__)
    input_dir  = os.path.join(base_dir, "input")
    if not os.path.exists(input_dir):
        input_dir = os.path.join(base_dir, "inputs")
    if not os.path.exists(input_dir):
        print(f"Không tìm thấy thư mục input: {input_dir}")
        return

    plot_dir = os.path.join(base_dir, "plot")
    log_dir  = base_dir

    logger, log_file = setup_logging(log_dir)

    all_algos = choose_benchmark_algorithms()
    run_mode  = choose_run_mode()

    TEST_MAX_SIZE = 6

    # Store raw runs before averaging by difficulty, algorithm, and grid size.
    agg = defaultdict(lambda: {a: defaultdict(lambda: {"t":[],"m":[],"a":[],"i":[]}) for a in all_algos})

    all_files = sorted(f for f in os.listdir(input_dir) if f.endswith(".txt"))
    if run_mode == "test":
        files = []
        for f in all_files:
            try:
                s, _, _ = read_input(os.path.join(input_dir, f))
                if s <= TEST_MAX_SIZE:
                    files.append(f)
            except Exception:
                pass
    else:
        files = all_files

    log("=" * 60)
    log("BẮT ĐẦU CHẠY BENCHMARK")
    log(f"Log file: {log_file}")
    log(f"Chế độ  : {'TEST (size ≤ 6x6)' if run_mode == 'test' else 'FULL (tất cả)'}")
    log("Thuật toán đã chọn:")
    for algo in all_algos:
        log(f"  - {algo}")
    log(f"Số file sẽ chạy: {len(files)}")
    log("=" * 60)

    for filename in files:
        filepath   = os.path.join(input_dir, filename)
        difficulty = parse_difficulty(filename)
        size, org_grid, (h, v) = read_input(filepath)
        log(f"\n[{difficulty.upper()}] {filename}  (Size {size}x{size})")

        for algo in all_algos:
            tracemalloc.start()
            start_time = time.time()

            solved_grid = None
            inferences  = 1
            _nodes_ref  = [1]
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(60)
            try:
                solved_grid, inferences = call_algorithm(algo, size, org_grid, h, v)
                _nodes_ref[0] = inferences
            except TimeoutException:
                inferences = max(_nodes_ref[0], LAST_INFERENCES)
            finally:
                signal.alarm(0)

            exec_time = time.time() - start_time
            mem_usage = tracemalloc.get_traced_memory()[1] / (1024 * 1024)
            tracemalloc.stop()

            is_correct = validate_solution(size, org_grid, solved_grid, h, v)
            accuracy   = 100.0 if is_correct else 0.0

            agg[difficulty][algo][size]["t"].append(exec_time)
            agg[difficulty][algo][size]["m"].append(mem_usage)
            agg[difficulty][algo][size]["a"].append(accuracy)
            agg[difficulty][algo][size]["i"].append(inferences)

            status_icon = "✓" if is_correct else "✗"
            log(f"  {status_icon} {algo:<38} Time={exec_time:.4f}s  Mem={mem_usage:.2f}MB  Inf={inferences}")

    log("\n" + "=" * 60)
    log("VẼ BIỂU ĐỒ THEO ĐỘ KHÓ")
    log("=" * 60)

    results_by_diff = {}
    for diff in agg:
        results_by_diff[diff] = {a: {"sizes":[], "time":[], "memory":[], "accuracy":[], "inferences":[]} for a in all_algos}
        for algo in all_algos:
            for s in sorted(agg[diff][algo].keys()):
                d = agg[diff][algo][s]
                if d["t"]:
                    results_by_diff[diff][algo]["sizes"].append(s)
                    results_by_diff[diff][algo]["time"].append(np.mean(d["t"]))
                    results_by_diff[diff][algo]["memory"].append(np.mean(d["m"]))
                    results_by_diff[diff][algo]["accuracy"].append(np.mean(d["a"]))
                    results_by_diff[diff][algo]["inferences"].append(np.mean(d["i"]))

    plot_metrics(results_by_diff, all_algos, plot_dir)

    log("\n✅ BENCHMARK HOÀN TẤT!")
    log(f"   Biểu đồ: {plot_dir}/")
    log(f"   Log:     {log_file}")

if __name__ == "__main__":
    run_benchmark()
