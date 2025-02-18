# screens.py
import pygame
from button import Button
from game import Board
from levels import get_level

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
        if self.time_elapsed > 2:  # show splash for 2 seconds
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
        self.buttons.append(Button(rect=(10, 10, 100, 40),
                                   text="Back",
                                   callback=lambda: self.switch_screen_callback("main_menu")))
        self.buttons.append(Button(rect=(120, 10, 100, 40),
                                   text="Undo",
                                   callback=self.undo))
        self.buttons.append(Button(rect=(230, 10, 100, 40),
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
