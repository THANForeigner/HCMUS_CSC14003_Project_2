import flet as ft

# Windows 7 Aero-like Style Palette
WIN7_BLUE = "#3399FF"       # Sky Blue highlight
WIN7_BLUE_GLASS = "#A2C5E8" # Aero Glass Blue (soft sky)
WIN7_SKY_LIGHT = "#D9EBF9"  # Lighter Blue for backgrounds
WIN7_BG = "#F0F0F0"         # Main Light Background
WIN7_TEXT = "#1A1A1A"       # Primary Dark Text
WIN7_ACCENT = "#005696"     # Darker Blue accent
WIN7_WHITE = "#FFFFFF"      # Pure White
WIN7_GREY = "#E1E1E1"       # Subtle Grey
WIN7_DARK_BLUE = "#004578"  # Darker Blue for constraints
WIN7_SUCCESS = "#2E7D32"    # Green
WIN7_ERROR = "#C62828"      # Red
WIN7_WARNING = "#EF6C00"    # Orange
WIN7_HIGHLIGHT = "#FFFFE0"  # Light Yellow for "check"

class Win7Theme:
    # Main app background
    BG = WIN7_BG
    
    # Containers & Cards
    CARD_BG = WIN7_WHITE
    PANEL_BG = WIN7_BLUE_GLASS
    HEADER_BG = WIN7_SKY_LIGHT
    
    # Text
    TEXT_PRIMARY = WIN7_TEXT
    TEXT_SECONDARY = WIN7_ACCENT
    TEXT_INVERSE = WIN7_WHITE
    
    # Accents
    PRIMARY = WIN7_BLUE
    SECONDARY = WIN7_ACCENT
    
    # Grid / Puzzle Board
    CELL_FIXED_BG = WIN7_GREY
    CELL_EMPTY_BG = WIN7_WHITE
    CELL_TEXT_FIXED = WIN7_TEXT
    CELL_TEXT_EMPTY = WIN7_BLUE
    CONSTRAINT = WIN7_DARK_BLUE
    
    # Status / Actions
    SUCCESS = WIN7_SUCCESS
    ERROR = WIN7_ERROR
    WARNING = WIN7_WARNING
    CHECK = WIN7_HIGHLIGHT
    
    # Navigation / Buttons
    NAV_BG = WIN7_BLUE_GLASS
    BUTTON_BG = WIN7_BLUE
    BUTTON_TEXT = WIN7_WHITE
