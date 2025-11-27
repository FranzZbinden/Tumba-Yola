import pygame
import sys


def show_end_screen(message: str = "Game Over") -> None:
    pygame.init()
    WIDTH, HEIGHT = 600, 300
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game Result")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("arialblack", 48)
    subfont = pygame.font.SysFont("arial", 24)

    text_surf = font.render(message, True, (255, 255, 255))
    hint_surf = subfont.render("Press any key or close window to exit", True, (200, 200, 200))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                running = False
        window.fill((30, 30, 30))
        window.blit(text_surf, ( (WIDTH - text_surf.get_width()) // 2,
                                 (HEIGHT - text_surf.get_height()) // 2 - 20 ))
        window.blit(hint_surf, ( (WIDTH - hint_surf.get_width()) // 2,
                                  (HEIGHT - hint_surf.get_height()) // 2 + 40 ))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)

