import sys
import os
import flet as ft

# Ensure repo root and src directory are in path to allow imports anywhere
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, src_dir)
sys.path.insert(0, repo_root)

from gui.home_page import home_page
from gui.puzzle_page import PuzzlePage
from gui.demo_page import DemoPage

def main(page: ft.Page):
    # Setup main window properties
    page.title = "Futoshiki"
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
        elif page.route == "/demo":
            page.views.append(DemoPage(page))
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
