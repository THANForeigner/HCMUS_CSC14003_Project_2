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
        
        # Build layout
        self.controls = [
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(content=ft.Text("< Back"), on_click=lambda _: page.go("/")),
                    ft.Text("Select Puzzle:", size=16, weight=ft.FontWeight.BOLD),
                    self.file_dropdown,
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