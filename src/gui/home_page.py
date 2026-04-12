import flet as ft

def home_page(page: ft.Page):
    return ft.View(
        "/",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "FUTOSHIKI",
                            size=64,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_400
                        ),
                        ft.Text(
                            "A Constraint Satisfaction Puzzle",
                            size=18,
                            color=ft.Colors.GREY_400
                        ),
                        ft.Container(height=50),
                        ft.ElevatedButton(
                            text="🧩 Puzzle Solving Mode",
                            icon="extension",
                            width=350,
                            height=60,
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.GREEN_700,
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                            on_click=lambda _: page.go("/puzzle")
                        ),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            text="🤖 Algorithm Demonstration",
                            icon="smart_toy",
                            width=350,
                            height=60,
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.PURPLE_700,
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                            on_click=lambda _: print("Demo Mode coming soon...")
                        ),
                        ft.Container(height=100),
                        ft.Text(
                            "Artificial Bee Colony Optimization",
                            size=12,
                            color=ft.Colors.GREY_500
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
