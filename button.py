import pygame

class Button:
    def __init__(self, rect, text, callback, font=None, text_color=(255,255,255), bg_color=(50,50,50)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font or pygame.font.SysFont(None, 36)
        self.text_color = text_color
        self.bg_color = bg_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, (255,255,255), self.rect, width=2)  # border
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()
