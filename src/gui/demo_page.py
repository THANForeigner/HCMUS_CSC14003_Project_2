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
except ImportError:
    from gui.puzzle_manager import PuzzleManager
    from gui.solver_controller import SolverController

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

        # controls
        self.play_button = ft.ElevatedButton(content=ft.Text("Play"), on_click=self.on_play_pause)
        self.step_button = ft.ElevatedButton(content=ft.Text("Step"), on_click=self.on_manual_step)
        self.speed_slider = ft.Slider(min=0.05, max=1.0, divisions=19, value=0.25, label='{value}s', on_change=self.on_speed_change, width=180)

        self.controls = [
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(content=ft.Text("< Back"), on_click=lambda _: page.go("/")),
                    ft.Text("Algorithm Demonstration", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(content=ft.Text("Generate Solved"), on_click=self.on_generate),
                    ft.Container(width=10),
                    ft.ElevatedButton(content=ft.Text("Compute Solution"), on_click=self.on_compute_solution),
                    ft.Container(width=10),
                    self.play_button,
                    ft.Container(width=8),
                    self.step_button,
                    ft.Container(width=12),
                    ft.Row([ft.Text("Speed:"), self.speed_slider], alignment=ft.MainAxisAlignment.CENTER)
                ], alignment=ft.MainAxisAlignment.START),
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
        self._auto_playing = False

        # solver
        self.pmanager = PuzzleManager()
        self.solver = SolverController()

        # initial
        self.build_empty_board()
        self._is_initialized = True

    def build_empty_board(self):
        n = self.size
        self.grid = [[0 for _ in range(n)] for _ in range(n)]
        self.h_constraints = [[0 for _ in range(n-1)] for _ in range(n)]
        self.v_constraints = [[0 for _ in range(n)] for _ in range(n-1)]
        self._render_board()

    def _render_board(self):
        # create editable-looking grid of text fields (read-only for demo)
        n = self.size
        self.cells = []
        board_rows = []
        for r in range(n):
            row_controls = []
            row_cells = []
            for c in range(n):
                tf = ft.TextField(value="", width=60, height=60, text_align=ft.TextAlign.CENTER, text_size=24, read_only=True)
                row_controls.append(tf)
                row_cells.append(tf)
                if c < n-1:
                    sym = ""
                    row_controls.append(ft.Container(content=ft.Text(sym, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400), width=30, alignment=ft.Alignment(0,0)))
            self.cells.append(row_cells)
            board_rows.append(ft.Row(controls=row_controls, alignment=ft.MainAxisAlignment.CENTER))
            if r < n-1:
                v_controls = []
                for c in range(n):
                    v_controls.append(ft.Container(content=ft.Text("", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400), width=60, alignment=ft.Alignment(0,0)))
                    if c < n-1:
                        v_controls.append(ft.Container(width=30))
                board_rows.append(ft.Row(controls=v_controls, alignment=ft.MainAxisAlignment.CENTER))

        column = ft.Column(controls=board_rows, alignment=ft.MainAxisAlignment.CENTER)
        self.controls[2].content = column
        if self._is_initialized:
            self._page.update()

    def on_generate(self, e):
        try:
            grid, h, v = self.pmanager.generate_solved(self.size)
            self.grid = grid
            self.h_constraints = h
            self.v_constraints = v
            # create a partially blanked puzzle to demonstrate reveal
            import random
            blanks = max(1, (self.size * self.size) // 2)
            # start from full solution
            self._original_grid = [row[:] for row in grid]
            # blank random cells in original_grid
            indices = [(r, c) for r in range(self.size) for c in range(self.size)]
            random.shuffle(indices)
            for (r, c) in indices[:blanks]:
                self._original_grid[r][c] = 0
            # UI shows original (with blanks)
            for r in range(self.size):
                for c in range(self.size):
                    val = self._original_grid[r][c]
                    self.cells[r][c].value = str(val) if val != 0 else ""
            self.status.value = "Generated demo puzzle (partially blank)"
            self._page.update()
        except Exception as ex:
            self.status.value = f"Generate failed: {ex}"
            self._page.update()

    def on_compute_solution(self, e):
        # run solver full to get solution, then prepare steps for interactive reveal
        def callback(solution, stats):
            if solution is None:
                self.status.value = "No solution found"
                self._page.update()
                return
            self.status.value = "Solution computed — ready to reveal"
            self._solution = solution
            # prepare steps: reveal empty cells only
            steps = []
            for r in range(self.size):
                for c in range(self.size):
                    if self._original_grid is not None and self._original_grid[r][c] == 0:
                        steps.append((r, c, solution[r][c]))
            self._steps = steps
            self.step_player.set_steps(self._steps, self._step_callback)
            self._page.update()

        # start solver in background
        self.status.value = "Solving..."
        self._page.update()
        # run solver on the puzzle with blanks (original grid)
        puzzle_grid = self._original_grid if self._original_grid is not None else self.grid
        self.solver.run_full(self.size, puzzle_grid, self.h_constraints, self.v_constraints, callback=callback)

    def _step_callback(self, r, c, val):
        self.cells[r][c].value = str(val)
        self._page.update()

    def on_play_pause(self, e):
        if not self._steps:
            return
        if not self.step_player.is_running():
            # start auto play
            delay = float(self.speed_slider.value)
            self.step_player.start_auto(delay=delay)
            self.play_button.content = ft.Text("Pause")
        else:
            # pause
            self.step_player.pause()
            self.play_button.content = ft.Text("Play")
        self._page.update()

    def on_manual_step(self, e):
        if not self._steps:
            return
        self.step_player.step_once()

    def on_speed_change(self, e):
        # adjust delay for running player
        try:
            delay = float(self.speed_slider.value)
            self.step_player._delay = delay
        except Exception:
            pass
