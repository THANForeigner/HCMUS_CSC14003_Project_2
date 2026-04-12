import sys
import os
import flet as ft

# Ensure src directory is in path to allow imports anywhere
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.home_page import home_page
from gui.puzzle_page import PuzzlePage

def main(page: ft.Page):
    # Setup main window properties
    page.title = "Futoshiki - Artificial Bee Colony"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 900
    page.window_height = 800
    page.window_min_width = 700
    page.window_min_height = 600
    
    def route_change(route):
        page.views.clear()
        
        # Always add home page at the bottom of the stack
        page.views.append(home_page(page))
        
        if page.route == "/puzzle":
            # Add puzzle page on top
            page.views.append(PuzzlePage(page))
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.route = top_view.route
        page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Start app execution at root route
    route_change(None)

if __name__ == "__main__":
    ft.run(main)
