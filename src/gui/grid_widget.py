import flet as ft
from typing import List
from gui.theme import Win7Theme

def render_grid(grid: List[List[int]], h_constraints: List[List[int]], v_constraints: List[List[int]]) -> ft.Control:
    n = len(grid)
    board_rows = []

    for r in range(n):
        row_controls = []
        for c in range(n):
            val = grid[r][c]
            is_fixed = val != 0
            
            cell_container = ft.Container(
                content=ft.Text(str(val) if is_fixed else "", size=22, weight=ft.FontWeight.BOLD, color=Win7Theme.CELL_TEXT_FIXED if is_fixed else Win7Theme.CELL_TEXT_EMPTY),
                width=55, height=55, bgcolor=Win7Theme.CELL_FIXED_BG if is_fixed else Win7Theme.CELL_EMPTY_BG,
                border_radius=4, alignment=ft.Alignment(0, 0),
                border=ft.border.all(1, Win7Theme.PANEL_BG)
            )
            row_controls.append(cell_container)
            if c < n - 1:
                h_val = h_constraints[r][c]
                sym = "<" if h_val == 1 else ">" if h_val == -1 else ""
                row_controls.append(ft.Container(content=ft.Text(sym, size=18, color=Win7Theme.CONSTRAINT, weight=ft.FontWeight.BOLD), width=25, alignment=ft.Alignment(0, 0)))
        
        board_rows.append(ft.Row(controls=row_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=5))
        if r < n - 1:
            v_controls = []
            for c in range(n):
                v_val = v_constraints[r][c] if r < len(v_constraints) else 0
                sym = "^" if v_val == 1 else "v" if v_val == -1 else ""
                v_controls.append(ft.Container(content=ft.Text(sym, size=18, color=Win7Theme.CONSTRAINT, weight=ft.FontWeight.BOLD), width=55, alignment=ft.Alignment(0, 0)))
                if c < n - 1:
                    v_controls.append(ft.Container(width=25))
            board_rows.append(ft.Row(controls=v_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=5))

    return ft.Column(controls=board_rows, alignment=ft.MainAxisAlignment.CENTER, spacing=5)
