import customtkinter as ctk

class HomePage(ctk.CTkFrame):
    def __init__(self, master, start_puzzle_callback, start_demo_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.start_puzzle_callback = start_puzzle_callback
        self.start_demo_callback = start_demo_callback
        
        # Configure layout
        self.grid_rowconfigure(0, weight=1) # Top spacer
        self.grid_rowconfigure(1, weight=0) # Title
        self.grid_rowconfigure(2, weight=0) # Subtitle
        self.grid_rowconfigure(3, weight=0) # Buttons frame
        self.grid_rowconfigure(4, weight=1) # Bottom spacer
        self.grid_columnconfigure(0, weight=1)
        
        # Title Section
        self.title_label = ctk.CTkLabel(
            self, 
            text="FUTOSHIKI", 
            font=ctk.CTkFont(family="Inter", size=64, weight="bold"),
            text_color=("#1f538d", "#3a7ebf") # Modern blue tint
        )
        self.title_label.grid(row=1, column=0, pady=(0, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self,
            text="A Constraint Satisfaction Puzzle",
            font=ctk.CTkFont(family="Inter", size=18),
            text_color=("gray60", "gray40")
        )
        self.subtitle_label.grid(row=2, column=0, pady=(0, 50))
        
        # Action Buttons Frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=3, column=0, pady=20)
        
        # Mode 1: Puzzle Solving
        self.btn_puzzle = ctk.CTkButton(
            self.button_frame,
            text="🧩 Puzzle Solving Mode",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            width=350,
            corner_radius=12,
            fg_color="#2b8a3e",
            hover_color="#21662d",
            command=self._on_puzzle_click
        )
        self.btn_puzzle.pack(pady=15)
        
        # Mode 2: Algorithm Demo
        self.btn_demo = ctk.CTkButton(
            self.button_frame,
            text="🤖 Algorithm Demonstration",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            width=350,
            corner_radius=12,
            fg_color="#862e9c",
            hover_color="#5f206e",
            command=self._on_demo_click
        )
        self.btn_demo.pack(pady=15)
        
        # Bottom decorative footer
        self.footer_label = ctk.CTkLabel(
            self,
            text="Artificial Bee Colony Optimization",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=("gray70", "gray30")
        )
        self.footer_label.grid(row=4, column=0, sticky="s", pady=20)

    def _on_puzzle_click(self):
        print("Starting Puzzle Solving Mode...")
        if self.start_puzzle_callback:
            self.start_puzzle_callback()
            
    def _on_demo_click(self):
        print("Starting Algorithm Demonstration Mode...")
        if self.start_demo_callback:
            self.start_demo_callback()
