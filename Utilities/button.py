import pygame

class Button:

    DEFAULT_COLOR = (200, 200, 200)
    BORDER_COLOR = (0, 0, 0)

    def __init__(self, row, col, x, y, btn_width, btn_height):
        self.rect = pygame.Rect(x, y, btn_width, btn_height)
        self.index = (row, col)
        self.color = Button.DEFAULT_COLOR
        self.image = None
        self._scaled_cache_key = None  # (id(image), w, h),         # Cache for scaled image 
        self._scaled_cache_img = None

    def draw(self, surface):
        if self.color is not None:
            pygame.draw.rect(surface, self.color, self.rect)
        if self.image is not None:
            w, h = self.rect.size
            if w > 0 and h > 0:
                key = (id(self.image), w, h)
                if key != self._scaled_cache_key:
                    try:
                        self._scaled_cache_img = pygame.transform.smoothscale(self.image, (w, h))
                    except Exception:
                        self._scaled_cache_img = self.image
                    self._scaled_cache_key = key
                surface.blit(self._scaled_cache_img, self.rect)
        pygame.draw.rect(surface, Button.BORDER_COLOR, self.rect, 2)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)