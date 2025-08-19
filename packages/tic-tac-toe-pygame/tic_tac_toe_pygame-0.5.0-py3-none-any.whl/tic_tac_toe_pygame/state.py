"""
Tic-Tac-Toe game state module.
"""
import random

from tic_tac_toe_pygame.config import WINNING_COMBINATIONS


class Board:
    """A class to represent the Tic-Tac-Toe board."""

    def __init__(self):
        """Initialise the board with empty spaces."""
        self.reset()

    def __getitem__(self, position: int) -> str:
        """Get the value at a specific position on the board."""
        return self.board[position]

    def reset(self):
        """Reset the board to empty spaces."""
        self.board = [' ' for _ in range(9)]

    def update(self, position: int, player: str) -> bool:
        """Update the board with the player's move.
        
        Args:
            position (int): The position on the board (1-9).
            player (str): The player's symbol ('X' or 'O').
        
        Returns:
            bool: True if the move was successful, False if the position is already occupied.
        """
        if self.board[position - 1] == ' ':
            self.board[position - 1] = player
            return True
        return False


class GameState:
    """A class to represent the Tic-Tac-Toe game state."""

    def __init__(self):
        """Initialise the game state."""
        self.board = Board()
        self.running = True
        self.current_player = None
        self.game_over = False
        self.winner = None
        self._select_first_player()

    def _select_first_player(self):
        """Randomly select the first player."""
        if random.randint(0, 1) == 0:
            self.current_player = 'X'
        else:
            self.current_player = 'O'

    def reset_game(self):
        """Reset the game board and select the first player."""
        self.board.reset()
        self.game_over = False
        self.winner = None
        self._select_first_player()

    def check_winner(self):
        """Check if there is a winner."""
        for combo in WINNING_COMBINATIONS:
            if all(self.board[i] == self.current_player for i in combo):
                return True
        return False

    def update(self):
        """Update the game state after each move."""
        if self.check_winner():
            self.winner = self.current_player
            self.game_over = True
        elif ' ' not in self.board:
            self.winner = 'Draw'
            self.game_over = True
        else:
            self.current_player = 'X' if self.current_player == 'O' else 'O'
