"""
Event handler.
"""
import pygame

from tic_tac_toe_pygame.config import GRID_SIZE, CELL_SIZE


class EventHandler:
    """Class to handle Pygame events."""

    def __init__(self, screen, game_state):
        """Initialise the event manager.
        
        Args:
            screen: The Pygame screen to render events on.
            game_state: The current state of the game.
        """
        self.screen = screen
        self.game_state = game_state

    def handle_mouse_click(self, pos):
        """Handle mouse click events.
        
        Args:
            pos: The position of the mouse click.
        """
        x = pos[0] // CELL_SIZE
        y = pos[1] // CELL_SIZE
        if x>= GRID_SIZE or y >= GRID_SIZE:
            return
        position = y * GRID_SIZE + x + 1
        if self.game_state.board.update(position, self.game_state.current_player):
            self.game_state.update()

    def handle_event(self, event) -> None:
        """Handle the Pygame event
        
        Args:
            event: A Pygame event object.
        """
        match event.type:
            case pygame.QUIT:
                self.game_state.running = False
                return
            case pygame.KEYDOWN:
                match event.key:
                    case pygame.K_r:
                        self.game_state.reset_game()
                    case pygame.K_ESCAPE:
                        self.game_state.running = False
                return
            case pygame.MOUSEBUTTONDOWN:
                if self.game_state.game_over:
                    self.game_state.reset_game()
                    return
                pos = pygame.mouse.get_pos()
                self.handle_mouse_click(pos)
                return
