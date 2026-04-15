import os
import sys
import time
import logging
import tracemalloc
import matplotlib.pyplot as plt
import numpy as np
import signal
from datetime import datetime
from collections import defaultdict

class TimeoutException(BaseException):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Timeout")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.io_handler import read_input

# ============================================================
# SETUP LOGGING: in ra cả console lẫn file .log
# ============================================================
def setup_logging(log_dir):
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"benchmark_{timestamp}.log")

    logger = logging.getLogger("benchmark")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Ghi ra file
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(fh)

    # Hiển thị ra console
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)

    return logger, log_file

def log(msg=""):
    logging.getLogger("benchmark").info(msg)

# ============================================================
# PARSE ĐỘ KHÓ TỪ TÊN FILE
# Format: size4_easy_1.txt → difficulty = "easy"
# ============================================================
DIFFICULTIES = ["trivial", "easy", "tricky", "extreme"]

def parse_difficulty(filename):
    name = filename.lower()
    for diff in DIFFICULTIES:
        if diff in name:
            return diff
    return "unknown"

# ============================================================
# VALIDATOR
# ============================================================
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

# ============================================================
# GỌI THUẬT TOÁN
# ============================================================
import copy
from test_futoshiki import FutoshikiEvaluator

def call_algorithm(algo_name, size, grid, h, v):
    grid_copy = copy.deepcopy(grid)
    inferences = 1
    solution = None
    constraint = [h, v]

    try:
        # NHÓM 1
        if algo_name == "Comparing algorithms":
            from src.algorithm.comparing_algorithms.brute_force_and_backtrack.backtrack import Backtrack
            solver = Backtrack(size, grid_copy, constraint)
            res = solver.solve()
            if res != "Contradiction": solution = solver.solution
            inferences = getattr(solver, 'nodes_explored', 1)

        elif algo_name == "Forward Chaining":
            from src.algorithm.first_order_logic.fc_no_backtrack import forward_chaining as FC_no_bt
            solver = FC_no_bt(size, grid_copy, constraint)
            res = solver.solve()
            if res[0] == "Solved": solution = solver.solution
            inferences = getattr(solver, 'nodes_explored', 1)

        elif algo_name == "Backward Chaining":
            from src.algorithm.first_order_logic.bc_no_backtrack import bc_no_backtrack as BC_std
            solver = BC_std(size, grid_copy, constraint)
            res = solver.solve()
            if res[0] == "Solved": solution = solver.solution
            inferences = getattr(solver, 'nodes_explored', 1)

        elif algo_name == "A* (Không kết hợp AC-3)":
            evaluator = FutoshikiEvaluator(size, grid_copy, h, v)
            res = evaluator.solve_astar(use_ac3=False)
            if res.get("solved"):
                solution = [[list(evaluator.domains[r][c])[0] for c in range(size)] for r in range(size)]
            inferences = res.get("nodes", 1)

        # NHÓM 2
        elif algo_name == "Dancing Links":
            from src.algorithm.comparing_algorithms.dancing_links.dlx_futoshiki import DLXFutoshiki
            solver = DLXFutoshiki(size, grid_copy, constraint)
            res = solver.solve()
            solution = getattr(solver, "solution", None)
            inferences = getattr(solver, 'nodes_explored', 1)

        elif algo_name == "A* kết hợp AC-3":
            evaluator = FutoshikiEvaluator(size, grid_copy, h, v)
            res = evaluator.solve_astar(use_ac3=True)
            if res.get("solved"):
                solution = [[list(evaluator.domains[r][c])[0] for c in range(size)] for r in range(size)]
            inferences = res.get("nodes", 1)

        elif algo_name == "Forward Chaining kết hợp Backtracking":
            from src.algorithm.first_order_logic.forward_chaining import forward_chaining as FC
            solver = FC(size, grid_copy, constraint)
            res = solver.solve()
            if res[0] == "Solved": solution = solver.solution
            inferences = getattr(solver, 'nodes_explored', 1)

        elif algo_name == "Backward Chaining (bản cải tiến)":
            from src.algorithm.first_order_logic.backward_chaining import backward_chaining as BC_adv
            solver = BC_adv(size, grid_copy, constraint)
            res = solver.solve()
            if res[0] == "Solved": solution = solver.solution
            inferences = getattr(solver, 'nodes_explored', 1)

        elif algo_name == "Backward Chaining kết hợp AC-3":
            evaluator = FutoshikiEvaluator(size, grid_copy, h, v)
            res = evaluator.solve_bc_ac3()
            if res.get("solved"):
                solution = [[list(evaluator.domains[r][c])[0] for c in range(size)] for r in range(size)]
            inferences = res.get("nodes", 1)

    except RecursionError:
        pass
    except Exception:
        pass

    return solution, inferences

# ============================================================
# VẼ BIỂU ĐỒ (theo từng độ khó)
# ============================================================
MARKERS = ['o', 's', '^', 'D', 'v', 'P', 'X', '*', 'h']

def plot_metrics(results_by_diff, algorithm_groups, plot_dir):
    """
    results_by_diff: { difficulty: { algo: { sizes, time, memory, accuracy, inferences } } }
    """
    os.makedirs(plot_dir, exist_ok=True)

    metrics = {
        "time":       "Execution Time (s)",
        "memory":     "Memory Usage (MB)",
        "accuracy":   "Accuracy (%)",
        "inferences": "Inferences (Nodes)",
    }

    all_algos = algorithm_groups["Nhóm 1"] + algorithm_groups["Nhóm 2"]

    for diff, results in results_by_diff.items():
        # Bỏ qua nếu không có dữ liệu nào
        has_data = any(results[a]["sizes"] for a in all_algos)
        if not has_data:
            continue

        for key, ylabel in metrics.items():
            fig, axes = plt.subplots(1, 2, figsize=(15, 6))
            fig.suptitle(
                f"[{diff.upper()}] Tương quan {ylabel} theo Grid Size",
                fontsize=14, fontweight="bold"
            )

            for idx, (group_name, algos) in enumerate(algorithm_groups.items()):
                ax = axes[idx]
                for m_idx, algo in enumerate(algos):
                    data = results[algo]
                    if not data["sizes"]:
                        continue
                    ax.plot(
                        data["sizes"], data[key],
                        marker=MARKERS[m_idx % len(MARKERS)],
                        lw=2, label=algo
                    )

                ax.set_title(group_name, fontsize=12)
                ax.set_xlabel("Grid Size (NxN)")
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

# ============================================================
# MAIN BENCHMARK
# ============================================================
def run_benchmark():
    base_dir   = os.path.dirname(__file__)
    input_dir  = os.path.join(base_dir, "input")
    if not os.path.exists(input_dir):
        input_dir = os.path.join(base_dir, "inputs")
    if not os.path.exists(input_dir):
        print(f"Không tìm thấy thư mục input: {input_dir}")
        return

    plot_dir = os.path.join(base_dir, "plot")
    log_dir  = base_dir  # file .log nằm cùng thư mục test/

    logger, log_file = setup_logging(log_dir)

    algorithms = {
        "Nhóm 1": [
            "Comparing algorithms",
            "Forward Chaining",
            "Backward Chaining",
            "A* (Không kết hợp AC-3)",
        ],
        "Nhóm 2": [
            "Dancing Links",
            "A* kết hợp AC-3",
            "Forward Chaining kết hợp Backtracking",
            "Backward Chaining (bản cải tiến)",
            "Backward Chaining kết hợp AC-3",
        ],
    }
    all_algos = algorithms["Nhóm 1"] + algorithms["Nhóm 2"]

    # agg[difficulty][algo][size] = {t, m, a, i}
    agg = defaultdict(lambda: {a: defaultdict(lambda: {"t":[],"m":[],"a":[],"i":[]}) for a in all_algos})

    files = sorted(f for f in os.listdir(input_dir) if f.endswith(".txt"))

    log("=" * 60)
    log("BẮT ĐẦU CHẠY BENCHMARK")
    log(f"Log file: {log_file}")
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
            _nodes_ref  = [1]   # list để truyền nodes_explored ra khỏi timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(60)
            try:
                solved_grid, inferences = call_algorithm(algo, size, org_grid, h, v)
                _nodes_ref[0] = inferences
            except TimeoutException:
                inferences = _nodes_ref[0]  # lấy giá trị đếm được trước khi bị chém
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

    # ── Tính trung bình & vẽ biểu đồ ──
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

    plot_metrics(results_by_diff, algorithms, plot_dir)

    log("\n✅ BENCHMARK HOÀN TẤT!")
    log(f"   Biểu đồ: {plot_dir}/")
    log(f"   Log:     {log_file}")

if __name__ == "__main__":
    run_benchmark()
