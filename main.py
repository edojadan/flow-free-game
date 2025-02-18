# main.py

import pygame
import sys
from game import Board

def main():
    pygame.init()
    pygame.display.set_caption("Flow Free Clone (Pygame)")

    # Example level data
    level_data = [6, 5, "1d2a4b2b1c2c10da"]
    cell_size = 60

    board = Board(level_data, cell_size=cell_size)

    # Create a window sized to fit the board
    screen_width = board.width * cell_size
    screen_height = board.height * cell_size
    screen = pygame.display.set_mode((screen_width, screen_height))

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(30) / 1000.0  # Limit to ~30 FPS, dt in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                board.handle_event(event)

        board.update(dt)
        board.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

