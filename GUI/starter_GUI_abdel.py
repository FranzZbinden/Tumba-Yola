import pygame
import subprocess
import sys

pygame.init()

# Screen
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TumbaYola - Start Screen")

# Colors
BG_COLOR = (30, 61, 89)
BUTTON_COLOR = (245, 166, 35)
EXIT_COLOR = (231, 76, 60)
TEXT_COLOR = (255, 255, 255)

# Fonts
font_title = pygame.font.SysFont("arialblack", 50)
font_button = pygame.font.SysFont("arial", 30)

# Buttons
start_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 50)
exit_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50)

running = True
while running:
    screen.fill(BG_COLOR)

    # Screen title
    title_surface = font_title.render("TumbaYola", True, TEXT_COLOR)
    screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, 100))

    
    pygame.draw.rect(screen, BUTTON_COLOR, start_button)
    pygame.draw.rect(screen, EXIT_COLOR, exit_button)


    start_text = font_button.render("Start Game", True, TEXT_COLOR)
    exit_text = font_button.render("Exit", True, TEXT_COLOR)
    screen.blit(start_text, (start_button.x + 40, start_button.y + 10))
    screen.blit(exit_text, (exit_button.x + 75, exit_button.y + 10))

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                # pygame.quit()
                # (TO-DO) method start method call the method in client vvvvvvvv
                subprocess.Popen(["python", "GUI_matrix.py"])
                sys.exit()

            if exit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

    pygame.display.flip()