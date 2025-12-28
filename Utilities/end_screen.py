import pygame
from pathlib import Path

# Result: "win" or "lose"
def _load_bg(result: str, size: tuple[int, int]) -> pygame.Surface | None:
    try:
        project_root = Path(__file__).parent.parent
        bg_dir = project_root / "source_files" / "sprites" / "backgrounds"
        name = "win_img.png" if result == "win" else "lose_img.png"
        img = pygame.image.load(str(bg_dir / name)).convert()
        return pygame.transform.smoothscale(img, size)
    except Exception:
        return None

# Falls back to a system font if the file isn't available.
def _load_jersey10_font(size: int) -> pygame.font.Font:
    project_root = Path(__file__).parent.parent
    font_path = project_root / "source_files" / "fonts" / "Jersey10-Regular.ttf"
    try:
        if font_path.exists():
            return pygame.font.Font(str(font_path), size)
    except Exception:
        pass
    return pygame.font.SysFont("sans-serif", size)


def _draw_button(surface: pygame.Surface, rect: pygame.Rect, text: str, font: pygame.font.Font, bg: tuple[int, int, int]):
    pygame.draw.rect(surface, bg, rect, border_radius=10)
    pygame.draw.rect(surface, (0, 0, 0), rect, 2, border_radius=10)
    label = font.render(text, True, (255, 255, 255))
    surface.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    # Shows an end screen and returns the user's choice:
    # - "quit"
    # - "next_match"
def show_end_screen(message: str = "Game Over", result: str | None = None) -> str:
    pygame.init()

    WIDTH, HEIGHT = 535, 500
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game Result")
    clock = pygame.time.Clock()

    title_font = _load_jersey10_font(90)
    button_font = _load_jersey10_font(40)
    hint_font = pygame.font.SysFont("sans-serif", 20)

    # Pick background based on result (default: dark fill)
    bg = _load_bg(result if result in ("win", "lose") else "lose", (WIDTH, HEIGHT)) if result else None
    title_color = (255, 255, 255)
    if result == "win":
        title_color = (60, 220, 90)
    elif result == "lose":
        title_color = (220, 60, 60)

    # Buttons
    btn_w, btn_h = 225, 56
    gap = 22
    group_w = btn_w * 2 + gap
    y = HEIGHT - 90
    x0 = (WIDTH - group_w) // 2

    quit_rect = pygame.Rect(x0, y, btn_w, btn_h)
    next_rect = pygame.Rect(x0 + btn_w + gap, y, btn_w, btn_h)

    action = "quit"
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                action = "quit"
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if quit_rect.collidepoint(event.pos):
                    action = "quit"
                    running = False
                elif next_rect.collidepoint(event.pos):
                    action = "next_match"
                    running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    action = "quit"
                    running = False

        if bg is not None:
            window.blit(bg, (0, 0))
        else:
            window.fill((18, 18, 18))

        # Message (with a subtle shadow for readability)
        text = title_font.render(message, True, title_color)
        shadow = title_font.render(message, True, (0, 0, 0))
        tx = (WIDTH - text.get_width()) // 2
        ty = 70
        window.blit(shadow, (tx + 2, ty + 2))
        window.blit(text, (tx, ty))

        hint = hint_font.render("ESC = Quit", True, (240, 240, 240))
        window.blit(hint, (15, HEIGHT - hint.get_height() - 15))

        _draw_button(window, quit_rect, "QUIT", button_font, (220, 60, 60))
        _draw_button(window, next_rect, "NEXT MATCH", button_font, (40, 160, 90))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return action

