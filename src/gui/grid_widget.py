import flet as ft
from typing import List


def render_grid(grid: List[List[int]], h_constraints: List[List[int]], v_constraints: List[List[int]]) -> ft.Control:
    """Return a simple flet control rendering the grid as a column of rows.

    This helper is a lightweight alternative to the existing build_board
    implementation and may be used by future refactors.
    """
    n = len(grid)
    board_rows = []

    for r in range(n):
        row_controls = []
        for c in range(n):
            val = grid[r][c]
            txt = str(val) if val != 0 else ""
            tf = ft.TextField(
                value=txt,
                width=60,
                height=60,
                text_align=ft.TextAlign.CENTER,
                text_size=24,
                read_only=True,
                bgcolor=ft.Colors.BLUE_900 if val != 0 else ft.Colors.GREY_900,
                border_color=ft.Colors.BLUE_700 if val != 0 else ft.Colors.GREY_700,
                color=ft.Colors.WHITE if val != 0 else ft.Colors.CYAN_300,
            )
            row_controls.append(tf)
            if c < n - 1:
                h_val = h_constraints[r][c]
                sym = ""
                if h_val == 1:
                    sym = "<"
                elif h_val == -1:
                    sym = ">"
                row_controls.append(ft.Container(content=ft.Text(sym, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400), width=30, alignment=ft.Alignment(0,0)))
        board_rows.append(ft.Row(controls=row_controls, alignment=ft.MainAxisAlignment.CENTER))
        if r < n - 1:
            v_controls = []
            for c in range(n):
                v_val = v_constraints[r][c] if r < len(v_constraints) else 0
                sym = ""
                if v_val == 1:
                    sym = "^"
                elif v_val == -1:
                    sym = "v"
                v_controls.append(ft.Container(content=ft.Text(sym, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400), width=60, alignment=ft.Alignment(0,0)))
                if c < n - 1:
                    v_controls.append(ft.Container(width=30))
            board_rows.append(ft.Row(controls=v_controls, alignment=ft.MainAxisAlignment.CENTER))

    return ft.Column(controls=board_rows, alignment=ft.MainAxisAlignment.CENTER)
