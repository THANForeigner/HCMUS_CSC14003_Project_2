import os
import flet as ft
import sys
import asyncio

# Ensure src directory is in path to allow imports
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, base_dir)

try:
    from src.io_handler import read_input
except ImportError:
    pass

try:
    from src.gui.puzzle_manager import PuzzleManager
except ImportError:
    from gui.puzzle_manager import PuzzleManager

# Nord Theme Palette
POLAR_NIGHT_0 = "#2E3440"
POLAR_NIGHT_1 = "#3B4252"
POLAR_NIGHT_2 = "#434C5E"
POLAR_NIGHT_3 = "#4C566A"
SNOW_STORM_0 = "#D8DEE9"
SNOW_STORM_1 = "#E5E9F0"
SNOW_STORM_2 = "#ECEFF4"
FROST_0 = "#8FBCBB"
FROST_1 = "#88C0D0"
FROST_2 = "#81A1C1"
FROST_3 = "#5E81AC"
AURORA_RED = "#BF616A"
AURORA_ORANGE = "#D08770"
AURORA_YELLOW = "#EBCB8B"
AURORA_GREEN = "#A3BE8C"
AURORA_PURPLE = "#B48EAD"

class PuzzlePage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/puzzle", bgcolor=POLAR_NIGHT_0)
        self._page = page
        self._is_initialized = False
        self.size = 0
        self.grid_data = []
        self.h_constraints = []
        self.v_constraints = []
        self.cells = []
        
        # UI Elements
        self.status_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=SNOW_STORM_0)
        self.board_container = ft.Container(padding=20, expand=True)
        self.numpad_container = ft.Container(
            content=ft.Text("Select a cell", color=POLAR_NIGHT_3, italic=True),
            width=200,
            padding=20,
            alignment=ft.Alignment(0, 0)
        )
        
        self.file_dropdown = ft.Dropdown(
            width=200,
            on_select=self.on_file_selected,
            bgcolor=POLAR_NIGHT_1,
            color=SNOW_STORM_2,
            border_color=POLAR_NIGHT_3,
            focused_border_color=FROST_1
        )
        self.load_available_files()
        
        self.algorithm_dropdown = ft.Dropdown(
            width=180,
            value='backtrack',
            options=[
                ft.dropdown.Option('backtrack', text='Backtracking'),
                ft.dropdown.Option('brute_force', text='Brute Force'),
                ft.dropdown.Option('astar', text="A* (heuristic h3)"),
                ft.dropdown.Option('astar_ac3', text='A* + AC3')
            ],
            bgcolor=POLAR_NIGHT_1,
            color=SNOW_STORM_2,
            border_color=POLAR_NIGHT_3,
            focused_border_color=FROST_1
        )

        self.play_button = ft.IconButton(icon=ft.Icons.PLAY_ARROW, on_click=self.on_play_pause, icon_color=FROST_1, tooltip="Play/Pause")
        self.step_button = ft.IconButton(icon=ft.Icons.SKIP_NEXT, on_click=self.on_manual_step, icon_color=FROST_1, tooltip="Next Step")
        self.speed_slider = ft.Slider(min=0.01, max=1.0, value=0.1, width=120, on_change=self.on_speed_change, active_color=FROST_1)

        # Control panel
        self.controls = [
            ft.Container(
                content=ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: page.go("/"), icon_color=SNOW_STORM_0),
                    ft.VerticalDivider(width=1, color=POLAR_NIGHT_3),
                    ft.Text("Puzzle:", size=14, color=FROST_2),
                    self.file_dropdown,
                    ft.VerticalDivider(width=1, color=POLAR_NIGHT_3),
                    ft.Text("Algo:", size=14, color=FROST_2),
                    self.algorithm_dropdown,
                    ft.VerticalDivider(width=1, color=POLAR_NIGHT_3),
                    ft.ElevatedButton(
                        content=ft.Text("Solve"),
                        on_click=self.solve_puzzle,
                        style=ft.ButtonStyle(bgcolor=FROST_3, color=SNOW_STORM_2)
                    ),
                    ft.VerticalDivider(width=1, color=POLAR_NIGHT_3),
                    self.play_button,
                    self.step_button,
                    ft.Row([ft.Text("Speed", size=12, color=SNOW_STORM_0), self.speed_slider], spacing=5),
                    ft.Container(expand=True),
                    ft.TextButton("Clear", on_click=self.clear_board, style=ft.ButtonStyle(color=AURORA_RED))
                ], alignment=ft.MainAxisAlignment.START, spacing=15),
                padding=15,
                bgcolor=POLAR_NIGHT_1,
                border_radius=15,
                margin=ft.margin.only(left=20, right=20, top=10)
            ),
            ft.Row(
                [
                    self.board_container,
                    ft.VerticalDivider(width=1, color=POLAR_NIGHT_3),
                    self.numpad_container
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(
                        content=ft.Text("Check Solution", weight=ft.FontWeight.BOLD), 
                        on_click=self.check_win,
                        style=ft.ButtonStyle(
                            bgcolor=AURORA_GREEN, 
                            color=POLAR_NIGHT_0,
                            shape=ft.RoundedRectangleBorder(radius=10)
                        ),
                        height=45,
                        width=180
                    ),
                    ft.Container(width=20),
                    self.status_text
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=25
            )
        ]

        # Solver and StepPlayer setup
        try:
            from src.gui.solver_controller import SolverController
            from src.gui.step_player import StepPlayer
        except ImportError:
            from gui.solver_controller import SolverController
            from gui.step_player import StepPlayer

        self.solver = SolverController()
        self.step_player = StepPlayer()
        self._solution = None
        self._original_grid = None
        self._active_cell = None # (r, c)
        self._bottom_sheet = None

        if self.file_dropdown.options:
            self.file_dropdown.value = self.file_dropdown.options[0].key
            self.load_puzzle(self.file_dropdown.value)

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
        self.page.update()

    async def generate_solved(self, e):
        try:
            size = self.size if self.size >= 2 else 5
            pm = PuzzleManager()
            grid, h_constraints, v_constraints = pm.generate_solved(size)
            self.size, self.grid_data, self.h_constraints, self.v_constraints = size, grid, h_constraints, v_constraints
            self._original_grid = [row[:] for row in grid]
            self.build_board()
            self.status_text.value = "Generated solved puzzle"
            self.status_text.color = AURORA_GREEN
        except Exception as ex:
            self.status_text.value = f"Generate failed: {ex}"
            self.status_text.color = AURORA_RED
        self.page.update()

    async def clear_board(self, e):
        for r in range(self.size):
            for c in range(self.size):
                if self.grid_data[r][c] == 0:
                    self.cells[r][c].content.value = ""
                    self.cells[r][c].bgcolor = POLAR_NIGHT_2
        self.validate_board()

    def load_puzzle(self, filename):
        if not filename: return
        filepath = os.path.join(base_dir, "inputs", filename)
        try:
            self.size, self.grid_data, (self.h_constraints, self.v_constraints) = read_input(filepath)
            self._original_grid = [row[:] for row in self.grid_data]
            self.build_board()
        except Exception as e:
            self.status_text.value = f"Load error: {e}"
            self.status_text.color = AURORA_RED

    def build_board(self):
        self.cells = []
        board_rows = []
        for r in range(self.size):
            row_controls = []
            row_cells = []
            for c in range(self.size):
                val = self.grid_data[r][c]
                is_fixed = val != 0
                
                cell_content = ft.Text(
                    value=str(val) if is_fixed else "",
                    size=22, weight=ft.FontWeight.BOLD,
                    color=SNOW_STORM_2 if is_fixed else FROST_1
                )
                
                cell_container = ft.Container(
                    content=cell_content,
                    alignment=ft.alignment.Alignment(0, 0),
                    width=55, height=55,
                    bgcolor=POLAR_NIGHT_1 if is_fixed else POLAR_NIGHT_2,
                    border_radius=8,
                    data=(r, c),
                    on_click=self._handle_cell_click,
                    on_hover=lambda e, row=r, col=c: self.on_cell_hover(e, row, col),
                    animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT_QUART),
                    animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
                )
                
                row_controls.append(cell_container)
                row_cells.append(cell_container)
                
                if c < self.size - 1:
                    h_val = self.h_constraints[r][c]
                    txt = "<" if h_val == 1 else ">" if h_val == -1 else ""
                    row_controls.append(ft.Container(content=ft.Text(txt, size=18, color=FROST_3, weight=ft.FontWeight.BOLD), alignment=ft.alignment.Alignment(0, 0), width=25))
            
            self.cells.append(row_cells)
            board_rows.append(ft.Row(controls=row_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=5))
            
            if r < self.size - 1:
                v_controls = []
                for c in range(self.size):
                    v_val = self.v_constraints[r][c]
                    txt = "^" if v_val == 1 else "v" if v_val == -1 else ""
                    v_controls.append(ft.Container(content=ft.Text(txt, size=18, color=FROST_3, weight=ft.FontWeight.BOLD), alignment=ft.alignment.Alignment(0, 0), width=55))
                    if c < self.size - 1: v_controls.append(ft.Container(width=25))
                board_rows.append(ft.Row(controls=v_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=5))

        self.board_container.content = ft.Column(controls=board_rows, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
        self.validate_board()

    def on_cell_hover(self, e, r, c):
        # Highlight row and column
        is_hover = e.data == "true"
        target_color = POLAR_NIGHT_3 if is_hover else None
        
        for i in range(self.size):
            if i != c:
                cell = self.cells[r][i]
                if not target_color:
                    cell.bgcolor = POLAR_NIGHT_1 if self.grid_data[r][i] != 0 else POLAR_NIGHT_2
                else: cell.bgcolor = target_color
            if i != r:
                cell = self.cells[i][c]
                if not target_color:
                    cell.bgcolor = POLAR_NIGHT_1 if self.grid_data[i][c] != 0 else POLAR_NIGHT_2
                else: cell.bgcolor = target_color
        
        self.cells[r][c].scale = 1.1 if is_hover else 1.0
        self.page.update()

    async def _handle_cell_click(self, e):
        r, c = e.control.data
        await self.on_cell_click(r, c)

    async def on_cell_click(self, r, col_idx):
        if self.grid_data[r][col_idx] != 0: return # Fixed
        
        self._active_cell = (r, col_idx)
        
        # Highlight active cell
        for row in self.cells:
            for cell in row:
                if cell.border: cell.border = None
        self.cells[r][col_idx].border = ft.border.all(2, FROST_1)
        
        # Build Side-panel numpad
        n = self.size
        buttons = []
        for i in range(1, n + 1):
            async def make_on_click(val):
                async def handler(e): await self.on_numpad_select(val)
                return handler
                
            buttons.append(
                ft.ElevatedButton(
                    content=ft.Text(str(i)),
                    on_click=await make_on_click(i),
                    width=50, height=50,
                    style=ft.ButtonStyle(
                        bgcolor=POLAR_NIGHT_2,
                        color=FROST_1,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=0
                    )
                )
            )
        
        async def clear_handler(e): await self.on_numpad_select(0)
        buttons.append(
            ft.ElevatedButton(
                content=ft.Text("X"),
                on_click=clear_handler,
                width=50, height=50,
                style=ft.ButtonStyle(
                    bgcolor=AURORA_RED,
                    color=SNOW_STORM_2,
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=0
                )
            )
        )
        
        self.numpad_container.content = ft.Column([
            ft.Text(f"Cell ({r+1},{col_idx+1})", size=16, weight=ft.FontWeight.BOLD, color=FROST_2),
            ft.Container(height=10),
            ft.Row(buttons, wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.update()

    async def on_numpad_select(self, val):
        if self._active_cell:
            r, c = self._active_cell
            self.cells[r][c].content.value = str(val) if val != 0 else ""
            self.cells[r][c].border = None
            self._active_cell = None
            
            # Reset numpad container
            self.numpad_container.content = ft.Text("Select a cell", color=POLAR_NIGHT_3, italic=True)
            
            self.validate_board()
            self.page.update()

    def validate_board(self):
        current = [[int(self.cells[r][c].content.value) if self.cells[r][c].content.value else 0 for c in range(self.size)] for r in range(self.size)]
        has_error = False
        for r in range(self.size):
            for c in range(self.size):
                self.cells[r][c].bgcolor = POLAR_NIGHT_1 if self.grid_data[r][c] != 0 else POLAR_NIGHT_2
        
        for r in range(self.size):
            for c in range(self.size):
                val = current[r][c]
                if val == 0: continue
                if current[r].count(val) > 1 or [current[i][c] for i in range(self.size)].count(val) > 1:
                    self.cells[r][c].bgcolor = AURORA_RED
                    has_error = True
                if c < self.size - 1:
                    h = self.h_constraints[r][c]
                    if h == 1 and current[r][c+1] != 0 and not (val < current[r][c+1]):
                        self.cells[r][c].bgcolor = self.cells[r][c+1].bgcolor = AURORA_ORANGE; has_error = True
                    if h == -1 and current[r][c+1] != 0 and not (val > current[r][c+1]):
                        self.cells[r][c].bgcolor = self.cells[r][c+1].bgcolor = AURORA_ORANGE; has_error = True
                if r < self.size - 1:
                    v = self.v_constraints[r][c]
                    if v == 1 and current[r+1][c] != 0 and not (val < current[r+1][c]):
                        self.cells[r][c].bgcolor = self.cells[r+1][c].bgcolor = AURORA_ORANGE; has_error = True
                    if v == -1 and current[r+1][c] != 0 and not (val > current[r+1][c]):
                        self.cells[r][c].bgcolor = self.cells[r+1][c].bgcolor = AURORA_ORANGE; has_error = True
        
        self.status_text.value = "Conflict detected" if has_error else ""
        self.status_text.color = AURORA_RED
        if self._is_initialized: self.page.update()

    async def check_win(self, e):
        self.validate_board()
        if self.status_text.value: return
        for r in range(self.size):
            for c in range(self.size):
                if not self.cells[r][c].content.value:
                    self.status_text.value = "Incomplete board"; self.status_text.color = AURORA_ORANGE
                    self.page.update(); return
        self.status_text.value = "Perfect Solution!"; self.status_text.color = AURORA_GREEN
        self.page.update()

    async def solve_puzzle(self, e):
        async def on_result(solution, stats, steps=None):
            if solution is None:
                self.status_text.value = "No solution found"; self.status_text.color = AURORA_RED
            else:
                self.status_text.value = f"Solved: {stats.get('nodes_generated','?')} nodes"; self.status_text.color = AURORA_GREEN
            self.page.update()

        self.status_text.value = "Solving..."; self.status_text.color = FROST_1; self.page.update()
        async def event_callback(action, r, c, val):
            if action == 'check': self.cells[r][c].bgcolor = AURORA_YELLOW
            elif action == 'assign':
                self.cells[r][c].content.value = str(val); self.cells[r][c].bgcolor = AURORA_GREEN; self.cells[r][c].scale = 1.1
                await asyncio.sleep(0.05); self.cells[r][c].scale = 1.0
            elif action == 'backtrack':
                if self._original_grid[r][c] == 0: self.cells[r][c].content.value = ""
                self.cells[r][c].bgcolor = AURORA_RED
            self.page.update()

        await self.step_player.start_streaming(event_callback, delay=self.speed_slider.value)
        await self.solver.run_with_history(self.size, self.grid_data, self.h_constraints, self.v_constraints, callback=on_result, algorithm=self.algorithm_dropdown.value, step_player=self.step_player)

    async def on_play_pause(self, e):
        if not self.step_player.is_running():
            await self.step_player.start_auto(delay=self.speed_slider.value)
            self.play_button.icon = ft.Icons.PAUSE
        else:
            if self.step_player.is_paused():
                self.step_player.resume(); self.play_button.icon = ft.Icons.PAUSE
            else:
                self.step_player.pause(); self.play_button.icon = ft.Icons.PLAY_ARROW
        self.page.update()

    async def on_manual_step(self, e):
        await self.step_player.step_once(); self.page.update()

    async def on_speed_change(self, e):
        self.step_player._delay = float(self.speed_slider.value)
