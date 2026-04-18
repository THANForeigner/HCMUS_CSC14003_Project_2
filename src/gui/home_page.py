import flet as ft
from gui.theme import Win7Theme

def home_page(page: ft.Page):
    return ft.View(
        route="/",
        bgcolor=Win7Theme.BG,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "FUTOSHIKI",
                            size=72,
                            weight=ft.FontWeight.BOLD,
                            color=Win7Theme.PRIMARY,
                            italic=True
                        ),
                        ft.Text(
                            "Group - Doryouku",
                            size=20,
                            color=Win7Theme.TEXT_SECONDARY,
                        ),
                        ft.Container(height=60),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.GRID_ON, color=Win7Theme.TEXT_INVERSE),
                                ft.Text("Puzzle Solver", size=18, weight=ft.FontWeight.BOLD)
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            width=320,
                            height=65,
                            style=ft.ButtonStyle(
                                color=Win7Theme.TEXT_INVERSE,
                                bgcolor=Win7Theme.PRIMARY,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=lambda _: page.go("/puzzle")
                        ),
                        ft.Container(height=15),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.AUTO_AWESOME, color=Win7Theme.TEXT_INVERSE),
                                ft.Text("Algorithm Demo", size=18, weight=ft.FontWeight.BOLD)
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            width=320,
                            height=65,
                            style=ft.ButtonStyle(
                                color=Win7Theme.TEXT_INVERSE,
                                bgcolor=Win7Theme.SECONDARY,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=lambda _: page.go("/demo")
                        ),
                        ft.Container(height=120),
                        ft.Text(
                            "CSC14003: Introduction to Artificial Intelligence",
                            size=12,
                            color=Win7Theme.TEXT_SECONDARY
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
