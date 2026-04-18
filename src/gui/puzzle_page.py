import os
import flet as ft
import sys
import asyncio

# Ensure src directory is in path to allow imports
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, base_dir)

try:
    from src.io_handler import read_input, get_test_inputs, get_input_filename
except ImportError:
    from io_handler import read_input, get_test_inputs, get_input_filename

try:
    from src.gui.puzzle_manager import PuzzleManager
except ImportError:
    from gui.puzzle_manager import PuzzleManager

from src.gui.theme import Win7Theme


class PuzzlePage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/puzzle", bgcolor=Win7Theme.BG, scroll=ft.ScrollMode.AUTO
        )
        self._page = page
        self._is_initialized = False
        self.size = 0
        self.grid_data = []
        self.h_constraints = []
        self.v_constraints = []
        self.cells = []
        self._test_inputs_data = {}

        # UI Elements
        self.status_text = ft.Text(
            "", size=18, weight=ft.FontWeight.BOLD, color=Win7Theme.TEXT_PRIMARY
        )
        self.board_container = ft.Container(padding=20, expand=True)
        self.numpad_container = ft.Container(
            content=ft.Text(
                "Select a cell", color=Win7Theme.TEXT_SECONDARY, italic=True
            ),
            width=200,
            padding=20,
            alignment=ft.Alignment(0, 0),
        )

        # Cascading Dropdowns with enhanced design
        self.size_dropdown = ft.Dropdown(
            label="Size",
            width=100,
            label_style=ft.TextStyle(
                size=12, color=Win7Theme.TEXT_SECONDARY, weight=ft.FontWeight.BOLD
            ),
            text_style=ft.TextStyle(
                size=13, color=Win7Theme.TEXT_PRIMARY, weight=ft.FontWeight.W_500
            ),
            bgcolor=Win7Theme.CARD_BG,
            color=Win7Theme.TEXT_PRIMARY,
            border_color=Win7Theme.PANEL_BG,
            focused_border_color=Win7Theme.PRIMARY,
            border_radius=6,
        )
        self.size_dropdown.on_change = self.on_size_selected

        self.diff_dropdown = ft.Dropdown(
            label="Difficulty",
            width=120,
            label_style=ft.TextStyle(
                size=12, color=Win7Theme.TEXT_SECONDARY, weight=ft.FontWeight.BOLD
            ),
            text_style=ft.TextStyle(
                size=13, color=Win7Theme.TEXT_PRIMARY, weight=ft.FontWeight.W_500
            ),
            bgcolor=Win7Theme.CARD_BG,
            color=Win7Theme.TEXT_PRIMARY,
            border_color=Win7Theme.PANEL_BG,
            focused_border_color=Win7Theme.PRIMARY,
            border_radius=6,
        )
        self.diff_dropdown.on_change = self.on_diff_selected

        self.id_dropdown = ft.Dropdown(
            label="Puzzle ID",
            width=110,
            label_style=ft.TextStyle(
                size=12, color=Win7Theme.TEXT_SECONDARY, weight=ft.FontWeight.BOLD
            ),
            text_style=ft.TextStyle(
                size=13, color=Win7Theme.TEXT_PRIMARY, weight=ft.FontWeight.W_500
            ),
            bgcolor=Win7Theme.CARD_BG,
            color=Win7Theme.TEXT_PRIMARY,
            border_color=Win7Theme.PANEL_BG,
            focused_border_color=Win7Theme.PRIMARY,
            border_radius=6,
        )
        self.id_dropdown.on_change = self.on_id_selected

        self.load_available_files()

        self.algorithm_dropdown = ft.Dropdown(
            width=210,
            label_style=ft.TextStyle(
                size=12, color=Win7Theme.TEXT_SECONDARY, weight=ft.FontWeight.BOLD
            ),
            text_style=ft.TextStyle(
                size=13, color=Win7Theme.TEXT_PRIMARY, weight=ft.FontWeight.W_500
            ),
            value="astar_ac3",
            options=[
                ft.dropdown.Option("astar_ac3", text="A* + AC-3"),
                ft.dropdown.Option("backward_chaining_with_ac3", text="Backward Chaining + AC-3"),
            ],
            bgcolor=Win7Theme.CARD_BG,
            color=Win7Theme.TEXT_PRIMARY,
            border_color=Win7Theme.PANEL_BG,
            focused_border_color=Win7Theme.PRIMARY,
            border_radius=6,
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
            width=120,
            on_change=self.on_speed_change,
            active_color=Win7Theme.PRIMARY,
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

        # Control panel with improved dropdown styling
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_BACK,
                                    on_click=lambda _: page.go("/"),
                                    icon_color=Win7Theme.TEXT_PRIMARY,
                                ),
                                ft.VerticalDivider(width=1, color=Win7Theme.PANEL_BG),
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.Text(
                                                "Test Input:",
                                                size=14,
                                                color=Win7Theme.TEXT_SECONDARY,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            self.size_dropdown,
                                            self.diff_dropdown,
                                            self.id_dropdown,
                                            ft.ElevatedButton(
                                                content=ft.Text("Upload Test"),
                                                on_click=self.hard_refresh_page,
                                                style=ft.ButtonStyle(
                                                    bgcolor=Win7Theme.PRIMARY,
                                                    color=Win7Theme.TEXT_INVERSE,
                                                ),
                                            ),
                                        ],
                                        spacing=8,
                                        alignment=ft.MainAxisAlignment.START,
                                    ),
                                    padding=ft.padding.symmetric(horizontal=5),
                                ),
                                ft.VerticalDivider(width=1, color=Win7Theme.PANEL_BG),
                                ft.Text(
                                    "Algo:",
                                    size=14,
                                    color=Win7Theme.TEXT_SECONDARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                self.algorithm_dropdown,
                                ft.VerticalDivider(width=1, color=Win7Theme.PANEL_BG),
                                ft.ElevatedButton(
                                    content=ft.Text("Solve"),
                                    on_click=self.solve_puzzle,
                                    style=ft.ButtonStyle(
                                        bgcolor=Win7Theme.PRIMARY,
                                        color=Win7Theme.TEXT_INVERSE,
                                    ),
                                ),
                                ft.VerticalDivider(width=1, color=Win7Theme.PANEL_BG),
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
                                ft.Container(expand=True),
                                ft.TextButton(
                                    "Clear",
                                    on_click=self.clear_board,
                                    style=ft.ButtonStyle(color=Win7Theme.ERROR),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=5,
                        ),
                        ft.Row(
                            [
                                ft.Text("Speed", size=12, color=Win7Theme.TEXT_PRIMARY),
                                self.speed_slider,
                                ft.Container(expand=True),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=5,
                        ),
                    ],
                    spacing=5,
                ),
                padding=15,
                bgcolor=Win7Theme.HEADER_BG,
                border_radius=10,
                border=ft.border.all(1, Win7Theme.PANEL_BG),
                margin=ft.margin.only(left=20, right=20, top=10),
            ),
            ft.Row(
                [
                    self.board_container,
                    ft.VerticalDivider(width=1, color=Win7Theme.PANEL_BG),
                    self.numpad_container,
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(
                content=ft.Row(
                    [
                        ft.ElevatedButton(
                            content=ft.Text(
                                "Check Solution", weight=ft.FontWeight.BOLD
                            ),
                            on_click=self.check_win,
                            style=ft.ButtonStyle(
                                bgcolor=Win7Theme.SUCCESS,
                                color=Win7Theme.TEXT_INVERSE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            height=45,
                            width=180,
                        ),
                        ft.Container(width=20),
                        self.status_text,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=25,
            ),
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
        self._solution_ready = False
        self._solving = False
        self._original_grid = None
        self._active_cell = None  # (r, c)
        self._bottom_sheet = None
        self.cell_colors = []  # To store colors for hover restoration

        if self.size_dropdown.options:
            self.size_dropdown.value = "4"
            asyncio.create_task(self.on_size_selected(None))

        self._is_initialized = True

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
            # Stop any running solver/step_player
            if self.step_player.is_running() or self.step_player.is_paused():
                await self.step_player.stop()
            
            # Reset UI elements and state
            self.play_button.icon = ft.Icons.PLAY_ARROW
            self.status_text.value = ""
            self._active_cell = None
            self.numpad_container.content = ft.Text(
                "Select a cell", color=Win7Theme.TEXT_SECONDARY, italic=True
            )
            
            # Explicitly reset size before loading new puzzle
            self.size = 0
            
            # Reload the puzzle
            await self.on_id_selected(None)
            
            # Verify size was properly updated
            if self.size == 0:
                self.status_text.value = "Error: Failed to load puzzle"
                self.status_text.color = Win7Theme.ERROR
            else:
                self.status_text.value = "Page refreshed"
                self.status_text.color = Win7Theme.SUCCESS
        else:
            self.status_text.value = "Please select Size, Difficulty, and ID"
            self.status_text.color = Win7Theme.ERROR
        self._page.update()

    async def on_size_selected(self, e):
        try:
            state = self._parse_dropdown_state()
            size_val = state["size"]
            if not size_val:
                return
            size = int(size_val)

            # Get available difficulties for this size
            diffs = self._sort_difficulties(self._test_inputs_data[size].keys())
            self.diff_dropdown.options = [ft.dropdown.Option(d) for d in diffs]

            # Auto-select 'trivial' if available, otherwise first option
            default_diff = "trivial" if "trivial" in diffs else diffs[0]
            self.diff_dropdown.value = default_diff

            # Trigger next cascade
            await self.on_diff_selected(None)
            if self._is_initialized:
                self.page.update()
        except (TypeError, ValueError, KeyError):
            self.diff_dropdown.options = []
            self.id_dropdown.options = []
            if self._is_initialized:
                self.page.update()

    async def on_diff_selected(self, e):
        try:
            state = self._parse_dropdown_state()
            size_val = state["size"]
            diff = state["difficulty"]
            if not size_val or not diff:
                return
            size = int(size_val)

            # Get available IDs for this size and difficulty
            ids = sorted(self._test_inputs_data[size][diff].keys())
            self.id_dropdown.options = [ft.dropdown.Option(str(i)) for i in ids]

            # Auto-select '1' if available, otherwise first option
            default_id = 1 if 1 in ids else ids[0]
            self.id_dropdown.value = str(default_id)

            # Trigger load
            await self.on_id_selected(None)
            if self._is_initialized:
                self.page.update()
        except (TypeError, ValueError, KeyError):
            self.id_dropdown.options = []
            if self._is_initialized:
                self.page.update()

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

            # Verify the combination exists in the data
            if (
                size in self._test_inputs_data
                and diff in self._test_inputs_data[size]
                and id_val in self._test_inputs_data[size][diff]
            ):
                rel_path = self._test_inputs_data[size][diff][id_val]
                self.load_puzzle(rel_path)

            if self._is_initialized:
                self.page.update()
        except (TypeError, ValueError, KeyError):
            if self._is_initialized:
                self.page.update()

    async def generate_solved(self, e):
        try:
            size = self.size if self.size >= 2 else 5
            pm = PuzzleManager()
            grid, h_constraints, v_constraints = pm.generate_solved(size)
            self.size, self.grid_data, self.h_constraints, self.v_constraints = (
                size,
                grid,
                h_constraints,
                v_constraints,
            )
            self._original_grid = [row[:] for row in grid]
            self.build_board()
            self.status_text.value = "Generated solved puzzle"
            self.status_text.color = Win7Theme.SUCCESS
        except Exception as ex:
            self.status_text.value = f"Generate failed: {ex}"
            self.status_text.color = Win7Theme.ERROR
        self.page.update()

    async def clear_board(self, e):
        for r in range(self.size):
            for c in range(self.size):
                if self.grid_data[r][c] == 0:
                    self.cells[r][c].content.value = ""
                    self.cells[r][c].bgcolor = Win7Theme.CELL_EMPTY_BG
        self.validate_board()

    def load_puzzle(self, path):
        if not path:
            return

        # Normalize path separators for the current OS
        normalized_path = os.path.normpath(path)

        if "test" in normalized_path and "input" in normalized_path:
            filepath = os.path.join(base_dir, normalized_path)
        else:
            filepath = os.path.join(base_dir, "test", "input", normalized_path)

        try:
            self.size, self.grid_data, (self.h_constraints, self.v_constraints) = (
                read_input(filepath)
            )
            self._original_grid = [row[:] for row in self.grid_data]
            # Reset active cell and numpad when loading new puzzle
            self._active_cell = None
            self.numpad_container.content = ft.Text(
                "Select a cell", color=Win7Theme.TEXT_SECONDARY, italic=True
            )
            self.build_board()
            if self._is_initialized:
                self.page.update()
        except Exception as e:
            print(f"Error loading puzzle from {filepath}: {e}")
            self.status_text.value = f"Load error: {e}"
            self.status_text.color = Win7Theme.ERROR
            if self._is_initialized:
                self.page.update()

    def build_board(self):
        self.cells = []
        self.cell_colors = [
            [Win7Theme.CELL_EMPTY_BG for _ in range(self.size)]
            for _ in range(self.size)
        ]
        board_rows = []
        for r in range(self.size):
            row_controls = []
            row_cells = []
            for c in range(self.size):
                val = self.grid_data[r][c]
                is_fixed = val != 0

                initial_bg = (
                    Win7Theme.CELL_FIXED_BG if is_fixed else Win7Theme.CELL_EMPTY_BG
                )
                self.cell_colors[r][c] = initial_bg

                cell_content = ft.Text(
                    value=str(val) if is_fixed else "",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=Win7Theme.CELL_TEXT_FIXED
                    if is_fixed
                    else Win7Theme.CELL_TEXT_EMPTY,
                )

                cell_container = ft.Container(
                    content=cell_content,
                    alignment=ft.alignment.Alignment(0, 0),
                    width=55,
                    height=55,
                    bgcolor=initial_bg,
                    border_radius=4,
                    border=ft.border.all(1, Win7Theme.PANEL_BG),
                    data=(r, c),
                    on_click=self._handle_cell_click,
                    on_hover=lambda e, row=r, col=c: self.on_cell_hover(e, row, col),
                    animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT_QUART),
                    animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                )

                row_controls.append(cell_container)
                row_cells.append(cell_container)

                if c < self.size - 1:
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
                            alignment=ft.alignment.Alignment(0, 0),
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

            if r < self.size - 1:
                v_controls = []
                for c in range(self.size):
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
                            alignment=ft.alignment.Alignment(0, 0),
                            width=55,
                        )
                    )
                    if c < self.size - 1:
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
        self.validate_board()

    def on_cell_hover(self, e, r, c):
        # Highlight row and column
        is_hover = e.data == "true"
        target_color = Win7Theme.SKY_LIGHT if is_hover else None

        for i in range(self.size):
            if i != c:
                cell = self.cells[r][i]
                if not target_color:
                    cell.bgcolor = self.cell_colors[r][i]
                else:
                    cell.bgcolor = target_color
            if i != r:
                cell = self.cells[i][c]
                if not target_color:
                    cell.bgcolor = self.cell_colors[i][c]
                else:
                    cell.bgcolor = target_color

        self.cells[r][c].scale = 1.1 if is_hover else 1.0
        self.page.update()

    async def _handle_cell_click(self, e):
        r, c = e.control.data
        await self.on_cell_click(r, c)

    async def on_cell_click(self, r, col_idx):
        if self.grid_data[r][col_idx] != 0:
            return  # Fixed

        self._active_cell = (r, col_idx)

        # Highlight active cell
        for row in self.cells:
            for cell in row:
                if cell.border:
                    cell.border = ft.border.all(1, Win7Theme.PANEL_BG)
        self.cells[r][col_idx].border = ft.border.all(2, Win7Theme.PRIMARY)

        # Build Side-panel numpad
        n = self.size
        buttons = []
        for i in range(1, n + 1):

            async def make_on_click(val):
                async def handler(e):
                    await self.on_numpad_select(val)

                return handler

            buttons.append(
                ft.ElevatedButton(
                    content=ft.Text(str(i)),
                    on_click=await make_on_click(i),
                    width=50,
                    height=50,
                    style=ft.ButtonStyle(
                        bgcolor=Win7Theme.CELL_EMPTY_BG,
                        color=Win7Theme.PRIMARY,
                        shape=ft.RoundedRectangleBorder(radius=4),
                        padding=0,
                    ),
                )
            )

        async def clear_handler(e):
            await self.on_numpad_select(0)

        buttons.append(
            ft.ElevatedButton(
                content=ft.Text("X"),
                on_click=clear_handler,
                width=50,
                height=50,
                style=ft.ButtonStyle(
                    bgcolor=Win7Theme.ERROR,
                    color=Win7Theme.TEXT_INVERSE,
                    shape=ft.RoundedRectangleBorder(radius=4),
                    padding=0,
                ),
            )
        )

        self.numpad_container.content = ft.Column(
            [
                ft.Text(
                    f"Cell ({r + 1},{col_idx + 1})",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=Win7Theme.TEXT_SECONDARY,
                ),
                ft.Container(height=10),
                ft.Row(
                    buttons,
                    wrap=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.page.update()

    async def on_numpad_select(self, val):
        if self._active_cell:
            r, c = self._active_cell
            self.cells[r][c].content.value = str(val) if val != 0 else ""
            # Ensure text color is visible - use primary text color for user-entered values
            self.cells[r][c].content.color = Win7Theme.TEXT_PRIMARY if val != 0 else Win7Theme.CELL_TEXT_EMPTY
            self.cells[r][c].border = ft.border.all(1, Win7Theme.PANEL_BG)
            self._active_cell = None

            # Reset numpad container
            self.numpad_container.content = ft.Text(
                "Select a cell", color=Win7Theme.TEXT_SECONDARY, italic=True
            )

            self.validate_board()
            self.page.update()

    def validate_board(self):
        current = [
            [
                int(self.cells[r][c].content.value)
                if self.cells[r][c].content.value
                else 0
                for c in range(self.size)
            ]
            for r in range(self.size)
        ]
        has_error = False
        # First pass: Reset all backgrounds and text colors to default states
        for r in range(self.size):
            for c in range(self.size):
                color = (
                    Win7Theme.CELL_FIXED_BG
                    if self.grid_data[r][c] != 0
                    else Win7Theme.CELL_EMPTY_BG
                )
                self.cells[r][c].bgcolor = color
                self.cell_colors[r][c] = color
                # Set text color based on whether cell has content
                val = current[r][c]
                if val != 0:
                    self.cells[r][c].content.color = Win7Theme.TEXT_PRIMARY
                else:
                    self.cells[r][c].content.color = Win7Theme.CELL_TEXT_EMPTY

        # Second pass: Check for conflicts and apply error/warning colors
        for r in range(self.size):
            for c in range(self.size):
                val = current[r][c]
                if val == 0:
                    continue
                if (
                    current[r].count(val) > 1
                    or [current[i][c] for i in range(self.size)].count(val) > 1
                ):
                    color = Win7Theme.ERROR
                    self.cells[r][c].bgcolor = color
                    self.cell_colors[r][c] = color
                    self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
                    has_error = True
                if c < self.size - 1:
                    h = self.h_constraints[r][c]
                    if (
                        h == 1
                        and current[r][c + 1] != 0
                        and not (val < current[r][c + 1])
                    ):
                        self.cells[r][c].bgcolor = self.cells[r][c + 1].bgcolor = (
                            Win7Theme.WARNING
                        )
                        self.cell_colors[r][c] = self.cell_colors[r][c + 1] = (
                            Win7Theme.WARNING
                        )
                        has_error = True
                    if (
                        h == -1
                        and current[r][c + 1] != 0
                        and not (val > current[r][c + 1])
                    ):
                        self.cells[r][c].bgcolor = self.cells[r][c + 1].bgcolor = (
                            Win7Theme.WARNING
                        )
                        self.cell_colors[r][c] = self.cell_colors[r][c + 1] = (
                            Win7Theme.WARNING
                        )
                        has_error = True
                if r < self.size - 1:
                    v = self.v_constraints[r][c]
                    if (
                        v == 1
                        and current[r + 1][c] != 0
                        and not (val < current[r + 1][c])
                    ):
                        self.cells[r][c].bgcolor = self.cells[r + 1][c].bgcolor = (
                            Win7Theme.WARNING
                        )
                        self.cell_colors[r][c] = self.cell_colors[r + 1][c] = (
                            Win7Theme.WARNING
                        )
                        has_error = True
                    if (
                        v == -1
                        and current[r + 1][c] != 0
                        and not (val > current[r + 1][c])
                    ):
                        self.cells[r][c].bgcolor = self.cells[r + 1][c].bgcolor = (
                            Win7Theme.WARNING
                        )
                        self.cell_colors[r][c] = self.cell_colors[r + 1][c] = (
                            Win7Theme.WARNING
                        )
                        has_error = True

        self.status_text.value = "Conflict detected" if has_error else ""
        self.status_text.color = Win7Theme.ERROR
        if self._is_initialized:
            self.page.update()

    async def check_win(self, e):
        self.validate_board()
        if self.status_text.value:
            return
        for r in range(self.size):
            for c in range(self.size):
                if not self.cells[r][c].content.value:
                    self.status_text.value = "Incomplete board"
                    self.status_text.color = Win7Theme.WARNING
                    self.page.update()
                    return
        self.status_text.value = "Perfect Solution!"
        self.status_text.color = Win7Theme.SUCCESS
        self.page.update()

    async def solve_puzzle(self, e):
        self._solving = True
        self._solution_ready = False
        self._solution = None
        
        async def on_result(solution, stats, steps=None):
            self._solving = False
            self._solution = solution
            self._solution_ready = solution is not None
            
            expanded = stats.get('nodes_expanded', 0)
            max_nodes = int(self.max_nodes_field.value) if not self.unlimited_nodes_checkbox.value else None
            
            if solution is None:
                if max_nodes is not None and expanded >= max_nodes:
                    self.status_text.value = f"Max node limit reached ({expanded} nodes)"
                else:
                    self.status_text.value = "No solution found"
                self.status_text.color = Win7Theme.ERROR
            else:
                self.status_text.value = f"Solved: {stats.get('nodes_generated', '?')} nodes | {stats.get('time', 0):.3f}s"
                self.status_text.color = Win7Theme.SUCCESS
                for r in range(self.size):
                    for c in range(self.size):
                        if self._original_grid[r][c] == 0:
                            self.cells[r][c].content.value = str(solution[r][c])
                            self.cells[r][c].bgcolor = Win7Theme.SUCCESS
                            self.cell_colors[r][c] = Win7Theme.SUCCESS
            
            self.page.update()

        self.status_text.value = "Solving..."
        self.status_text.color = Win7Theme.PRIMARY
        self.page.update()

        self._last_grid = [row[:] for row in self._original_grid]

        async def event_callback(action, grid_or_r, c_or_val=None, val_or_none=None):
            if action == "step" and isinstance(grid_or_r, list):
                grid = grid_or_r
                for r in range(self.size):
                    for c in range(self.size):
                        if grid[r][c] != self._last_grid[r][c] and grid[r][c] != 0:
                            self.cells[r][c].content.value = str(grid[r][c])
                            self.cells[r][c].bgcolor = Win7Theme.SUCCESS
                            self.cell_colors[r][c] = Win7Theme.SUCCESS
                            self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
                        elif grid[r][c] == 0 and self._last_grid[r][c] != 0:
                            self.cells[r][c].content.value = ""
                            self.cells[r][c].bgcolor = Win7Theme.CELL_EMPTY_BG
                            self.cell_colors[r][c] = Win7Theme.CELL_EMPTY_BG
                self._last_grid = [row[:] for row in grid]
                self.page.update()
            elif action == "check":
                r, c, val = grid_or_r, c_or_val, val_or_none
                self.cells[r][c].bgcolor = Win7Theme.CHECK
                # Don't save CHECK to cell_colors as it's transient
                self.page.update()
            elif action == "assign":
                r, c, val = grid_or_r, c_or_val, val_or_none
                self.cells[r][c].content.value = str(val)
                self.cells[r][c].bgcolor = Win7Theme.SUCCESS
                self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
                self.cells[r][c].scale = 1.1
                self.cell_colors[r][c] = Win7Theme.SUCCESS
                await asyncio.sleep(0.05)
                self.cells[r][c].scale = 1.0
                self.page.update()
            elif action == "backtrack":
                r, c, val = grid_or_r, c_or_val, val_or_none
                if self._original_grid[r][c] == 0:
                    self.cells[r][c].content.value = ""
                self.cells[r][c].bgcolor = Win7Theme.ERROR
                self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
                self.cell_colors[r][c] = Win7Theme.ERROR
                self.page.update()
            elif action == "expand":
                r, c = grid_or_r, c_or_val
                self.cells[r][c].bgcolor = Win7Theme.SKY_LIGHT
                # Transient, don't save to cell_colors
                self.page.update()
            elif action == "gen":
                r, c, val = grid_or_r, c_or_val, val_or_none
                self.cells[r][c].content.value = str(val)
                self.cells[r][c].bgcolor = Win7Theme.WARNING
                self.cells[r][c].content.color = Win7Theme.TEXT_INVERSE
                self.cell_colors[r][c] = Win7Theme.WARNING
                self.page.update()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                self.step_player.run_streaming(
                    event_callback, delay=self.speed_slider.value
                )
            )
            tg.create_task(
                self.solver.run_with_history(
                    self.size,
                    self.grid_data,
                    self.h_constraints,
                    self.v_constraints,
                    callback=on_result,
                    algorithm=self.algorithm_dropdown.value,
                    step_player=self.step_player,
                    max_nodes=int(self.max_nodes_field.value) if not self.unlimited_nodes_checkbox.value else None,
                )
            )

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
        self.page.update()

    async def on_manual_step(self, e):
        await self.step_player.step_once()
        self.page.update()

    async def on_solve_instantly(self, e):
        self.status_text.value = "Solving..."
        self.status_text.color = Win7Theme.PRIMARY
        self.page.update()

        async def on_result(solution, stats):
            if solution is None:
                self.status_text.value = "No solution found"
                self.status_text.color = Win7Theme.ERROR
            else:
                self.status_text.value = f"Solved: {stats.get('nodes_generated', '?')} nodes | {stats.get('time', 0):.3f}s"
                self.status_text.color = Win7Theme.SUCCESS
                for r in range(self.size):
                    for c in range(self.size):
                        if self._original_grid[r][c] == 0:
                            self.cells[r][c].content.value = str(solution[r][c])
                            self.cells[r][c].bgcolor = Win7Theme.SUCCESS
                            self.cell_colors[r][c] = Win7Theme.SUCCESS
            self.page.update()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                self.solver.run_full(
                    self.size,
                    self.grid_data,
                    self.h_constraints,
                    self.v_constraints,
                    callback=on_result,
                    algorithm=self.algorithm_dropdown.value,
                    max_nodes=int(self.max_nodes_field.value) if not self.unlimited_nodes_checkbox.value else None,
                )
            )

    async def on_speed_change(self, e):
        self.step_player._delay = float(self.speed_slider.value)

    async def on_unlimited_nodes_change(self, e):
        self.max_nodes_field.disabled = self.unlimited_nodes_checkbox.value
        self.page.update()
