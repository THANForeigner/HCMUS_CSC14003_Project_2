import os
import sys
import threading
import flet as ft

# Ensure imports can resolve during different run modes
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

try:
    from src.gui.puzzle_manager import PuzzleManager
    from src.gui.solver_controller import SolverController
    from src.io_handler import read_input
except ImportError:
    from gui.puzzle_manager import PuzzleManager
    from gui.solver_controller import SolverController
    from io_handler import read_input

class DemoPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/demo")
        self._page = page
        self._is_initialized = False
        self.size = 5
        self.grid = []
        self.h_constraints = []
        self.v_constraints = []
        self.cells = []
        self.status = ft.Text("", size=16)

        # Dropdowns
        self.file_dropdown = ft.Dropdown(
            width=180,
            on_select=self.on_file_selected
        )
        self.load_available_files()

        self.algorithm_dropdown = ft.Dropdown(
            width=180,
            value='backtrack',
            options=[
                ft.dropdown.Option('backtrack', text='Backtracking'),
                ft.dropdown.Option('brute_force', text='Brute Force'),
                ft.dropdown.Option('backward_chaining_with_ac3', text='Backward Chaining with AC3'),
                ft.dropdown.Option('backward_chaining', text='Backward Chaining'),
                ft.dropdown.Option('bc_no_backtrack', text='Backward Chaining No Backtrack'),
                ft.dropdown.Option('forward_chaining', text='Forward Chaining'),
                ft.dropdown.Option('fc_with_backtrack', text='Forward Chaining with Backtrack'),
                ft.dropdown.Option('dancing_links', text='Dancing Links'),
                ft.dropdown.Option('astar_h2', text='A* (h2)'),
                ft.dropdown.Option('astar_h1', text='A* (h1)'),
                ft.dropdown.Option('astar_h3', text='A* (h3)'),
                ft.dropdown.Option('astar_ac3_h1', text='A* with AC3 (h1)'),
                ft.dropdown.Option('astar_ac3_h2', text='A* with AC3 (h2)'),
                ft.dropdown.Option('astar_ac3_h3', text='A* with AC3 (h3)'),
            ]
        )

        # controls
        self.speed_slider = ft.Slider(min=0.05, max=1.0, divisions=19, value=0.25, label='{value}s', on_change=self.on_speed_change, width=150)

        self.controls = [
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(content=ft.Text("< Back"), on_click=lambda _: page.go("/")),
                    ft.Text("Test:", size=16, weight=ft.FontWeight.BOLD),
                    self.file_dropdown,
                    ft.Text("Algo:", size=16, weight=ft.FontWeight.BOLD),
                    self.algorithm_dropdown,
                    ft.ElevatedButton(content=ft.Text("Compute Solution"), on_click=self.on_compute_solution),
                    ft.Row([ft.Text("Speed:"), self.speed_slider], alignment=ft.MainAxisAlignment.CENTER)
                ], alignment=ft.MainAxisAlignment.START, wrap=True),
                padding=20
            ),
            ft.Container(content=self.status, padding=10),
            ft.Container(content=ft.Column([], alignment=ft.MainAxisAlignment.CENTER), expand=True, alignment=ft.Alignment(0,0))
        ]

        # step player
        try:
            from src.gui.step_player import StepPlayer
        except ImportError:
            from gui.step_player import StepPlayer
        self.step_player = StepPlayer()
        self._steps = []
        self._solution = None
        self._original_grid = None

        # solver
        self.pmanager = PuzzleManager()
        self.solver = SolverController()

        # initial setup
        if self.file_dropdown.options:
            self.file_dropdown.value = self.file_dropdown.options[0].key
            self.load_puzzle(self.file_dropdown.value)
        else:
            self.build_empty_board()
            
        self._is_initialized = True

    def load_available_files(self):
        inputs_dir = os.path.join(base_dir, "inputs")
        files = []
        if os.path.exists(inputs_dir):
            for f in os.listdir(inputs_dir):
                if f.endswith(".txt") and f.startswith("input-"):
                    files.append(f)
        files.sort()
        self.file_dropdown.options = [ft.dropdown.Option(f) for f in files]

    def on_file_selected(self, e):
        self.load_puzzle(e.control.value)
        self._page.update()

    def load_puzzle(self, filename):
        if not filename: return
        filepath = os.path.join(base_dir, "inputs", filename)
        self.status.value = ""
        try:
            self.size, self.grid, constraints = read_input(filepath)
            self.h_constraints, self.v_constraints = constraints
            self._original_grid = [row[:] for row in self.grid]
            self._render_board()
        except Exception as e:
            self.status.value = f"Failed to load: {e}"
            self._page.update()

    def build_empty_board(self):
        n = self.size
        self.grid = [[0 for _ in range(n)] for _ in range(n)]
        self.h_constraints = [[0 for _ in range(n-1)] for _ in range(n)]
        self.v_constraints = [[0 for _ in range(n)] for _ in range(n-1)]
        self._original_grid = [row[:] for row in self.grid]
        self._render_board()

    def _render_board(self):
        n = self.size
        self.cells = []
        board_rows = []
        for r in range(n):
            row_controls = []
            row_cells = []
            for c in range(n):
                val = self._original_grid[r][c] if self._original_grid else 0
                tf = ft.TextField(
                    value=str(val) if val != 0 else "", 
                    width=60, height=60, text_align=ft.TextAlign.CENTER, 
                    text_size=24, read_only=True,
                    bgcolor=ft.Colors.BLUE_900 if val != 0 else ft.Colors.GREY_900
                )
                row_controls.append(tf)
                row_cells.append(tf)
                if c < n-1:
                    h_val = self.h_constraints[r][c]
                    sym = "<" if h_val == 1 else ">" if h_val == -1 else ""
                    row_controls.append(ft.Container(content=ft.Text(sym, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400), width=30, alignment=ft.Alignment(0,0)))
            self.cells.append(row_cells)
            board_rows.append(ft.Row(controls=row_controls, alignment=ft.MainAxisAlignment.CENTER))
            if r < n-1:
                v_controls = []
                for c in range(n):
                    v_val = self.v_constraints[r][c]
                    sym = "^" if v_val == 1 else "v" if v_val == -1 else ""
                    v_controls.append(ft.Container(content=ft.Text(sym, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400), width=60, alignment=ft.Alignment(0,0)))
                    if c < n-1:
                        v_controls.append(ft.Container(width=30))
                board_rows.append(ft.Row(controls=v_controls, alignment=ft.MainAxisAlignment.CENTER))

        column = ft.Column(controls=board_rows, alignment=ft.MainAxisAlignment.CENTER)
        self.controls[2].content = column
        
        if self.step_player.is_running() or self.step_player.is_paused():
            self.step_player.stop()
            
        if self._is_initialized:
            self._page.update()

    def on_compute_solution(self, e):
        def callback(solution, stats, steps=None):
            if solution is None:
                self.status.value = "No solution found"
                self._page.update()
                return
            self.status.value = f"Solution computed (Nodes generated: {stats.get('nodes_generated', '?')}) — ready to reveal"
            self._solution = solution
            self._page.update()

        self.status.value = "Solving..."
        self._page.update()
        
        # Reset board visuals back to original values before solving/streaming
        for r in range(self.size):
            for c in range(self.size):
                val = self._original_grid[r][c] if self._original_grid is not None else self.grid[r][c]
                self.cells[r][c].value = str(val) if val != 0 else ""
                self.cells[r][c].bgcolor = ft.Colors.BLUE_900 if val != 0 else ft.Colors.GREY_900
        self._page.update()
        
        puzzle_grid = self._original_grid if self._original_grid is not None else self.grid
        algo = self.algorithm_dropdown.value
        
        # Start streaming mode on step_player
        self.step_player.start_streaming(self._event_callback, delay=self.delay_slider.value if hasattr(self, 'delay_slider') else 0.1)

        try:
            self.solver.run_with_history(self.size, puzzle_grid, self.h_constraints, self.v_constraints, callback=callback, algorithm=algo, step_player=self.step_player)
        except AttributeError:
            self.solver.run_full(self.size, puzzle_grid, self.h_constraints, self.v_constraints, callback=lambda sol, stats: callback(sol, stats, None), algorithm=algo)

    def _event_callback(self, action, r, c, val):
        if r < 0 or c < 0: return
        if action == 'check':
            self.cells[r][c].bgcolor = ft.Colors.AMBER_400
        elif action == 'assign':
            self.cells[r][c].value = str(val)
            self.cells[r][c].bgcolor = ft.Colors.GREEN_700
        elif action == 'backtrack':
            if self._original_grid[r][c] == 0:
                self.cells[r][c].value = ""
            self.cells[r][c].bgcolor = ft.Colors.RED_700
        elif action == 'expand':
            self.cells[r][c].bgcolor = ft.Colors.PURPLE_500
        elif action == 'gen':
            self.cells[r][c].value = str(val)
            self.cells[r][c].bgcolor = ft.Colors.YELLOW_700
        self._page.update()

    def _step_callback(self, r, c, val):
        self.cells[r][c].value = str(val)
        self.cells[r][c].bgcolor = ft.Colors.GREEN_700
        self._page.update()

    def on_speed_change(self, e):
        try:
            delay = float(self.speed_slider.value)
            self.step_player._delay = delay
        except Exception:
            pass