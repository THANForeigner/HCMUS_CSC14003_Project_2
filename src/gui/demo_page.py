import os
import sys
import asyncio
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

try:
    from src.gui.step_player import StepPlayer
except ImportError:
    from gui.step_player import StepPlayer

from src.gui.theme import Win7Theme

class DemoPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/demo", bgcolor=Win7Theme.BG)
        self._page = page
        self._is_initialized = False
        self.size = 5
        self.grid = []
        self.h_constraints = []
        self.v_constraints = []
        self.cells = []
        self.status = ft.Text("", size=16, color=Win7Theme.TEXT_PRIMARY, weight=ft.FontWeight.BOLD)

        # Dropdowns
        self.file_dropdown = ft.Dropdown(
            width=180,
            on_select=self.on_file_selected,
            bgcolor=Win7Theme.CARD_BG, color=Win7Theme.TEXT_PRIMARY, border_color=Win7Theme.PANEL_BG
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
                ft.dropdown.Option('bc_no_backtrack', text='BC No Backtrack'),
                ft.dropdown.Option('forward_chaining', text='Forward Chaining'),
                ft.dropdown.Option('fc_with_backtrack', text='FC with Backtrack'),
                ft.dropdown.Option('dancing_links', text='Dancing Links'),
                ft.dropdown.Option('astar_h2', text='A* (h2)'),
                ft.dropdown.Option('astar_h1', text='A* (h1)'),
                ft.dropdown.Option('astar_h3', text='A* (h3)'),
                ft.dropdown.Option('astar_ac3_h1', text='A* AC3 (h1)'),
                ft.dropdown.Option('astar_ac3_h2', text='A* AC3 (h2)'),
                ft.dropdown.Option('astar_ac3_h3', text='A* AC3 (h3)'),
            ],
            bgcolor=Win7Theme.CARD_BG, color=Win7Theme.TEXT_PRIMARY, border_color=Win7Theme.PANEL_BG
        )

        self.speed_slider = ft.Slider(min=0.01, max=1.0, value=0.1, active_color=Win7Theme.PRIMARY, width=150, on_change=self.on_speed_change)

        self.board_container = ft.Container(
            content=ft.Column([], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.Alignment(0, 0),
            padding=20
        )

        self.controls = [
            ft.Container(
                content=ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/"), icon_color=Win7Theme.TEXT_PRIMARY),
                    ft.Text("Test:", size=14, color=Win7Theme.TEXT_SECONDARY),
                    self.file_dropdown,
                    ft.IconButton(icon=ft.Icons.REFRESH, on_click=lambda _: self.load_puzzle(self.file_dropdown.value), icon_color=Win7Theme.PRIMARY),
                    ft.Text("Algo:", size=14, color=Win7Theme.TEXT_SECONDARY),
                    self.algorithm_dropdown,
                    ft.ElevatedButton(
                        content=ft.Text("Demonstrate"),
                        on_click=self.on_compute_solution,
                        style=ft.ButtonStyle(bgcolor=Win7Theme.PRIMARY, color=Win7Theme.TEXT_INVERSE)
                    ),
                    ft.Row([ft.Text("Speed", size=12, color=Win7Theme.TEXT_PRIMARY), self.speed_slider], spacing=5)
                ], alignment=ft.MainAxisAlignment.START, wrap=True),
                padding=15, bgcolor=Win7Theme.HEADER_BG, border_radius=10, margin=10, border=ft.border.all(1, Win7Theme.PANEL_BG)
            ),
            ft.Row([self.status], alignment=ft.MainAxisAlignment.CENTER),
            self.board_container
        ]

        self.step_player = StepPlayer()
        self.solver = SolverController()
        self._original_grid = None

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

    async def on_file_selected(self, e):
        self.load_puzzle(e.control.value)
        self._page.update()

    def load_puzzle(self, filename):
        if not filename: return
        filepath = os.path.join(base_dir, "inputs", filename)
        try:
            self.size, self.grid, (self.h_constraints, self.v_constraints) = read_input(filepath)
            self._original_grid = [row[:] for row in self.grid]
            self._render_board()
        except Exception as e:
            self.status.value = f"Error: {e}"; self.status.color = Win7Theme.ERROR

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
                is_fixed = val != 0
                
                cell_container = ft.Container(
                    content=ft.Text(str(val) if is_fixed else "", size=22, weight=ft.FontWeight.BOLD, color=Win7Theme.CELL_TEXT_FIXED if is_fixed else Win7Theme.CELL_TEXT_EMPTY),
                    alignment=ft.Alignment(0, 0),
                    width=55, height=55, bgcolor=Win7Theme.CELL_FIXED_BG if is_fixed else Win7Theme.CELL_EMPTY_BG,
                    border_radius=4,
                    border=ft.border.all(1, Win7Theme.PANEL_BG),
                    animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT_QUART),
                    animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
                )
                row_controls.append(cell_container)
                row_cells.append(cell_container)
                if c < n-1:
                    h_val = self.h_constraints[r][c]
                    txt = "<" if h_val == 1 else ">" if h_val == -1 else ""
                    row_controls.append(ft.Container(content=ft.Text(txt, size=18, color=Win7Theme.CONSTRAINT, weight=ft.FontWeight.BOLD), alignment=ft.Alignment(0, 0), width=25))
            self.cells.append(row_cells)
            board_rows.append(ft.Row(controls=row_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=5))
            if r < n-1:
                v_controls = []
                for c in range(n):
                    v_val = self.v_constraints[r][c]
                    txt = "^" if v_val == 1 else "v" if v_val == -1 else ""
                    v_controls.append(ft.Container(content=ft.Text(txt, size=18, color=Win7Theme.CONSTRAINT, weight=ft.FontWeight.BOLD), alignment=ft.Alignment(0, 0), width=55))
                    if c < n-1: v_controls.append(ft.Container(width=25))
                board_rows.append(ft.Row(controls=v_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=5))

        self.board_container.content = ft.Column(controls=board_rows, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
        if self.step_player.is_running(): asyncio.create_task(self.step_player.stop())
        if self._is_initialized: self._page.update()

    async def on_compute_solution(self, e):
        async def callback(solution, stats, steps=None):
            if solution is None: self.status.value = "No solution found"; self.status.color = Win7Theme.ERROR
            else: self.status.value = f"Demo Finished. {stats.get('nodes_generated','?')} nodes."; self.status.color = Win7Theme.SUCCESS
            self._page.update()

        self.status.value = "Demonstrating..."; self.status.color = Win7Theme.PRIMARY; self._page.update()
        
        # Reset board visuals
        for r in range(self.size):
            for c in range(self.size):
                val = self._original_grid[r][c]
                self.cells[r][c].content.value = str(val) if val != 0 else ""
                self.cells[r][c].bgcolor = Win7Theme.CELL_FIXED_BG if val != 0 else Win7Theme.CELL_EMPTY_BG
        self._page.update()
        
        async def event_callback(action, r, c, val):
            if action == 'check': self.cells[r][c].bgcolor = Win7Theme.CHECK
            elif action == 'assign':
                self.cells[r][c].content.value = str(val); self.cells[r][c].bgcolor = Win7Theme.SUCCESS; self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE; self.cells[r][c].scale = 1.1
                await asyncio.sleep(0.05); self.cells[r][c].scale = 1.0
            elif action == 'backtrack':
                if self._original_grid[r][c] == 0: self.cells[r][c].content.value = ""
                self.cells[r][c].bgcolor = Win7Theme.ERROR; self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
            elif action == 'expand': self.cells[r][c].bgcolor = Win7Theme.SKY_LIGHT
            elif action == 'gen': self.cells[r][c].content.value = str(val); self.cells[r][c].bgcolor = Win7Theme.WARNING; self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
            self._page.update()

        await self.step_player.start_streaming(event_callback, delay=self.speed_slider.value)
        await self.solver.run_with_history(self.size, self._original_grid, self.h_constraints, self.v_constraints, callback=callback, algorithm=self.algorithm_dropdown.value, step_player=self.step_player)

    async def on_speed_change(self, e):
        self.step_player._delay = float(self.speed_slider.value)
