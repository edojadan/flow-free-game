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
        Solves the puzzle using iterative deepening A* (IDA*).
        
        Assumes self.board.grid is a 2D list (size self.height x self.width) where:
        - None indicates an empty cell.
        - Nonempty cells are color tuples.
        
        This method first builds a local mapping from each unique color tuple to a unique lowercase letter,
        then converts the board into a 2D list of characters (empty = '0'; endpoints = assigned letter).
        
        It then uses IDA* with the heuristic h(board) = (number of empty cells) to search for a solution.
        Once the board is solved (no '0's remain and all cells are uppercase) it extracts, via BFS,
        each color’s complete path (as a list of (row, col) tuples).
        
        Returns:
        A dictionary mapping each original color tuple (from self.board.endpoints) to its solved path,
        or None if no solution is found.
        """
        # --- Step 1: Build a mapping from unique color tuples to unique lowercase letters ---
        unique_colors = []
        for row in self.board.grid:
            for cell in row:
                if cell is not None and cell not in unique_colors:
                    unique_colors.append(cell)
        available_letters = list("abcdefghijklmnopqrstuvwxyz")
        if len(unique_colors) > len(available_letters):
            print("Not enough letters for the number of unique colors.")
            return None
        mapping = {}
        for i, col in enumerate(unique_colors):
            mapping[col] = available_letters[i]
        
        # --- Step 2: Convert self.board.grid to a board of characters ---
        rows = self.height
        cols = self.width
        b = []
        for i in range(rows):
            new_row = []
            for j in range(cols):
                cell = self.board.grid[i][j]
                if cell is None:
                    new_row.append('0')
                else:
                    new_row.append(mapping[cell])
            b.append(new_row)
        
        # --- Helper Functions ---
        def count_empty(board):
            return sum(row.count('0') for row in board)
        
        def number_of_neighbours(board, x, y):
            count = 0
            cell = board[x][y]
            if x > 0 and board[x-1][y].lower() == cell.lower():
                count += 1
            if x < len(board) - 1 and board[x+1][y].lower() == cell.lower():
                count += 1
            if y > 0 and board[x][y-1].lower() == cell.lower():
                count += 1
            if y < len(board[0]) - 1 and board[x][y+1].lower() == cell.lower():
                count += 1
            return count

        def is_solved(board):
            # Board is solved if there are no empty cells and all cells are uppercase.
            for i in range(len(board)):
                for j in range(len(board[0])):
                    if board[i][j] == '0' or board[i][j] != board[i][j].upper():
                        return False
            # Also, for each color (ignoring case), there should be exactly two endpoints (cells with one neighbour).
            colors = set(cell.lower() for row in board for cell in row)
            for color in colors:
                end_count = 0
                for i in range(len(board)):
                    for j in range(len(board[0])):
                        if board[i][j].lower() == color:
                            n = number_of_neighbours(board, i, j)
                            if n == 1:
                                end_count += 1
                            elif n == 0:
                                return False
                if end_count != 2:
                    return False
            return True

        def pass_constraints_check(board):
            # Basic pruning: no cell should have >2 same-letter neighbours and each endpoint should have at least one adjacent empty.
            for i in range(len(board)):
                for j in range(len(board[0])):
                    if board[i][j] != '0' and number_of_neighbours(board, i, j) > 2:
                        return False
                    if board[i][j] in available_letters:
                        empty_adj = 0
                        if i > 0 and board[i-1][j] == '0':
                            empty_adj += 1
                        if i < len(board) - 1 and board[i+1][j] == '0':
                            empty_adj += 1
                        if j > 0 and board[i][j-1] == '0':
                            empty_adj += 1
                        if j < len(board[0]) - 1 and board[i][j+1] == '0':
                            empty_adj += 1
                        if empty_adj == 0:
                            return False
            return True

        def find_possible_moves(board):
            moves = []
            processed = set()
            rcount = len(board)
            ccount = len(board[0])
            for i in range(rcount):
                for j in range(ccount):
                    if board[i][j] in available_letters and board[i][j] not in processed:
                        for di, dj in [(1,0), (-1,0), (0,1), (0,-1)]:
                            ni, nj = i + di, j + dj
                            if 0 <= ni < rcount and 0 <= nj < ccount and board[ni][nj] == '0':
                                new_board = [row[:] for row in board]
                                new_board[ni][nj] = board[i][j]  # extend path
                                new_board[i][j] = board[i][j].upper()  # mark as used
                                moves.append(new_board)
                        processed.add(board[i][j])
            # Heuristic: prefer boards with fewer empty cells.
            moves.sort(key=count_empty)
            return moves

        # --- IDA* Search Implementation ---
        # Our cost so far is simply the number of moves (g), and heuristic h(board)=count_empty(board)
        def heuristic(board):
            return count_empty(board)
        
        def search(board, g, threshold):
            f = g + heuristic(board)
            if f > threshold:
                return f
            if is_solved(board):
                return board
            min_threshold = float('inf')
            if not pass_constraints_check(board):
                return float('inf')
            for nb in find_possible_moves(board):
                result = search(nb, g + 1, threshold)
                if isinstance(result, list):  # solution found (board is a list of lists)
                    return result
                if result < min_threshold:
                    min_threshold = result
            return min_threshold

        threshold = heuristic(b)
        MAX_THRESHOLD = 2  # Adjust as needed
        solved_board = None
        while threshold <= MAX_THRESHOLD:
            result = search([row[:] for row in b], 0, threshold)
            if isinstance(result, list):
                solved_board = result
                break
            if result == float('inf'):
                break
            threshold = result
        if solved_board is None:
            print("IDA* failed to find a solution within threshold limit.")
            return None

        # --- BFS Extraction of Color Paths ---
        def bfs_path(board, start, goal, letter):
            queue = deque([[start]])
            visited = {start}
            while queue:
                path = queue.popleft()
                (r, c) = path[-1]
                if (r, c) == goal:
                    return path
                for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < len(board) and 0 <= nc < len(board[0]):
                        if (nr, nc) not in visited:
                            if (nr, nc) == goal or board[nr][nc].lower() == letter:
                                visited.add((nr, nc))
                                queue.append(path + [(nr, nc)])
            return None

        color_paths = {}
        # self.board.endpoints is assumed to be a dict mapping original color tuple -> list of endpoints ((r,c) in 0-indexed coordinates)
        for orig_color, eps in self.board.endpoints.items():
            if len(eps) != 2:
                return None
            letter = mapping[orig_color]  # assigned letter for this color
            start, goal = eps[0], eps[1]
            path = bfs_path(solved_board, start, goal, letter)
            if path is None:
                return None
            color_paths[orig_color] = path

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
