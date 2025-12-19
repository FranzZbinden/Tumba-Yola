import pygame
import sys
import os
import subprocess
from pathlib import Path

pygame.init()

# Window
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TumbaYola - Start Screen")
clock = pygame.time.Clock()

try:
    # Get project root (parent of Utilities folder)
    project_root = Path(__file__).parent.parent
    bg_path = project_root / "sprites" / "start_scr_img.png"
    bg_img = pygame.image.load(str(bg_path)).convert()
    bg_img = pygame.transform.smoothscale(bg_img, (WIDTH, HEIGHT))
except Exception:
    bg_img = None  # fallback to solid color if image missing

# Colors
BG_COLOR = (30, 61, 89)
BUTTON_COLOR = (245, 166, 35)
EXIT_COLOR = (231, 76, 60)
TEXT_COLOR = (255, 255, 255)
TEXT_COLOR_INPUT = (25, 25, 25)
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
        color = TEXT_COLOR_INPUT if self.text else PLACEHOLDER_COLOR
        txt_surf = font_input.render(content, True, color)
        surf.blit(txt_surf, (self.rect.x + 12, self.rect.y + (self.rect.height - txt_surf.get_height()) // 2))

    def get_value(self):
        return self.text.strip()


def draw_button(surf, rect, text, bg_color):
    pygame.draw.rect(surf, bg_color, rect, border_radius=8)
    pygame.draw.rect(surf, (0, 0, 0), rect, 2, border_radius=8)
    txt = font_button.render(text, True, TEXT_COLOR)
    surf.blit(txt, (rect.centerx - txt.get_width() // 2, rect.y + (rect.height - txt.get_height()) // 2))


# Inline bottom layout configuration
input_w, input_h = 360, 44
btn_w, btn_h = 220, 50

# Spacing
gap_input_start = 24
gap_between_buttons = 16
margin_bottom = 60

# Prepare UI objects
ip_box = InputBox(0, 0, input_w, input_h)
start_btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
quit_btn_rect = pygame.Rect(0, 0, btn_w, btn_h)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_btn_rect.collidepoint(event.pos):
                typed = ip_box.get_value()
                if not typed:
                    print("Please enter a server IP.")
                else:
                    host = typed.strip()
                    project_root = Path(__file__).parent.parent
                    subprocess.Popen([sys.executable, "client.py", host], cwd=project_root)
                    pygame.quit()
                    sys.exit()
            if quit_btn_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
        ip_box.handle_event(event)

    # Compute dynamic positions each frame (center the whole bottom row)
    group_height = btn_h
    y = HEIGHT - margin_bottom - group_height
    group_width = input_w + gap_input_start + btn_w + gap_between_buttons + btn_w
    x0 = (WIDTH - group_width) // 2

    # Positions
    input_x = x0
    input_y = y + (btn_h - input_h) // 2

    start_x = input_x + input_w + gap_input_start
    start_y = y

    quit_x = start_x + btn_w + gap_between_buttons
    quit_y = y

    # Update rects
    ip_box.rect.x, ip_box.rect.y = input_x, input_y
    start_btn_rect.x, start_btn_rect.y = start_x, start_y
    quit_btn_rect.x, quit_btn_rect.y = quit_x, quit_y

    # Background
    if bg_img is not None:
        screen.blit(bg_img, (0, 0))
    else:
        screen.fill(BG_COLOR)

    # Draw inline bottom row: input + buttons
    ip_box.draw(screen)
    draw_button(screen, start_btn_rect, "START", BUTTON_COLOR)
    draw_button(screen, quit_btn_rect, "QUIT", EXIT_COLOR)

    pygame.display.flip()
    clock.tick(60)