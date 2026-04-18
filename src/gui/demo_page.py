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
    from src.io_handler import read_input, get_test_inputs, get_input_filename
except ImportError:
    from gui.puzzle_manager import PuzzleManager
    from gui.solver_controller import SolverController
    from io_handler import read_input, get_test_inputs, get_input_filename

try:
    from src.gui.step_player import StepPlayer
except ImportError:
    from gui.step_player import StepPlayer

from src.gui.theme import Win7Theme


class DemoPage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/demo", bgcolor=Win7Theme.BG, scroll=ft.ScrollMode.AUTO)
        self._page = page
        self._is_initialized = False
        self.size = 5
        self.grid = []
        self.h_constraints = []
        self.v_constraints = []
        self.cells = []
        self._test_inputs_data = {}
        self.status = ft.Text(
            "", size=16, color=Win7Theme.TEXT_PRIMARY, weight=ft.FontWeight.BOLD
        )

        # Cascading Dropdowns
        self.size_dropdown = ft.Dropdown(
            label="Size",
            width=80,
            bgcolor=Win7Theme.CARD_BG,
            color=Win7Theme.TEXT_PRIMARY,
            border_color=Win7Theme.PANEL_BG,
        )
        self.size_dropdown.on_change = self.on_size_selected

        self.diff_dropdown = ft.Dropdown(
            label="Diff",
            width=100,
            bgcolor=Win7Theme.CARD_BG,
            color=Win7Theme.TEXT_PRIMARY,
            border_color=Win7Theme.PANEL_BG,
        )
        self.diff_dropdown.on_change = self.on_diff_selected

        self.id_dropdown = ft.Dropdown(
            label="ID",
            width=120,
            bgcolor=Win7Theme.CARD_BG,
            color=Win7Theme.TEXT_PRIMARY,
            border_color=Win7Theme.PANEL_BG,
        )
        self.id_dropdown.on_change = self.on_id_selected

        self.load_available_files()

        self.algorithm_dropdown = ft.Dropdown(
            width=200,
            value="astar_ac3",
            options=[
                ft.dropdown.Option("backtrack", text="Backtracking"),
                ft.dropdown.Option("brute_force", text="Brute Force"),
                ft.dropdown.Option("astar_h1", text="A* + h1 (Hamming)"),
                ft.dropdown.Option("astar_h2", text="A* + h2 "),
                ft.dropdown.Option("astar_h3", text="A* + h3 (MRV)"),
                ft.dropdown.Option("astar_ac3", text="A* + AC-3"),
                ft.dropdown.Option("astar_ac3_h1", text="A* + AC-3 + h1"),
                ft.dropdown.Option("astar_ac3_h2", text="A* + AC-3 + h2"),
                ft.dropdown.Option("astar_ac3_h3", text="A* + AC-3 + h3"),
                ft.dropdown.Option("backward_chaining_with_ac3", text="Backward Chaining + AC-3"),
                ft.dropdown.Option("backward_chaining", text="Backward Chaining"),
                ft.dropdown.Option("bc_no_backtrack", text="BC No Backtrack"),
                ft.dropdown.Option("forward_chaining", text="Forward Chaining"),
                ft.dropdown.Option("fc_with_backtrack", text="FC with Backtrack"),
                ft.dropdown.Option("dancing_links", text="Dancing Links"),
            ],
            bgcolor=Win7Theme.CARD_BG,
            color=Win7Theme.TEXT_PRIMARY,
            border_color=Win7Theme.PANEL_BG,
        )

        self.play_button = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW,
            on_click=self.on_play_pause,
            icon_color=Win7Theme.PRIMARY,
            tooltip="Play/Pause",
        )
        self.step_button = ft.IconButton(
            icon=ft.Icons.SKIP_NEXT,
            on_click=self.on_manual_step,
            icon_color=Win7Theme.PRIMARY,
            tooltip="Next Step",
        )
        self.speed_slider = ft.Slider(
            min=0.01,
            max=1.0,
            value=0.1,
            active_color=Win7Theme.PRIMARY,
            width=150,
            on_change=self.on_speed_change,
        )
        self.max_nodes_field = ft.TextField(
            label="Max Nodes",
            value="500000",
            width=100,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            tooltip="Max Nodes to Expand",
        )
        self.unlimited_nodes_checkbox = ft.Checkbox(
            label="Unlimited",
            value=False,
            on_change=self.on_unlimited_nodes_change,
            tooltip="Disable node limit",
        )
        self.solve_instantly_button = ft.IconButton(
            icon=ft.Icons.FAST_FORWARD,
            on_click=self.on_solve_instantly,
            icon_color=Win7Theme.PRIMARY,
            tooltip="Solve Instantly (No Delay)",
        )

        self.board_container = ft.Container(
            content=ft.Column(
                [],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.Alignment(0, 0),
            padding=20,
        )

        self.controls = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK,
                            on_click=lambda _: page.go("/"),
                            icon_color=Win7Theme.TEXT_PRIMARY,
                        ),
                        ft.Text("Test:", size=14, color=Win7Theme.TEXT_SECONDARY),
                        self.size_dropdown,
                        self.diff_dropdown,
                        self.id_dropdown,
                        ft.ElevatedButton(
                            content=ft.Text("Upload Test"),
                            on_click=self.hard_refresh_page,
                            style=ft.ButtonStyle(
                                bgcolor=Win7Theme.PRIMARY, color=Win7Theme.TEXT_INVERSE
                            ),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            on_click=self.refresh_puzzle,
                            icon_color=Win7Theme.PRIMARY,
                        ),
                        ft.Text("Algo:", size=14, color=Win7Theme.TEXT_SECONDARY),
                        self.algorithm_dropdown,
                        ft.ElevatedButton(
                            content=ft.Text("Demonstrate"),
                            on_click=self.on_compute_solution,
                            style=ft.ButtonStyle(
                                bgcolor=Win7Theme.PRIMARY, color=Win7Theme.TEXT_INVERSE
                            ),
                        ),
                        self.play_button,
                        self.step_button,
                        self.solve_instantly_button,
                        ft.Row(
                            [
                                ft.Text("Speed", size=12, color=Win7Theme.TEXT_PRIMARY),
                                self.speed_slider,
                            ],
                            spacing=5,
                        ),
                        ft.Text("Max Nodes:", size=12, color=Win7Theme.TEXT_PRIMARY),
                        self.max_nodes_field,
                        self.unlimited_nodes_checkbox,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    wrap=True,
                ),
                padding=15,
                bgcolor=Win7Theme.HEADER_BG,
                border_radius=10,
                margin=10,
                border=ft.border.all(1, Win7Theme.PANEL_BG),
            ),
            ft.Row([self.status], alignment=ft.MainAxisAlignment.CENTER),
            self.board_container,
        ]

        self.step_player = StepPlayer()
        self.solver = SolverController()
        self._original_grid = None
        self._solution_ready = False  # Track if solver has finished
        self._final_solution = None  # Store final solution for instant display

        if self.size_dropdown.options:
            self.size_dropdown.value = "4"
            asyncio.create_task(self.on_size_selected(None))
        else:
            self.build_empty_board()

        self._is_initialized = True
        
        # Schedule auto-start after initialization
        asyncio.create_task(self._auto_start_animation())

    def load_available_files(self):
        self._test_inputs_data = get_test_inputs()
        sizes = sorted(self._test_inputs_data.keys())
        self.size_dropdown.options = [ft.dropdown.Option(str(s)) for s in sizes]

    def _parse_dropdown_state(self):
        """Parse and return the current state of Size, Difficulty, and ID dropdowns"""
        state = {
            "size": self.size_dropdown.value,
            "difficulty": self.diff_dropdown.value,
            "id": self.id_dropdown.value,
        }
        return state

    def _sort_difficulties(self, diffs):
        """Sort difficulties in custom order: trivial, easy, tricky, extreme"""
        order = ["trivial", "easy", "tricky", "extreme"]
        return sorted(diffs, key=lambda x: order.index(x) if x in order else len(order))

    def _handle_address_input(self):
        """Capture and process the Address input field value"""
        # Removed - address field is no longer used
        pass

    async def hard_refresh_page(self, e):
        """Perform a hard refresh of the page"""
        state = self._parse_dropdown_state()
        if state["size"] and state["difficulty"] and state["id"]:
            await self.on_id_selected(None)
            self.status.value = "Page refreshed"
            self.status.color = Win7Theme.SUCCESS
        else:
            self.status.value = "Please select Size, Difficulty, and ID"
            self.status.color = Win7Theme.ERROR
        self._page.update()

    async def on_size_selected(self, e):
        try:
            state = self._parse_dropdown_state()
            size_val = state["size"]
            if not size_val:
                return
            size = int(size_val)

            diffs = self._sort_difficulties(self._test_inputs_data[size].keys())
            self.diff_dropdown.options = [ft.dropdown.Option(d) for d in diffs]

            # Auto-select 'trivial' if available, otherwise first option
            default_diff = "trivial" if "trivial" in diffs else diffs[0]
            self.diff_dropdown.value = default_diff

            # Trigger next cascade
            await self.on_diff_selected(None)
        except (TypeError, ValueError, KeyError):
            if self._is_initialized:
                self._page.update()

    async def on_diff_selected(self, e):
        try:
            state = self._parse_dropdown_state()
            size_val = state["size"]
            diff = state["difficulty"]
            if not size_val or not diff:
                return
            size = int(size_val)

            ids = sorted(self._test_inputs_data[size][diff].keys())
            self.id_dropdown.options = [ft.dropdown.Option(str(i)) for i in ids]

            # Auto-select '1' if available, otherwise first option
            default_id = 1 if 1 in ids else ids[0]
            self.id_dropdown.value = str(default_id)

            # Trigger load
            await self.on_id_selected(None)
        except (TypeError, ValueError, KeyError):
            if self._is_initialized:
                self._page.update()

    async def on_id_selected(self, e):
        try:
            state = self._parse_dropdown_state()
            size_val = state["size"]
            diff = state["difficulty"]
            id_val_str = state["id"]

            if not size_val or not diff or not id_val_str:
                return
            size = int(size_val)
            id_val = int(id_val_str)

            if (
                size in self._test_inputs_data
                and diff in self._test_inputs_data[size]
                and id_val in self._test_inputs_data[size][diff]
            ):
                rel_path = self._test_inputs_data[size][diff][id_val]
                self.load_puzzle(rel_path)

            if self._is_initialized:
                self._page.update()
        except (TypeError, ValueError, KeyError):
            if self._is_initialized:
                self._page.update()

    async def refresh_puzzle(self, e):
        # Stop any running animation and reset state
        if self.step_player.is_running() or self.step_player.is_paused():
            await self.step_player.stop()
        
        # Reset UI elements
        self.play_button.icon = ft.Icons.PAUSE
        self.status.value = ""
        
        # Reload the puzzle
        await self.on_id_selected(None)

    async def _auto_start_animation(self):
        """Auto-start animation after page initialization"""
        # Wait for cascade to complete puzzle loading
        # Try with increasing delays if puzzle not loaded yet
        for attempt in range(10):  # Try up to 10 times with 0.1s each = 1 second total
            if self._is_initialized and self.grid:
                await self.step_player.start_auto(delay=self.speed_slider.value)
                self.play_button.icon = ft.Icons.PAUSE
                self._update_solve_instantly_button_state()
                self._page.update()
                return
            await asyncio.sleep(0.1)

    async def on_file_selected(self, e):
        self.load_puzzle(e.control.value)
        self._page.update()

    def load_puzzle(self, path):
        if not path:
            return
        # If it's just a filename, assume it's in the default test/input dir
        if "/" not in path and "\\" not in path:
            filepath = os.path.join(base_dir, "test", "input", path)
        else:
            filepath = os.path.join(base_dir, path)

        try:
            self.size, self.grid, (self.h_constraints, self.v_constraints) = read_input(
                filepath
            )
            self._original_grid = [row[:] for row in self.grid]
            self._render_board()
        except Exception as e:
            self.status.value = f"Error: {e}"
            self.status.color = Win7Theme.ERROR

    def build_empty_board(self):
        n = self.size
        self.grid = [[0 for _ in range(n)] for _ in range(n)]
        self.h_constraints = [[0 for _ in range(n - 1)] for _ in range(n)]
        self.v_constraints = [[0 for _ in range(n)] for _ in range(n - 1)]
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
                    content=ft.Text(
                        str(val) if is_fixed else "",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=Win7Theme.CELL_TEXT_FIXED
                        if is_fixed
                        else Win7Theme.CELL_TEXT_EMPTY,
                    ),
                    alignment=ft.Alignment(0, 0),
                    width=55,
                    height=55,
                    bgcolor=Win7Theme.CELL_FIXED_BG
                    if is_fixed
                    else Win7Theme.CELL_EMPTY_BG,
                    border_radius=4,
                    border=ft.border.all(1, Win7Theme.PANEL_BG),
                    animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT_QUART),
                    animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                )
                row_controls.append(cell_container)
                row_cells.append(cell_container)
                if c < n - 1:
                    h_val = self.h_constraints[r][c]
                    txt = "<" if h_val == 1 else ">" if h_val == -1 else ""
                    row_controls.append(
                        ft.Container(
                            content=ft.Text(
                                txt,
                                size=18,
                                color=Win7Theme.CONSTRAINT,
                                weight=ft.FontWeight.BOLD,
                            ),
                            alignment=ft.Alignment(0, 0),
                            width=25,
                        )
                    )
            self.cells.append(row_cells)
            board_rows.append(
                ft.Row(
                    controls=row_controls,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                )
            )
            if r < n - 1:
                v_controls = []
                for c in range(n):
                    v_val = self.v_constraints[r][c]
                    txt = "^" if v_val == 1 else "v" if v_val == -1 else ""
                    v_controls.append(
                        ft.Container(
                            content=ft.Text(
                                txt,
                                size=18,
                                color=Win7Theme.CONSTRAINT,
                                weight=ft.FontWeight.BOLD,
                            ),
                            alignment=ft.Alignment(0, 0),
                            width=55,
                        )
                    )
                    if c < n - 1:
                        v_controls.append(ft.Container(width=25))
                board_rows.append(
                    ft.Row(
                        controls=v_controls,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5,
                    )
                )

        self.board_container.content = ft.Column(
            controls=board_rows,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )
        if self.step_player.is_running():
            asyncio.create_task(self.step_player.stop())
        if self._is_initialized:
            self._page.update()

    async def on_compute_solution(self, e):
        # Reset solution tracking state
        self._solution_ready = False
        self._final_solution = None
        
        async def callback(solution, stats, steps=None):
            # Store the final solution when solver finishes
            self._final_solution = solution
            self._solution_ready = True
            
            # Check if solution is incomplete (hit node limit)
            is_incomplete = stats.get('incomplete', False)
            hit_limit = stats.get('hit_limit', False)
            max_nodes = int(self.max_nodes_field.value) if not self.unlimited_nodes_checkbox.value else None
            
            if solution is None or is_incomplete:
                if hit_limit and max_nodes:
                    self.status.value = f"Max node limit reached ({stats.get('nodes_expanded', 0)} nodes)"
                else:
                    self.status.value = "No solution found"
                self.status.color = Win7Theme.ERROR
            else:
                self.status.value = (
                    f"Demo Finished. {stats.get('nodes_generated', '?')} nodes."
                )
                self.status.color = Win7Theme.SUCCESS
                
                # Update board with final solution
                for r in range(self.size):
                    for c in range(self.size):
                        if self._original_grid[r][c] == 0:
                            self.cells[r][c].content.value = str(solution[r][c])
                            self.cells[r][c].bgcolor = Win7Theme.SUCCESS
                            self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
            
            # Update button state now that solution is ready
            self._update_solve_instantly_button_state()
            self._page.update()

        self.status.value = "Demonstrating..."
        self.status.color = Win7Theme.PRIMARY
        self._page.update()

        # Reset board visuals
        for r in range(self.size):
            for c in range(self.size):
                val = self._original_grid[r][c]
                self.cells[r][c].content.value = str(val) if val != 0 else ""
                self.cells[r][c].bgcolor = (
                    Win7Theme.CELL_FIXED_BG if val != 0 else Win7Theme.CELL_EMPTY_BG
                )
        self._page.update()

        self._last_grid = [row[:] for row in self._original_grid]

        async def event_callback(action, r_or_grid, c_or_nodes=None, val_or_none=None):
            if action == "step" and isinstance(r_or_grid, list):
                grid = r_or_grid
                for r in range(self.size):
                    for c in range(self.size):
                        if grid[r][c] != self._last_grid[r][c] and grid[r][c] != 0:
                            self.cells[r][c].content.value = str(grid[r][c])
                            self.cells[r][c].bgcolor = Win7Theme.SUCCESS
                            self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
                        elif grid[r][c] == 0 and self._last_grid[r][c] != 0:
                            self.cells[r][c].content.value = ""
                            self.cells[r][c].bgcolor = Win7Theme.CELL_EMPTY_BG
                self._last_grid = [row[:] for row in grid]
                self._page.update()
            elif action == "check":
                r, c = r_or_grid, c_or_nodes
                self.cells[r][c].bgcolor = Win7Theme.CHECK
                self._page.update()
            elif action == "assign":
                r, c, val = r_or_grid, c_or_nodes, val_or_none
                self.cells[r][c].content.value = str(val)
                self.cells[r][c].bgcolor = Win7Theme.SUCCESS
                self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
                self.cells[r][c].scale = 1.1
                await asyncio.sleep(0.05)
                self.cells[r][c].scale = 1.0
                self._page.update()
            elif action == "backtrack":
                r, c = r_or_grid, c_or_nodes
                if self._original_grid[r][c] == 0:
                    self.cells[r][c].content.value = ""
                self.cells[r][c].bgcolor = Win7Theme.ERROR
                self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
                self._page.update()
            elif action == "expand":
                r, c = r_or_grid, c_or_nodes
                self.cells[r][c].bgcolor = Win7Theme.SKY_LIGHT
                self._page.update()
            elif action == "gen":
                r, c, val = r_or_grid, c_or_nodes, val_or_none
                self.cells[r][c].content.value = str(val)
                self.cells[r][c].bgcolor = Win7Theme.WARNING
                self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
                self._page.update()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                self.step_player.run_streaming(
                    event_callback, delay=self.speed_slider.value
                )
            )
            tg.create_task(
                self.solver.run_with_history(
                    self.size,
                    self._original_grid,
                    self.h_constraints,
                    self.v_constraints,
                    callback=callback,
                    algorithm=self.algorithm_dropdown.value,
                    step_player=self.step_player,
                    max_nodes=int(self.max_nodes_field.value) if not self.unlimited_nodes_checkbox.value else None,
                )
            )

    def _update_solve_instantly_button_state(self):
        """Enable Solve Instantly button always (can solve anytime)."""
        self.solve_instantly_button.disabled = False
        self.solve_instantly_button.tooltip = "Solve Instantly (No Delay)"

    async def on_play_pause(self, e):
        if not self.step_player.is_running():
            await self.step_player.start_auto(delay=self.speed_slider.value)
            self.play_button.icon = ft.Icons.PAUSE
        else:
            if self.step_player.is_paused():
                self.step_player.resume()
                self.play_button.icon = ft.Icons.PAUSE
            else:
                self.step_player.pause()
                self.play_button.icon = ft.Icons.PLAY_ARROW
        self._update_solve_instantly_button_state()
        self._page.update()

    async def on_manual_step(self, e):
        await self.step_player.step_once()
        self._page.update()

    async def on_speed_change(self, e):
        self.step_player._delay = float(self.speed_slider.value)

    async def on_unlimited_nodes_change(self, e):
        self.max_nodes_field.disabled = self.unlimited_nodes_checkbox.value
        self._page.update()

    async def on_solve_instantly(self, e):
        self.status.value = "Solving..."
        self.status.color = Win7Theme.PRIMARY
        self._page.update()

        async def on_result(solution, stats):
            if solution is None:
                self.status.value = "No solution found"
                self.status.color = Win7Theme.ERROR
            else:
                self.status.value = f"Solved: {stats.get('nodes_generated', '?')} nodes | {stats.get('time', 0):.3f}s"
                self.status.color = Win7Theme.SUCCESS
                for r in range(self.size):
                    for c in range(self.size):
                        if self._original_grid[r][c] == 0:
                            self.cells[r][c].content.value = str(solution[r][c])
                            self.cells[r][c].bgcolor = Win7Theme.SUCCESS
                            self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
            self._page.update()

        await self.solver.run_full(
            self.size,
            self._original_grid,
            self.h_constraints,
            self.v_constraints,
            callback=on_result,
            algorithm=self.algorithm_dropdown.value,
            max_nodes=int(self.max_nodes_field.value) if not self.unlimited_nodes_checkbox.value else None,
        )
