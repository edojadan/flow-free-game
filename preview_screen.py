import pygame
from collections import deque
from screens import BaseScreen
from button import Button
from game import Board
from level_notation import parse_level

class PreviewScreen(BaseScreen):
    def __init__(self, switch_screen_callback, puzzle_data):
        super().__init__()
        self.switch_screen_callback = switch_screen_callback
        
        # Parse puzzle_data (i.e. [height, width, "encoded_string"])
        self.height, self.width, self.grid = parse_level(puzzle_data)
        
        # Create a Board so we can draw it
        self.board = Board(puzzle_data)
        
        # Solve the puzzle so it's displayed in a solved state
        solved_paths = self._solve_board()
        if solved_paths:
            # Mark each color’s path
            for color, path in solved_paths.items():
                self.board.paths[color] = path
                for (r, c) in path:
                    self.board.cell_owner[r][c] = color
            self.board.solved = True
        else:
            print("PreviewScreen: Could not solve puzzle automatically.")
        
        # Add a 'Close' button at the bottom center
        screen_rect = pygame.display.get_surface().get_rect()
        btn_width, btn_height = 100, 40
        self.buttons.append(Button(
            rect=(
                screen_rect.centerx - btn_width//2,
                screen_rect.height - btn_height - 20,
                btn_width,
                btn_height
            ),
            text="Close",
            callback=lambda: self.switch_screen_callback("generate_level")
        ))

    def _solve_board(self):
        """
        Simple BFS-based solver to fill the puzzle with exactly one path per color,
        returning {color: [(r,c), (r,c), ...], ...} if solved, else None.
        """
        endpoints = self.board.endpoints  # e.g. {'a': [(r0,c0),(r1,c1)], ...}
        used = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        # Pre-mark endpoints in 'used'
        for color, eps in endpoints.items():
            for (r, c) in eps:
                used[r][c] = color

        color_paths = {}
        for color, eps in endpoints.items():
            if len(eps) != 2:
                return None
            start, goal = eps[0], eps[1]
            path = self._bfs_path(start, goal, used, color)
            if not path:
                return None
            for (r, c) in path:
                used[r][c] = color
            color_paths[color] = path

        # Check coverage
        for r in range(self.height):
            for c in range(self.width):
                if used[r][c] is None:
                    return None
        return color_paths

    def _bfs_path(self, start, goal, used, color):
        queue = deque([[start]])
        visited = {start}
        while queue:
            path = queue.popleft()
            (r, c) = path[-1]
            if (r, c) == goal:
                return path
            for nr, nc in [(r-1,c),(r+1,c),(r,c-1),(r,c+1)]:
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    if (nr, nc) not in visited:
                        # We allow using (nr, nc) if it's empty or belongs to the same color
                        # or if it’s the goal endpoint
                        if (nr, nc) == goal or used[nr][nc] in (None, color):
                            visited.add((nr, nc))
                            queue.append(path + [(nr, nc)])
        return None

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((0,0,0))
        self.board.draw(surface)
        for btn in self.buttons:
            btn.draw(surface)
