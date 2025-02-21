import pygame
from button import Button
from game import Board
from levels import get_level
from colors import COLOR_MAP
from level_generator import generate_level


# Global list to store previously generated puzzle data
generated_puzzles = []
generated_puzzle_index = 0  # which puzzle in the list we're on

class GenerateLevelScreen:
    def __init__(self, switch_screen_callback):
        self.switch_screen_callback = switch_screen_callback
        self.buttons = []
        self.font = pygame.font.SysFont(None, 32)
        self.selected_size = 6
        "self.selected_flows = 1"

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
        if generated_puzzles:
            puzzle_data = generated_puzzles[-1]
            self.switch_screen_callback("preview_puzzle", extra=puzzle_data)
        else:
            print("No puzzle to preview yet.")

    def generate_new_puzzle(self):
        puzzle_data = generate_level(self.selected_size)
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
            """elif event.key == pygame.K_RIGHT:
                # Increase flows
                if self.selected_flows < self.selected_size:
                    self.selected_flows += 1
            elif event.key == pygame.K_LEFT:
                # Decrease flows
                if self.selected_flows > 1:
                    self.selected_flows -= 1"""

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
            f"Current size = {self.selected_size}x{self.selected_size}",
            #f"Current flows = {self.selected_flows}",
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
    def handle_resize(self, new_w, new_h):
        # Default implementation (no operation)
        pass

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
        self.buttons.append(Button(rect=(mid_x -170, 400, 420, 50),
                                   text="Generate Level beta test",
                                   callback=lambda: self.switch_screen_callback("generate_level")))
        self.buttons.append(Button(rect=(mid_x-100, 200, 200, 50),
                                   text="Play",
                                   callback=lambda: self.switch_screen_callback("game")))
        self.buttons.append(Button(rect=(mid_x-100, 300, 200, 50),
                                   text="Color Schemes",
                                   callback=lambda: self.switch_screen_callback("color_scheme")))
        self.buttons.append(Button(rect=(mid_x-170, 500, 500, 50),
                                   text="Previous levels beta test",
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
        self.buttons = []
    
        # Load a level; if none is provided, use default from levels.py
        if level_data is None:
            level_data = get_level(0)
        self.board = Board(level_data, cell_size=60)
        
        # We'll create the Button objects, but hold an identifier for each
        self.btn_back = Button(rect=(10,450,100,40), text="Back", callback=lambda: self.switch_screen_callback("main_menu"))
        self.btn_restart = Button(rect=(230, 450,100,40), text="Restart", callback=self.restart)

        self.buttons.extend([self.btn_back, self.btn_restart])


    def handle_resize(self, new_width, new_height):
        """
        Called when the window is resized; reposition everything accordingly.
        """
        # Suppose you want to place the buttons at the bottom, spaced evenly:
        margin_bottom = 20
        button_width = 100
        button_height = 40
        
        # e.g. place them horizontally spaced at x=10,120,230, pinned near the bottom
        self.btn_back.rect = pygame.Rect(10, new_height - button_height - margin_bottom, button_width, button_height)
        self.btn_restart.rect = pygame.Rect(230, new_height - button_height - margin_bottom, button_width, button_height)

        new_width
    
    
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
        self.schemes = {
            "Apple": {
                'a': (255,   0,   0),  # Bright red
                'b': (153,   0,   0),  # Darker red
                'c': (255, 102, 102),  # Light/pinkish red
                'd': (204,  51,  51),  # Muted red
                'e': (  0, 255,   0),  # Bright green
                'f': (  0, 153,   0),  # Darker green
                'g': (102, 255, 102),  # Pastel green
                'h': ( 51, 204,  51),  # Medium‐bright green
                'i': (255, 255,   0),  # Yellow
                'j': (255, 128,   0),  # Orange
                'k': (153,   0, 153),  # Purple
                'l': (  0, 255, 255),  # Cyan
            },
            "Banana": {
                'a': (255, 255, 102),  # Pale yellow
                'b': (255, 255,   0),  # Primary yellow
                'c': (204, 204,   0),  # Duller yellow
                'd': (255, 204,  51),  # Orange‐yellow
                'e': (255, 229, 153),  # Very light banana
                'f': (255, 255, 153),  # Light pastel yellow
                'g': (248, 229, 145),  # Slightly warm banana
                'h': (255, 230, 120),  # Peachy yellow
                'i': (153, 204,  51),  # Yellow‐green
                'j': (204, 255,   0),  # Lime‐ish
                'k': (255, 153,   0),  # Deeper orange
                'l': (255, 102,   0),  # Reddish orange
            },
            "Grape": {
                'a': (128,   0, 128),  # Classic purple
                'b': (153,  50, 204),  # Medium purple
                'c': (186,  85, 211),  # Orchid
                'd': (147, 112, 219),  # Medium purple / pastel
                'e': ( 75,   0, 130),  # Indigo
                'f': (216, 191, 216),  # Thistle
                'g': (238, 130, 238),  # Violet
                'h': (221, 160, 221),  # Plum
                'i': (255,   0, 255),  # Magenta
                'j': (255, 192, 203),  # Pink
                'k': (  0, 255, 255),  # Cyan for contrast
                'l': (255, 255,   0),  # Bright yellow contrast
            },
            "Orange": {
                'a': (255,  69,   0),  # Orange red
                'b': (255, 140,   0),  # Dark orange
                'c': (255, 165,   0),  # Standard orange
                'd': (255,  99,  71),  # Tomato
                'e': (255, 127,  80),  # Coral
                'f': (255, 160, 122),  # Light salmon
                'g': (255, 200, 120),  # Lighter orange
                'h': (255, 100,  50),  # Vibrant orange
                'i': (128,   0,   0),  # Maroon
                'j': (255,  20, 147),  # Hot pink for contrast
                'k': (  0, 255, 255),  # Cyan for contrast
                'l': (255, 255,   0),  # Bright yellow
            },
            "Lime": {
                'a': (  0, 255,   0),  # Bright green
                'b': (124, 252,   0),  # Lawn green
                'c': ( 50, 205,  50),  # Lime green
                'd': (127, 255,   0),  # Chartreuse
                'e': (173, 255,  47),  # Green‐yellow
                'f': (102, 255, 102),  # Pastel green
                'g': (  0, 153,   0),  # Dark green
                'h': (152, 251, 152),  # Pale green
                'i': (  0, 255, 255),  # Cyan accent
                'j': (255, 255,   0),  # Yellow accent
                'k': (255, 128,   0),  # Orange accent
                'l': (153,   0, 153),  # Purple accent
            },
            "Cherry": {
                'a': (222,  49,  99),  # Raspberry
                'b': (255, 105, 180),  # Hot pink
                'c': (255,  20, 147),  # Deep pink
                'd': (219, 112, 147),  # Pale violet red
                'e': (255,   0, 127),  # Rose
                'f': (229,  57,  53),  # Another bright red
                'g': (153,   0,   0),  # Darker red
                'h': (255, 102, 102),  # Light red/pink
                'i': (255, 128,   0),  # Contrasting orange
                'j': (255, 255,   0),  # Bright yellow
                'k': (  0, 255, 255),  # Cyan
                'l': (128,   0, 128),  # Purple
            },
            "Blueberry": {
                'a': (  0,   0, 139),  # Dark blue
                'b': ( 25,  25, 112),  # Midnight blue
                'c': ( 65, 105, 225),  # Royal blue
                'd': ( 30, 144, 255),  # Dodger blue
                'e': (100, 149, 237),  # Cornflower
                'f': ( 70, 130, 180),  # Steel blue
                'g': (  0,   0, 255),  # Pure blue
                'h': (  0, 191, 255),  # Deep sky
                'i': (  0, 255, 255),  # Cyan
                'j': (138,  43, 226),  # Blue violet
                'k': (143,   0, 255),  # Vivid purple
                'l': (255, 255,   0),  # Yellow accent
            },
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

