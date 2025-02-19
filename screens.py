import pygame
from button import Button
from game import Board
from levels import get_level
from puzzle_generator import generate_puzzle
from colors import COLOR_MAP
from puzzle_generator import make_puzzle_direct


# Global list to store previously generated puzzle data
generated_puzzles = []
generated_puzzle_index = 0  # which puzzle in the list we're on

class GenerateLevelScreen:
    def __init__(self, switch_screen_callback):
        self.switch_screen_callback = switch_screen_callback
        self.buttons = []
        self.font = pygame.font.SysFont(None, 32)
        self.selected_size = 6
        self.selected_flows = 1

        # Variables to keep track of user selections
        self.selected_size = 6
        self.selected_flows = 1

        screen_rect = pygame.display.get_surface().get_rect()
        mid_x = screen_rect.centerx

        # Buttons
        self.buttons.append(Button(
            rect=(mid_x - 100, 280, 200, 40),
            text="Preview",
            callback=self.preview_puzzle
        ))
        self.buttons.append(Button(
            rect=(mid_x - 100, 330, 200, 40),
            text="New Puzzle",
            callback=self.generate_new_puzzle
        ))
        self.buttons.append(Button(
            rect=(mid_x - 100, 380, 200, 40),
            text="Next Puzzle",
            callback=self.load_next_puzzle
        ))
        self.buttons.append(Button(
            rect=(mid_x - 100, 430, 200, 40),
            text="Back",
            callback=lambda: self.switch_screen_callback("main_menu")
        ))

    def preview_puzzle(self):
        # If we have at least one puzzle stored, display a solved preview
        if generated_puzzles:
            puzzle_data = generated_puzzles[-1]  # last generated
            # Switch to a special preview screen or create a pop-up
            # For demonstration, let's just jump to the GameScreen but mark it solved forcibly
            # or you can create a new "PreviewScreen"
            self.switch_screen_callback("game", extra=puzzle_data)
        else:
            print("No puzzle to preview yet.")

    def generate_new_puzzle(self):
        puzzle_data = make_puzzle_direct(self.selected_size, self.selected_size, self.selected_flows)
        # puzzle_data = [height, width, rle]
        generated_puzzles.append(puzzle_data)
        print("Generated puzzle:", puzzle_data)

    def load_next_puzzle(self):
        # Cycle among stored puzzles
        global generated_puzzle_index
        if not generated_puzzles:
            print("No puzzles generated yet.")
            return
        generated_puzzle_index = (generated_puzzle_index + 1) % len(generated_puzzles)
        puzzle = generated_puzzles[generated_puzzle_index]
        self.switch_screen_callback("game", extra=puzzle)

    def handle_event(self, event):
        # Capture user input for puzzle size and flow count
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # Increase puzzle size
                if self.selected_size < 12:
                    self.selected_size += 1
                    # Make sure flows <= selected_size
                    if self.selected_flows > self.selected_size:
                        self.selected_flows = self.selected_size
            elif event.key == pygame.K_DOWN:
                # Decrease puzzle size
                if self.selected_size > 6:
                    self.selected_size -= 1
                    # Make sure flows <= selected_size
                    if self.selected_flows > self.selected_size:
                        self.selected_flows = self.selected_size
            elif event.key == pygame.K_RIGHT:
                # Increase flows
                if self.selected_flows < self.selected_size:
                    self.selected_flows += 1
            elif event.key == pygame.K_LEFT:
                # Decrease flows
                if self.selected_flows > 1:
                    self.selected_flows -= 1

        # Pass button events
        for btn in self.buttons:
            btn.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((20, 20, 20))
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Generate Level (Beta)", True, (255, 255, 255))
        surface.blit(title, (50, 50))

        # Instructions
        instructions = [
            "Use UP/DOWN to select size (6 to 12).",
            "Use LEFT/RIGHT to select flows (1 to size).",
            f"Current size = {self.selected_size}x{self.selected_size}",
            f"Current flows = {self.selected_flows}",
        ]
        y = 120
        for line in instructions:
            text_surf = self.font.render(line, True, (200, 200, 200))
            surface.blit(text_surf, (50, y))
            y += 30

        # Draw buttons
        for btn in self.buttons:
            btn.draw(surface)

class BaseScreen:
    def __init__(self):
        self.buttons = []

    def update(self, dt):
        pass

    def draw(self, surface):
        for btn in self.buttons:
            btn.draw(surface)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

class SplashScreen(BaseScreen):
    def __init__(self, switch_screen_callback):
        super().__init__()
        self.switch_screen_callback = switch_screen_callback
        self.time_elapsed = 0
        self.logo_font = pygame.font.SysFont(None, 72)

    def update(self, dt):
        self.time_elapsed += dt
        if self.time_elapsed > 1:  # show splash for 2 seconds
            self.switch_screen_callback("main_menu")

    def draw(self, surface):
        surface.fill((0, 0, 0))
        text = self.logo_font.render("Flow Free", True, (255,255,0))
        rect = text.get_rect(center=surface.get_rect().center)
        surface.blit(text, rect)

class MainMenuScreen(BaseScreen):
    def __init__(self, switch_screen_callback):
        super().__init__()
        self.switch_screen_callback = switch_screen_callback
        screen_rect = pygame.display.get_surface().get_rect()
        mid_x = screen_rect.centerx
        self.buttons.append(Button(rect=(mid_x - 100, 400, 420, 50),
                                   text="Generate Level beta test",
                                   callback=lambda: self.switch_screen_callback("generate_level")))
        self.buttons.append(Button(rect=(mid_x-100, 200, 200, 50),
                                   text="Play",
                                   callback=lambda: self.switch_screen_callback("game")))
        self.buttons.append(Button(rect=(mid_x-100, 300, 200, 50),
                                   text="Color Schemes",
                                   callback=lambda: self.switch_screen_callback("color_scheme")))
    
    def draw(self, surface):
        surface.fill((30, 30, 30))
        font = pygame.font.SysFont(None, 48)
        title = font.render("Main Menu", True, (255,255,255))
        title_rect = title.get_rect(center=(surface.get_width()//2, 100))
        surface.blit(title, title_rect)
        super().draw(surface)

class GameScreen(BaseScreen):
    def __init__(self, switch_screen_callback, level_data=None):
        super().__init__()
        self.switch_screen_callback = switch_screen_callback
        # Load a level; if none is provided, use default from levels.py
        if level_data is None:
            level_data = get_level(0)
        self.board = Board(level_data, cell_size=60)
        # Add control buttons
        self.buttons.append(Button(rect=(10, 450, 100, 40),
                                   text="Back",
                                   callback=lambda: self.switch_screen_callback("main_menu")))
        self.buttons.append(Button(rect=(120, 450, 100, 40),
                                   text="Undo",
                                   callback=self.undo))
        self.buttons.append(Button(rect=(230, 450, 100, 40),
                                   text="Restart",
                                   callback=self.restart))
    
    def undo(self):
        print("Undo pressed")
        # Implement undo logic if desired
    
    def restart(self):
        print("Restart pressed")
        # Restart the level by reinitializing the board
        # (For simplicity, we reload the same level)
        from levels import get_level
        self.board = Board(get_level(0), cell_size=60)
    
    def update(self, dt):
        self.board.update(dt)
        # If the board is solved, switch to the level completion screen
        if self.board.solved:
            self.switch_screen_callback("level_complete", extra=self.board)
    
    def draw(self, surface):
        surface.fill((0, 0, 0))
        self.board.draw(surface)
        super().draw(surface)
    
    def handle_event(self, event):
        self.board.handle_event(event)
        super().handle_event(event)

class LevelCompletionScreen(BaseScreen):
    def __init__(self, switch_screen_callback, board):
        super().__init__()
        self.switch_screen_callback = switch_screen_callback
        self.board = board
        screen_rect = pygame.display.get_surface().get_rect()
        mid_x = screen_rect.centerx
        self.message = "Level Completed!"
        self.buttons.append(Button(rect=(mid_x-100, 300, 200, 50),
                                   text="Next Level",
                                   callback=lambda: self.switch_screen_callback("game")))
        self.buttons.append(Button(rect=(mid_x-100, 370, 200, 50),
                                   text="New Puzzle",
                                   callback=lambda: self.switch_screen_callback("game")))
        self.buttons.append(Button(rect=(mid_x-100, 440, 200, 50),
                                   text="Home",
                                   callback=lambda: self.switch_screen_callback("main_menu")))
    
    def draw(self, surface):
        surface.fill((20, 20, 20))
        font = pygame.font.SysFont(None, 60)
        text = font.render(self.message, True, (0, 255, 0))
        rect = text.get_rect(center=(surface.get_width()//2, 150))
        surface.blit(text, rect)
        super().draw(surface)

class ColorSchemeScreen(BaseScreen):
    def __init__(self, switch_screen_callback, apply_scheme_callback):
        super().__init__()
        self.switch_screen_callback = switch_screen_callback
        self.apply_scheme_callback = apply_scheme_callback
        # Define 7 fruit-based color schemes as an example.
        self.schemes = {
            "Apple": {
                'a': (255, 0, 0),
                'b': (0, 255, 0),
                'c': (0, 0, 255),
                'd': (255, 255, 0),
                'e': (255, 165, 0),
                'f': (0, 255, 255),
                'g': (255, 192, 203),
            },
            "Banana": {
                'a': (240, 230, 140),
                'b': (255, 255, 102),
                'c': (255, 204, 51),
                'd': (255, 255, 51),
                'e': (255, 204, 102),
                'f': (255, 255, 153),
                'g': (255, 255, 102),
            },
            "Grape": {
                'a': (128, 0, 128),
                'b': (153, 50, 204),
                'c': (186, 85, 211),
                'd': (138, 43, 226),
                'e': (147, 112, 219),
                'f': (216, 191, 216),
                'g': (221, 160, 221),
            },
            "Orange": {
                'a': (255, 69, 0),
                'b': (255, 140, 0),
                'c': (255, 165, 0),
                'd': (255, 99, 71),
                'e': (255, 127, 80),
                'f': (255, 160, 122),
                'g': (255, 69, 0),
            },
            "Lime": {
                'a': (50, 205, 50),
                'b': (124, 252, 0),
                'c': (0, 255, 0),
                'd': (173, 255, 47),
                'e': (127, 255, 0),
                'f': (0, 250, 154),
                'g': (50, 205, 50),
            },
            "Cherry": {
                'a': (222, 49, 99),
                'b': (255, 105, 180),
                'c': (255, 20, 147),
                'd': (219, 112, 147),
                'e': (255, 0, 127),
                'f': (255, 20, 147),
                'g': (222, 49, 99),
            },
            "Blueberry": {
                'a': (0, 0, 139),
                'b': (25, 25, 112),
                'c': (65, 105, 225),
                'd': (30, 144, 255),
                'e': (100, 149, 237),
                'f': (70, 130, 180),
                'g': (0, 0, 139),
            }
        }
        # Create a button for each scheme.
        screen_rect = pygame.display.get_surface().get_rect()
        y = 150
        for name in self.schemes.keys():
            self.buttons.append(Button(
                rect=(50, y, 200, 40),
                text=name,
                callback=lambda n=name: self.apply_scheme(n)
            ))
            y += 50
        # Add a Back button.
        self.buttons.append(Button(
            rect=(50, y + 20, 200, 40),
            text="Back",
            callback=lambda: self.switch_screen_callback("main_menu")
        ))
    
    def apply_scheme(self, scheme_name):
        scheme = self.schemes[scheme_name]
        # Apply the scheme instantly.
        self.apply_scheme_callback(scheme)
        # Immediately switch back to the game screen (a new Board will be created using the new scheme).
        self.switch_screen_callback("game")
    
    def draw(self, surface):
        surface.fill((40, 40, 40))
        font = pygame.font.SysFont(None, 48)
        text = font.render("Color Schemes", True, (255, 255, 255))
        rect = text.get_rect(center=(surface.get_width() // 2, 80))
        surface.blit(text, rect)
        super().draw(surface)

