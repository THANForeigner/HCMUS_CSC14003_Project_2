import os
import flet as ft
import sys

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
    # allow running as package or module during development
    from gui.puzzle_manager import PuzzleManager


class PuzzlePage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/puzzle")
        self._page = page
        self._is_initialized = False
        self.size = 0
        self.grid_data = []
        self.h_constraints = []
        self.v_constraints = []
        self.cells = []
        
        # UI Elements
        self.status_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD)
        self.board_container = ft.Container(alignment=ft.Alignment(0, 0))
        self.file_dropdown = ft.Dropdown(
            width=250,
            on_select=self.on_file_selected
        )
        self.load_available_files()
        
        # algorithm selector
        self.algorithm_dropdown = ft.Dropdown(
            width=200,
            value='backtrack',
            options=[
                ft.dropdown.Option('backtrack', text='Backtracking'),
                ft.dropdown.Option('astar', text="A* (heuristic h3)"),
                ft.dropdown.Option('astar_ac3', text='A* + AC3')
            ]
        )

        # interactive controls
        self.play_button = ft.ElevatedButton(content=ft.Text("Play"), on_click=self.on_play_pause)
        self.step_button = ft.ElevatedButton(content=ft.Text("Step"), on_click=self.on_manual_step)
        self.speed_slider = ft.Slider(min=0.05, max=1.0, divisions=19, value=0.25, width=140, on_change=self.on_speed_change)

        # Build layout
        self.controls = [
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(content=ft.Text("< Back"), on_click=lambda _: page.go("/")),
                    ft.Text("Select Puzzle:", size=16, weight=ft.FontWeight.BOLD),
                    self.file_dropdown,
                    ft.Container(width=10),
                    ft.Text("Algorithm:", size=16, weight=ft.FontWeight.BOLD),
                    self.algorithm_dropdown,
                    ft.Container(width=10),
                    ft.ElevatedButton(content=ft.Text("Generate Solved"), on_click=self.generate_solved),
                    ft.Container(width=10),
                    ft.ElevatedButton(content=ft.Text("Solve"), on_click=self.solve_puzzle),
                    ft.Container(width=8),
                    self.play_button,
                    ft.Container(width=8),
                    self.step_button,
                    ft.Container(width=12),
                    ft.Row([ft.Text("Speed:"), self.speed_slider], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Text("Clear Board"), 
                        on_click=self.clear_board,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE)
                    )
                ], alignment=ft.MainAxisAlignment.START),
                padding=20
            ),
            ft.Container(
                content=self.board_container,
                expand=True,
                alignment=ft.Alignment(0, 0)
            ),
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(
                        ft.ElevatedButton(content=ft.Text("Check Solution")), 
                        on_click=self.check_win,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.GREEN_700, 
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=12)
                        ),
                        height=50,
                        width=200
                    ),
                    ft.Container(width=20),
                    self.status_text
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=30
            )
        ]

        if self.file_dropdown.options:
            self.file_dropdown.value = self.file_dropdown.options[0].key
            self.load_puzzle(self.file_dropdown.value)

        # solver controller
        try:
            from src.gui.solver_controller import SolverController
        except ImportError:
            from gui.solver_controller import SolverController
        self.solver = SolverController()

        # step player for interactive reveals
        try:
            from src.gui.step_player import StepPlayer
        except ImportError:
            from gui.step_player import StepPlayer
        self.step_player = StepPlayer()
        self._steps = []
        self._solution = None
        self._original_grid = None

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
        self.page.update()

    def generate_solved(self, e):
        # Generate a solved board (Phase 1 scaffold behavior)
        try:
            size = self.size if self.size and self.size >= 2 else 5
            pm = PuzzleManager()
            grid, h_constraints, v_constraints = pm.generate_solved(size)
            # update internal state and rebuild
            self.size = size
            self.grid_data = grid
            self.h_constraints = h_constraints
            self.v_constraints = v_constraints
            self._original_grid = [row[:] for row in grid]
            self.build_board()
            self.status_text.value = "Generated solved puzzle"
            self.status_text.color = ft.Colors.GREEN_400
        except Exception as ex:
            self.status_text.value = f"Generate failed: {ex}"
            self.status_text.color = ft.Colors.RED_400
        self.page.update()

    def clear_board(self, e):
        for r in range(self.size):
            for c in range(self.size):
                if self.grid_data[r][c] == 0:
                    self.cells[r][c].value = ""
        self.validate_board()

    def load_puzzle(self, filename):
        if not filename: return
        filepath = os.path.join(base_dir, "inputs", filename)
        self.status_text.value = ""
        
        try:
            self.size, self.grid_data, constraints = read_input(filepath)
            self.h_constraints, self.v_constraints = constraints
            self.build_board()
        except Exception as e:
            self.status_text.value = f"Failed to load: {e}"
            self.status_text.color = ft.Colors.RED
            self.board_container.content = None

    def on_cell_change(self, e):
        # Validate immediately on cell input changes
        self.validate_board()

    def build_board(self):
        self.cells = []
        board_rows = []
        
        for r in range(self.size):
            row_controls = []
            row_cells = []
            
            for c in range(self.size):
                val = self.grid_data[r][c]
                is_fixed = val != 0
                
                tf = ft.TextField(
                    value=str(val) if is_fixed else "",
                    width=60,
                    height=60,
                    text_align=ft.TextAlign.CENTER,
                    text_size=24,
                    read_only=is_fixed,
                    bgcolor=ft.Colors.BLUE_900 if is_fixed else ft.Colors.GREY_900,
                    border_color=ft.Colors.BLUE_700 if is_fixed else ft.Colors.GREY_700,
                    color=ft.Colors.WHITE if is_fixed else ft.Colors.CYAN_300,
                    content_padding=5,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    max_length=1,
                    on_change=self.on_cell_change
                )
                tf.input_filter = ft.InputFilter(allow=True, regex_string=r"^[1-9]*$", replacement_string="")
                
                row_controls.append(tf)
                row_cells.append(tf)
                
                if c < self.size - 1:
                    h_val = self.h_constraints[r][c]
                    txt = ""
                    if h_val == 1: txt = "<"
                    elif h_val == -1: txt = ">"
                    
                    row_controls.append(
                        ft.Container(
                            content=ft.Text(txt, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400),
                            width=30,
                            alignment=ft.Alignment(0, 0)
                        )
                    )
                    
            self.cells.append(row_cells)
            board_rows.append(ft.Row(controls=row_controls, alignment=ft.MainAxisAlignment.CENTER))
            
            if r < self.size - 1:
                v_controls = []
                for c in range(self.size):
                    v_val = self.v_constraints[r][c]
                    txt = ""
                    if v_val == 1: txt = "^"
                    elif v_val == -1: txt = "v"
                    
                    v_controls.append(
                        ft.Container(
                            content=ft.Text(txt, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400),
                            width=60,
                            alignment=ft.Alignment(0, 0)
                        )
                    )
                    
                    if c < self.size - 1:
                        v_controls.append(ft.Container(width=30))
                        
                board_rows.append(ft.Row(controls=v_controls, alignment=ft.MainAxisAlignment.CENTER))
                
        self.board_container.content = ft.Column(controls=board_rows, alignment=ft.MainAxisAlignment.CENTER)
        self.validate_board()

    def validate_board(self):
        current_grid = []
        for r in range(self.size):
            row_vals = []
            for c in range(self.size):
                val_str = self.cells[r][c].value.strip()
                val = int(val_str) if val_str.isdigit() else 0
                row_vals.append(val)
            current_grid.append(row_vals)
            
        has_error = False

        # Reset cell colors to default
        for r in range(self.size):
            for c in range(self.size):
                is_fixed = self.grid_data[r][c] != 0
                self.cells[r][c].bgcolor = ft.Colors.BLUE_900 if is_fixed else ft.Colors.GREY_900
        
        # Check rows & columns for duplicate logic
        for r in range(self.size):
            for c in range(self.size):
                val = current_grid[r][c]
                if val == 0: continue
                
                # Exceeds bounds
                if val > self.size:
                    self.cells[r][c].bgcolor = ft.Colors.RED_900
                    has_error = True
                
                # Row duplicate check
                if current_grid[r].count(val) > 1:
                    self.cells[r][c].bgcolor = ft.Colors.RED_900
                    has_error = True
                    
                # Column duplicate check
                col_vals = [current_grid[i][c] for i in range(self.size)]
                if col_vals.count(val) > 1:
                    self.cells[r][c].bgcolor = ft.Colors.RED_900
                    has_error = True
                    
        # Check constraints (Horizontal & Vertical)
        for r in range(self.size):
            for c in range(self.size - 1):
                h = self.h_constraints[r][c]
                v1, v2 = current_grid[r][c], current_grid[r][c+1]
                if h != 0 and v1 != 0 and v2 != 0:
                    if h == 1 and not (v1 < v2):
                        self.cells[r][c].bgcolor = ft.Colors.RED_900
                        self.cells[r][c+1].bgcolor = ft.Colors.RED_900
                        has_error = True
                    if h == -1 and not (v1 > v2):
                        self.cells[r][c].bgcolor = ft.Colors.RED_900
                        self.cells[r][c+1].bgcolor = ft.Colors.RED_900
                        has_error = True
                        
        for r in range(self.size - 1):
            for c in range(self.size):
                v = self.v_constraints[r][c]
                v1, v2 = current_grid[r][c], current_grid[r+1][c]
                if v != 0 and v1 != 0 and v2 != 0:
                    if v == 1 and not (v1 < v2):
                        self.cells[r][c].bgcolor = ft.Colors.RED_900
                        self.cells[r+1][c].bgcolor = ft.Colors.RED_900
                        has_error = True
                    if v == -1 and not (v1 > v2):
                        self.cells[r][c].bgcolor = ft.Colors.RED_900
                        self.cells[r+1][c].bgcolor = ft.Colors.RED_900
                        has_error = True

        if has_error:
            self.status_text.value = "Conflict detected!"
            self.status_text.color = ft.Colors.RED_400
        else:
            self.status_text.value = ""

        if self._is_initialized:
            self._page.update()

    def check_win(self, e):
        self.validate_board()
        if self.status_text.value == "Conflict detected!":
            return
            
        for r in range(self.size):
            for c in range(self.size):
                if not self.cells[r][c].value.strip():
                    self.status_text.value = "Board is incomplete!"
                    self.status_text.color = ft.Colors.ORANGE_400
                    self.page.update()
                    return
                    
        self.status_text.value = "Valid Solution! Excellent!"
        self.status_text.color = ft.Colors.GREEN_400
        self.page.update()

    def solve_puzzle(self, e):
        # Run solver in background and update board on completion. Use history-enabled runner when available.
        def on_result(solution, stats, steps=None):
            if solution is None:
                self.status_text.value = "No solution found"
                self.status_text.color = ft.Colors.RED_400
                self.page.update()
                return

            # store solution and original grid
            self._solution = solution
            if not getattr(self, '_original_grid', None):
                self._original_grid = [row[:] for row in self.grid_data]

            # In streaming mode, the board is updated live. Here we just set the final text.
            self.status_text.value = f"Solved - nodes: {stats.get('nodes_generated', '?')} time: {stats.get('time', 0):.3f}s"
            self.status_text.color = ft.Colors.GREEN_400
            self.page.update()

        try:
            self.status_text.value = "Solving..."
            self.status_text.color = ft.Colors.ORANGE_400
            self.page.update()
            
            # prepare for new solve
            self._original_grid = [row[:] for row in self.grid_data]
            for r in range(self.size):
                for c in range(self.size):
                    is_fixed = self.grid_data[r][c] != 0
                    self.cells[r][c].value = str(self.grid_data[r][c]) if is_fixed and self.grid_data[r][c] != 0 else ""
                    self.cells[r][c].bgcolor = ft.Colors.BLUE_900 if is_fixed else ft.Colors.GREY_900
            self.page.update()

            def event_callback(action, r, c, val):
                try:
                    if action == 'check':
                        self.cells[r][c].bgcolor = ft.Colors.AMBER_400
                    elif action == 'assign':
                        self.cells[r][c].value = str(val)
                        self.cells[r][c].bgcolor = ft.Colors.GREEN_700
                    elif action == 'backtrack':
                        if self._original_grid[r][c] == 0:
                            self.cells[r][c].value = ""
                        self.cells[r][c].bgcolor = ft.Colors.RED_700
                    self.page.update()
                except Exception:
                    pass

            # Start the player in streaming mode
            self.step_player.start_streaming(event_callback, delay=self.delay_slider.value if hasattr(self, 'delay_slider') else 0.1)

            # prefer history-enabled run
            try:
                self.solver.run_with_history(self.size, self.grid_data, self.h_constraints, self.v_constraints, callback=on_result, algorithm=self.algorithm_dropdown.value, step_player=self.step_player)
            except AttributeError:
                # fallback to run_full
                self.solver.run_full(self.size, self.grid_data, self.h_constraints, self.v_constraints, callback=lambda sol, stats: on_result(sol, stats, None), algorithm=self.algorithm_dropdown.value)
        except Exception as ex:
            self.status_text.value = f"Solver error: {ex}"
            self.status_text.color = ft.Colors.RED_400
            self.page.update()

    def _update_cell_and_refresh(self, r, c, val):
        self.cells[r][c].value = str(val)
        self.page.update()

    def on_play_pause(self, e):
        if not self._steps and not self.step_player._streaming:
            return
        if not self.step_player.is_running():
            delay = float(self.speed_slider.value)
            self.step_player.start_auto(delay=delay)
            # update button label
            self.play_button.content = ft.Text("Pause")
        else:
            # toggle pause/resume
            if self.step_player.is_paused():
                self.step_player.resume()
                self.play_button.content = ft.Text("Pause")
            else:
                self.step_player.pause()
                self.play_button.content = ft.Text("Play")
        self.page.update()

    def on_manual_step(self, e):
        if not self._steps and not self.step_player._streaming:
            return
        self.step_player.step_once()

    def on_speed_change(self, e):
        try:
            delay = float(self.speed_slider.value)
            self.step_player._delay = delay
        except Exception:
            pass