import flet as ft

# Nord Theme Palette
POLAR_NIGHT_0 = "#2E3440"
POLAR_NIGHT_1 = "#3B4252"
POLAR_NIGHT_3 = "#4C566A"
SNOW_STORM_0 = "#D8DEE9"
SNOW_STORM_2 = "#ECEFF4"
FROST_1 = "#88C0D0"
FROST_3 = "#5E81AC"
AURORA_GREEN = "#A3BE8C"
AURORA_PURPLE = "#B48EAD"

def home_page(page: ft.Page):
    return ft.View(
        route="/",
        bgcolor=POLAR_NIGHT_0,
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "FUTOSHIKI",
                            size=72,
                            weight=ft.FontWeight.BOLD,
                            color=FROST_1,
                            italic=True
                        ),
                        ft.Text(
                            "The Minimalist Logic Puzzle",
                            size=20,
                            color=SNOW_STORM_0,
                        ),
                        ft.Container(height=60),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.GRID_ON, color=POLAR_NIGHT_0),
                                ft.Text("Puzzle Solver", size=18, weight=ft.FontWeight.BOLD)
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            width=320,
                            height=65,
                            style=ft.ButtonStyle(
                                color=POLAR_NIGHT_0,
                                bgcolor=AURORA_GREEN,
                                shape=ft.RoundedRectangleBorder(radius=15),
                            ),
                            on_click=lambda _: page.go("/puzzle")
                        ),
                        ft.Container(height=15),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.AUTO_AWESOME, color=POLAR_NIGHT_0),
                                ft.Text("Algorithm Demo", size=18, weight=ft.FontWeight.BOLD)
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            width=320,
                            height=65,
                            style=ft.ButtonStyle(
                                color=POLAR_NIGHT_0,
                                bgcolor=AURORA_PURPLE,
                                shape=ft.RoundedRectangleBorder(radius=15),
                            ),
                            on_click=lambda _: page.go("/demo")
                        ),
                        ft.Container(height=120),
                        ft.Text(
                            "Powered by Constraint Satisfaction Algorithms",
                            size=12,
                            color=POLAR_NIGHT_3
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.Alignment(0, 0),
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
