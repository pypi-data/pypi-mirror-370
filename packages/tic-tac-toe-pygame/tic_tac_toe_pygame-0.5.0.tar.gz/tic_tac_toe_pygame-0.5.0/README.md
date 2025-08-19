[![Python](https://img.shields.io/pypi/pyversions/tic-tac-toe-pygame.svg)](https://badge.fury.io/py/tic-tac-toe-pygame)
[![PyPI](https://badge.fury.io/py/tic-tac-toe-pygame.svg)](https://badge.fury.io/py/tic-tac-toe-pygame)
[![License](https://img.shields.io/github/license/giansimone/tic-tac-toe-pygame)](https://github.com/giansimone/tic-tac-toe-pygame/blob/main/LICENSE)

# tic-tac-toe-pygame

![Tic-Tac-Toe game screenshot](assets/tictactoe-screenshot.png)

A Python implementation of the Tic-Tac-Toe game using Pygame.

## Overview

This is a simple Tic-Tac-Toe game built with Pygame. The game allows two players to play against each other on a 3x3 grid. Players take turns placing their marks (_X_ or _O_) in the empty cells of the grid until one player wins or the game ends in a draw. The game checks for winning conditions after each move and displays the result on the screen.

## Features

- Two-player mode.
- Simple and intuitive interface.
- Win detection and draw handling.
- Pygame graphics.

## Requirements

- Python 3.10 or higher.
- Pygame library.

## Installation

To install the required dependencies, run:

```bash
pip install tic-tac-toe-pygame
```

## Usage

To run the game, execute the following command in your terminal:

```bash
python -m tic_tac_toe_pygame
```

## Game Rules

- The game is played on a 3x3 grid.
- Players take turns placing their marks (_X_ or _O_) in the empty cells.
- The first player to align three of their marks horizontally, vertically, or diagonally wins the game.
- If all cells are filled and no player has three in a row, the game ends in a draw.

## How to Play

1. Start the game by running the command above.
2. The game window will open displaying a 3x3 grid.
3. Players take turns clicking on the empty cells to place their marks.
4. The game will announce the winner or if the game ends in a draw.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
