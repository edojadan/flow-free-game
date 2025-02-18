# game.py

import pygame
from level_notation import parse_level

class Board:
    def __init__(self, level_data, cell_size=60):
        self.cell_size = cell_size
        self.height, self.width, self.grid = parse_level(level_data)
        # current_path: list of (row, col) cells
        self.current_path = []
        self.current_color = None
        self.mouse_down = False

    def handle_event(self, event):
        """Handle a single Pygame event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.mouse_down = True
                row_col = self._cell_from_mouse()
                if row_col is not None:
                    r, c = row_col
                    color = self.grid[r][c]
                    # If it's an endpoint cell, start a path
                    if color is not None:
                        self.current_path = [(r, c)]
                        self.current_color = color
                    else:
                        self.current_path = []
                        self.current_color = None

        elif event.type == pygame.MOUSEMOTION:
            if self.mouse_down and self.current_color is not None:
                row_col = self._cell_from_mouse()
                if row_col is not None:
                    self._try_add_cell(row_col)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_down = False
                # Here you might check if the path ends on another endpoint of the same color
                # For now, we simply stop drawing the path
                self.current_path = []
                self.current_color = None

    def update(self, dt):
        """Update game state if needed. dt is time since last frame in seconds."""
        pass

    def draw(self, screen):
        """Draw the grid and current path onto the screen."""
        screen.fill((0, 0, 0))  # black background
        # Draw cells
        for r in range(self.height):
            for c in range(self.width):
                x = c * self.cell_size
                y = r * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                # Draw border
                pygame.draw.rect(screen, (160, 160, 160), rect, width=1)
                # Draw endpoint if color is not None
                color = self.grid[r][c]
                if color is not None:
                    # draw a circle inside the cell
                    center = (x + self.cell_size // 2, y + self.cell_size // 2)
                    radius = self.cell_size // 2 - 5
                    pygame.draw.circle(screen, color, center, radius)

        # Draw current path
        if self.current_path and self.current_color:
            path_points = []
            for (r, c) in self.current_path:
                px = c * self.cell_size + self.cell_size / 2
                py = r * self.cell_size + self.cell_size / 2
                path_points.append((px, py))

            # Draw thick lines between consecutive points
            if len(path_points) > 1:
                pygame.draw.lines(screen, self.current_color, False, path_points, width=8)
            else:
                # If just one cell in path, draw a smaller circle
                (px, py) = path_points[0]
                pygame.draw.circle(screen, self.current_color, (px, py), 8)

    def _cell_from_mouse(self):
        """Returns (row, col) of the cell under the current mouse position, or None if out of bounds."""
        x, y = pygame.mouse.get_pos()
        col = x // self.cell_size
        row = y // self.cell_size
        if 0 <= row < self.height and 0 <= col < self.width:
            return (row, col)
        return None

    def _try_add_cell(self, row_col):
        """Attempt to add a new cell to the current path if it's adjacent to the last cell."""
        if not self.current_path:
            return
        last_cell = self.current_path[-1]
        if row_col != last_cell:
            # Check adjacency
            if abs(row_col[0] - last_cell[0]) + abs(row_col[1] - last_cell[1]) == 1:
                # If we've already visited it in this path, backtrack or do nothing
                if row_col in self.current_path:
                    idx = self.current_path.index(row_col)
                    self.current_path = self.current_path[:idx+1]
                else:
                    self.current_path.append(row_col)
