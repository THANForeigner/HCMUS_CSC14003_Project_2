import os
import sys

# Ensure src directory is in path to allow imports anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from gui.home_page import HomePage

# Global setup for premium CustomTkinter look
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Setup main window
        self.title("Futoshiki - Artificial Bee Colony")
        self.geometry("800x600")
        self.minsize(600, 500)
        
        # Configure grid system for the root window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Container for screens/pages
        self.frames = {}
        
        # Initialize Home Page
        self._init_pages()
        
        # Show home page initially
        self.show_frame("HomePage")

    def _init_pages(self):
        # Home Page initialization
        home_page = HomePage(
            master=self,
            start_puzzle_callback=self.on_start_puzzle,
            start_demo_callback=self.on_start_demo
        )
        self.frames["HomePage"] = home_page
        
        # We grid the frame in the main window
        home_page.grid(row=0, column=0, sticky="nsew")
        
    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.grid_remove()
            
        # Show requested frame
        if frame_name in self.frames:
            self.frames[frame_name].grid(row=0, column=0, sticky="nsew")

    # Placeholder callbacks
    def on_start_puzzle(self):
        print("[App] User selected Puzzle Solving Mode.")
        # E.g., self.show_frame("PuzzlePage")
        
    def on_start_demo(self):
        print("[App] User selected Algorithm Demonstration Mode.")
        # E.g., self.show_frame("DemoPage")

if __name__ == "__main__":
    app = App()
    app.mainloop()
