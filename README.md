# Flow Free Clone (Pygame Version)

A minimal Flow Free–style puzzle in Python **without** Tkinter, using **Pygame** for rendering.

## Setup

1. **Install Pygame** (e.g. `pip install pygame` or `pip3 install pygame`).
2. Run `python main.py`.

## How to Play

- A window will appear with a 6×5 grid
- Some cells have colored circles (the endpoints).
- Click (and hold) on one endpoint, then drag to adjacent cells to form a path.
- Release the mouse to finalize your path. (This example does not yet store or verify the final path, but you can extend it.)

## Files

- **main.py** – Pygame initialization and main game loop
- **game.py** – `Board` class for rendering and handling the puzzle
- **level_notation.py** – Parses a compact run‐length encoded level format
- **colors.py** – Maps single‐character color codes to `(R, G, B)` tuples
