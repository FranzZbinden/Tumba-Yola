import pygame
import sys
import os

pygame.init()

# Window
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TumbaYola - Start Screen")
clock = pygame.time.Clock()

# Assets
try:
    bg_path = os.path.join("sprites", "start_scr_img.png")
    bg_img = pygame.image.load(bg_path).convert()
    bg_img = pygame.transform.smoothscale(bg_img, (WIDTH, HEIGHT))
except Exception:
    bg_img = None  # fallback to solid color if image missing

# Colors
BG_COLOR = (30, 61, 89)
BUTTON_COLOR = (245, 166, 35)
EXIT_COLOR = (231, 76, 60)
TEXT_COLOR = (255, 255, 255)
INPUT_BG = (255, 255, 255)
INPUT_BORDER = (20, 20, 20)
INPUT_ACTIVE = (80, 140, 230)
PLACEHOLDER_COLOR = (140, 140, 140)

# Fonts
font_title = pygame.font.SysFont("arialblack", 54)
font_label = pygame.font.SysFont("arial", 26)
font_button = pygame.font.SysFont("arial", 28)
font_input = pygame.font.SysFont("consolas", 26)


class InputBox:
    def __init__(self, x, y, w, h, placeholder="Enter server IP..."):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.placeholder = placeholder

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                pass  # no-op (UI only for now)
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                ch = event.unicode
                # Restrict to typical IP characters (digits, dot, colon)
                if ch.isdigit() or ch in ".:":
                    if len(self.text) < 21:
                        self.text += ch

    def draw(self, surf):
        # Background
        pygame.draw.rect(surf, INPUT_BG, self.rect, border_radius=6)
        # Border
        pygame.draw.rect(surf, INPUT_ACTIVE if self.active else INPUT_BORDER, self.rect, 2, border_radius=6)
        # Text
        content = self.text if self.text else self.placeholder
        color = TEXT_COLOR if self.text else PLACEHOLDER_COLOR
        txt_surf = font_input.render(content, True, color)
        surf.blit(txt_surf, (self.rect.x + 12, self.rect.y + (self.rect.height - txt_surf.get_height()) // 2))

    def get_value(self):
        return self.text.strip()


def draw_button(surf, rect, text, bg_color):
    pygame.draw.rect(surf, bg_color, rect, border_radius=8)
    pygame.draw.rect(surf, (0, 0, 0), rect, 2, border_radius=8)
    txt = font_button.render(text, True, TEXT_COLOR)
    surf.blit(txt, (rect.centerx - txt.get_width() // 2, rect.y + (rect.height - txt.get_height()) // 2))


# Layout
title_y = 80
ip_label_y = 210
input_w, input_h = 360, 44
input_x = (WIDTH - input_w) // 2
input_y = ip_label_y + 28
btn_w, btn_h = 220, 50
start_btn_rect = pygame.Rect((WIDTH - btn_w) // 2, input_y + input_h + 28, btn_w, btn_h)
quit_btn_rect = pygame.Rect((WIDTH - btn_w) // 2, start_btn_rect.bottom + 16, btn_w, btn_h)

ip_box = InputBox(input_x, input_y, input_w, input_h)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_btn_rect.collidepoint(event.pos):
                # UI only for now: just print entered IP and exit
                print(f"Start pressed with IP: '{ip_box.get_value()}'")
                pygame.quit()
                sys.exit()
            if quit_btn_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
        ip_box.handle_event(event)

    # Background
    if bg_img is not None:
        screen.blit(bg_img, (0, 0))
    else:
        screen.fill(BG_COLOR)

    # Title
    title_surface = font_title.render("Tumba-Yola", True, TEXT_COLOR)
    screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, title_y))

    # IP Label and Input
    ip_label = font_label.render("Server IP", True, TEXT_COLOR)
    screen.blit(ip_label, (WIDTH // 2 - ip_label.get_width() // 2, ip_label_y))
    ip_box.draw(screen)

    # Buttons
    draw_button(screen, start_btn_rect, "START", BUTTON_COLOR)
    draw_button(screen, quit_btn_rect, "QUIT", EXIT_COLOR)

    pygame.display.flip()
    clock.tick(60)