"""
Configuration settings for the Tic Tac Toe game using Pygame.
"""
# Pygame configuration
WINDOW_SIZE = (720, 480)
FPS = 60

# Grid configuration
GRID_SIZE = 3
CELL_SIZE = WINDOW_SIZE[1] // GRID_SIZE
LINE_WIDTH = 3

# Marker size
MARKER_SIZE = CELL_SIZE // 2

# Font size for text rendering
FONT_SIZE = CELL_SIZE // 3

# Color definitions
BACKGROUND_RGB = (0, 0, 0)
LINES_COLOUR = (255, 95, 31)
MARKERS_RGB = (255, 255, 255)
TEXT_RGB = (255, 255, 255)

# Winning combinations for Tic Tac Toe
WINNING_COMBINATIONS = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]
