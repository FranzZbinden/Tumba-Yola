import pygame

class Button:

    DEFAULT_COLOR = (200, 200, 200)
    BORDER_COLOR = (0, 0, 0)

    def __init__(self, row, col, x, y, btn_width, btn_height):
        self.rect = pygame.Rect(x, y, btn_width, btn_height)
        self.index = (row, col)
        self.color = Button.DEFAULT_COLOR

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, Button.BORDER_COLOR, self.rect, 2)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)