import pygame
from level_notation import parse_level

class Board:
    def __init__(self, level_data, cell_size=60):
        self.cell_size = cell_size
        self.height, self.width, self.grid = parse_level(level_data)

        # Find endpoints: color -> list of endpoint cells [(r1,c1), (r2,c2)]
        self.endpoints = {}
        for r in range(self.height):
            for c in range(self.width):
                color = self.grid[r][c]
                if color is not None:
                    if color not in self.endpoints:
                        self.endpoints[color] = []
                    self.endpoints[color].append((r, c))

        # paths[color] = list of (row, col) describing final path from one endpoint to the other
        # or None if that color not yet solved
        self.paths = {color: None for color in self.endpoints}

        # cell_owner[r][c] = which color currently occupies that cell’s path, or None if unused
        self.cell_owner = [[None for _ in range(self.width)] for _ in range(self.height)]

        # For user‐in‐progress path
        self.current_path = []
        self.current_color = None
        self.mouse_down = False

        self.solved = False  # Will be True once puzzle is solved

    def handle_event(self, event):
        """Handle Pygame events."""
        if self.solved:
            return  # If puzzle is solved, ignore further input

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                self.mouse_down = True
                cell = self._cell_from_mouse()
                if cell is not None:
                    r, c = cell
                    color = self.grid[r][c]
                    # Only start a path if it's an endpoint cell
                    if color is not None:
                        self.current_path = [cell]
                        self.current_color = color
                    else:
                        self.current_path = []
                        self.current_color = None

        elif event.type == pygame.MOUSEMOTION:
            if self.mouse_down and self.current_color is not None:
                cell = self._cell_from_mouse()
                if cell is not None:
                    self._try_add_cell(cell)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_down = False
                if self.current_color is not None and len(self.current_path) > 1:
                    # Check if path is valid: starts at endpoints[color][0] or [1], ends at the other
                    start = self.current_path[0]
                    end = self.current_path[-1]
                    ep = self.endpoints[self.current_color]
                    # We want a path that starts at ep[0] and ends at ep[1] (or vice versa)
                    if (start in ep and end in ep and start != end):
                        # This path is valid: store it
                        self.paths[self.current_color] = list(self.current_path)
                    else:
                        # Invalid path => remove it from cell_owner
                        for (r, c) in self.current_path:
                            if self.cell_owner[r][c] == self.current_color:
                                self.cell_owner[r][c] = None

                self.current_path = []
                self.current_color = None

                # Check if puzzle is solved
                self._check_solved()

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((0, 0, 0))  # black background

        # Draw grid lines + endpoints
        for r in range(self.height):
            for c in range(self.width):
                x = c * self.cell_size
                y = r * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(screen, (200, 200, 200), rect, width=1)

                # If it's an endpoint in the original grid, draw a circle
                if self.grid[r][c] is not None:
                    color = self.grid[r][c]
                    center = (x + self.cell_size // 2, y + self.cell_size // 2)
                    radius = self.cell_size // 2 - 4
                    pygame.draw.circle(screen, color, center, radius)

        # Draw final paths (for each color)
        for color, path_cells in self.paths.items():
            if path_cells:
                self._draw_path(screen, path_cells, color)

        # Draw the current, in‐progress path
        if self.current_path and self.current_color:
            self._draw_path(screen, self.current_path, self.current_color, in_progress=True)

        if self.solved:
            # Draw a "solved" message
            font = pygame.font.SysFont(None, 48)
            text_surf = font.render("Puzzle solved!", True, (255, 255, 0))
            screen.blit(text_surf, (20, 20))

    def _draw_path(self, screen, path_cells, color, in_progress=False):
        # Convert cell coords to pixel coords
        points = []
        for (r, c) in path_cells:
            x = c * self.cell_size + self.cell_size / 2
            y = r * self.cell_size + self.cell_size / 2
            points.append((x, y))
        thickness = 8 if not in_progress else 6
        if len(points) > 1:
            pygame.draw.lines(screen, color, False, points, thickness)
        else:
            # Single cell => draw small circle
            (px, py) = points[0]
            pygame.draw.circle(screen, color, (px, py), thickness)

    def _try_add_cell(self, cell):
        """Attempt to add 'cell' to current path, handle collisions, adjacency, etc."""
        if not self.current_path:
            return
        last_cell = self.current_path[-1]
        if cell == last_cell:
            return

        # Check adjacency
        if abs(cell[0] - last_cell[0]) + abs(cell[1] - last_cell[1]) == 1:
            r, c = cell
            # If this cell is occupied by a different color, remove that color's path
            owner = self.cell_owner[r][c]
            if owner is not None and owner != self.current_color:
                # Remove that path
                other_path = self.paths[owner]
                if other_path:
                    for (rr, cc) in other_path:
                        self.cell_owner[rr][cc] = None
                    self.paths[owner] = None

            # If we've already visited this cell in our path, backtrack
            if cell in self.current_path:
                idx = self.current_path.index(cell)
                self.current_path = self.current_path[:idx+1]
            else:
                self.current_path.append(cell)

            # Mark ownership
            for (rr, cc) in self.current_path:
                self.cell_owner[rr][cc] = self.current_color

    def _cell_from_mouse(self):
        """Returns (row, col) under mouse or None if out of bounds."""
        x, y = pygame.mouse.get_pos()
        col = x // self.cell_size
        row = y // self.cell_size
        if 0 <= row < self.height and 0 <= col < self.width:
            return (row, col)
        return None

    def _check_solved(self):
        """Set self.solved = True if all colors have valid paths and entire board is filled."""
        # 1) All colors must have a path
        for color, path in self.paths.items():
            if not path:
                return  # Not solved yet

        # 2) Every cell must be occupied by some color’s path
        for r in range(self.height):
            for c in range(self.width):
                if self.cell_owner[r][c] is None:
                    return  # Found an unused cell => not solved

        self.solved = True
        print("Puzzle solved!")