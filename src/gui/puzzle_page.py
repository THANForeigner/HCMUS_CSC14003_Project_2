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
        self.page = page
        
        self.size = 0
        self.grid_data = []
        self.h_constraints = []
        self.v_constraints = []
        self.cells = []
        
        # UI Elements
        self.status_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD)
        self.board_container = ft.Container(alignment=ft.alignment.center)
        self.file_dropdown = ft.Dropdown(
            width=250,
            on_change=self.on_file_selected
        )
        self.load_available_files()
        
        # Build layout
        self.controls = [
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton("< Back", on_click=lambda _: page.go("/")),
                    ft.Text("Select Puzzle:", size=16, weight=ft.FontWeight.BOLD),
                    self.file_dropdown
                ], alignment=ft.MainAxisAlignment.START),
                padding=20
            ),
            ft.Container(
                content=self.board_container,
                expand=True,
                alignment=ft.alignment.center
            ),
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(
                        "Check Solution", 
                        on_click=self.check_solution,
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
                    max_length=2,
                    counter_text=" "
                )
                # Restrict input to digits
                tf.input_filter = ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
                
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
                            alignment=ft.alignment.center
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
                            alignment=ft.alignment.center
                        )
                    )
                    
                    if c < self.size - 1:
                        v_controls.append(ft.Container(width=30)) # Spacing for horizontal constraints
                        
                board_rows.append(ft.Row(controls=v_controls, alignment=ft.MainAxisAlignment.CENTER))
                
        self.board_container.content = ft.Column(controls=board_rows, alignment=ft.MainAxisAlignment.CENTER)

    def check_solution(self, e):
        current_grid = []
        for r in range(self.size):
            row_vals = []
            for c in range(self.size):
                val_str = self.cells[r][c].value.strip()
                if not val_str:
                    self.status_text.value = "Board is incomplete!"
                    self.status_text.color = ft.Colors.RED_400
                    self.page.update()
                    return
                val = int(val_str)
                if val < 1 or val > self.size:
                    self.status_text.value = f"Values must be 1-{self.size}!"
                    self.status_text.color = ft.Colors.RED_400
                    self.page.update()
                    return
                row_vals.append(val)
            current_grid.append(row_vals)
            
        for r in range(self.size):
            if len(set(current_grid[r])) != self.size:
                self.status_text.value = f"Duplicate in row {r+1}!"
                self.status_text.color = ft.Colors.RED_400
                self.page.update()
                return
                
        for c in range(self.size):
            col_vals = [current_grid[r][c] for r in range(self.size)]
            if len(set(col_vals)) != self.size:
                self.status_text.value = f"Duplicate in column {c+1}!"
                self.status_text.color = ft.Colors.RED_400
                self.page.update()
                return
                
        for r in range(self.size):
            for c in range(self.size - 1):
                h = self.h_constraints[r][c]
                if h == 1 and not (current_grid[r][c] < current_grid[r][c+1]):
                    self.status_text.value = f"Violated horizontal constraint at Row {r+1} Col {c+1}!"
                    self.status_text.color = ft.Colors.RED_400
                    self.page.update()
                    return
                if h == -1 and not (current_grid[r][c] > current_grid[r][c+1]):
                    self.status_text.value = f"Violated horizontal constraint at Row {r+1} Col {c+1}!"
                    self.status_text.color = ft.Colors.RED_400
                    self.page.update()
                    return
                    
        for r in range(self.size - 1):
            for c in range(self.size):
                v = self.v_constraints[r][c]
                if v == 1 and not (current_grid[r][c] < current_grid[r+1][c]):
                    self.status_text.value = f"Violated vertical constraint at Row {r+1} Col {c+1}!"
                    self.status_text.color = ft.Colors.RED_400
                    self.page.update()
                    return
                if v == -1 and not (current_grid[r][c] > current_grid[r+1][c]):
                    self.status_text.value = f"Violated vertical constraint at Row {r+1} Col {c+1}!"
                    self.status_text.color = ft.Colors.RED_400
                    self.page.update()
                    return
                    
        self.status_text.value = "Valid Solution! Excellent!"
        self.status_text.color = ft.Colors.GREEN_400
        self.page.update()
