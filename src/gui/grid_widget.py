import flet as ft
from typing import List

# Nord Theme Palette
POLAR_NIGHT_1 = "#3B4252"
POLAR_NIGHT_2 = "#434C5E"
SNOW_STORM_2 = "#ECEFF4"
FROST_1 = "#88C0D0"
FROST_3 = "#5E81AC"

def render_grid(grid: List[List[int]], h_constraints: List[List[int]], v_constraints: List[List[int]]) -> ft.Control:
    """Return a Nord-themed flet control rendering the grid."""
    n = len(grid)
    board_rows = []

    for r in range(n):
        row_controls = []
        for c in range(n):
            val = grid[r][c]
            is_fixed = val != 0
            
            cell_container = ft.Container(
                content=ft.Text(str(val) if is_fixed else "", size=22, weight=ft.FontWeight.BOLD, color=SNOW_STORM_2 if is_fixed else FROST_1),
                width=55, height=55, bgcolor=POLAR_NIGHT_1 if is_fixed else POLAR_NIGHT_2,
                border_radius=8, alignment=ft.Alignment(0, 0)
            )
            row_controls.append(cell_container)
            if c < n - 1:
                h_val = h_constraints[r][c]
                sym = "<" if h_val == 1 else ">" if h_val == -1 else ""
                row_controls.append(ft.Container(content=ft.Text(sym, size=18, color=FROST_3, weight=ft.FontWeight.BOLD), width=25, alignment=ft.Alignment(0, 0)))
        
        board_rows.append(ft.Row(controls=row_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=5))
        if r < n - 1:
            v_controls = []
            for c in range(n):
                v_val = v_constraints[r][c] if r < len(v_constraints) else 0
                sym = "^" if v_val == 1 else "v" if v_val == -1 else ""
                v_controls.append(ft.Container(content=ft.Text(sym, size=18, color=FROST_3, weight=ft.FontWeight.BOLD), width=55, alignment=ft.Alignment(0, 0)))
                if c < n - 1:
                    v_controls.append(ft.Container(width=25))
            board_rows.append(ft.Row(controls=v_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=5))

    return ft.Column(controls=board_rows, alignment=ft.MainAxisAlignment.CENTER, spacing=5)
