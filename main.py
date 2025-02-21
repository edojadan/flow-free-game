import pygame
import sys
from screens import SplashScreen, MainMenuScreen, GameScreen, LevelCompletionScreen, ColorSchemeScreen
import colors  # our colors.py module
from preview_screen import PreviewScreen

def apply_scheme_callback(scheme):
    # Update the global color mapping in colors.py.
    colors.COLOR_MAP.clear()
    colors.COLOR_MAP.update(scheme)
    print("Applied color scheme:", scheme)

def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 700), pygame.RESIZABLE)
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
        elif screen_name == "generate_level":
            from screens import GenerateLevelScreen
            current_screen = GenerateLevelScreen(switch_screen_callback=switch_screen)
        elif screen_name == "preview_puzzle":
            # puzzle_data is in 'extra'
             current_screen = PreviewScreen(switch_screen_callback=switch_screen, puzzle_data=extra)
        elif screen_name == "generate_level":
            current_screen = GenerateLevelScreen(switch_screen_callback=switch_screen)
    
    switch_screen("splash")

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(30)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                new_w, new_h = event.w, event.h
                screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
                if current_screen:
                    current_screen.handle_resize(new_w, new_h)
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

