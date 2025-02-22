import pygame
import sys
from screens import SplashScreen, MainMenuScreen, GameScreen, LevelCompletionScreen, ColorSchemeScreen
import colors  # our colors.py module

def apply_scheme_callback(scheme):
    # Update the global color mapping in colors.py.
    # This assumes your game uses colors.COLOR_MAP during level parsing.
    colors.COLOR_MAP.clear()
    colors.COLOR_MAP.update(scheme)
    print("Applied color scheme:", scheme)

def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 500))
    pygame.display.set_caption("Flow Free Clone")
    
    current_screen = None

    def switch_screen(screen_name, extra=None):
        nonlocal current_screen
        if screen_name == "splash":
            current_screen = SplashScreen(switch_screen)
        elif screen_name == "main_menu":
            current_screen = MainMenuScreen(switch_screen)
        elif screen_name == "game":
            # Pass level data (extra) if provided; otherwise, use default.
            current_screen = GameScreen(switch_screen, level_data=extra)
        elif screen_name == "level_complete":
            current_screen = LevelCompletionScreen(switch_screen, board=extra)
        elif screen_name == "color_scheme":
            # Pass the apply_scheme_callback so that scheme changes take effect instantly.
            current_screen = ColorSchemeScreen(switch_screen, apply_scheme_callback)
    
    switch_screen("splash")

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(30) / 1000.0  # ~30 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                if current_screen:
                    current_screen.handle_event(event)
        
        if current_screen:
            current_screen.update(dt)
            current_screen.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

