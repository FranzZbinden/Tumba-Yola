import pygame
import sys

# Initialize PyGame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyGame Button Example")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

# Button properties
btn = pygame.Rect(300, 250, 200, 50)  # x, y, width, height
font = pygame.font.Font(None, 36)
btn_txt = font.render("Click Me!", True, WHITE)

# Main loop
running = True
while running:
    screen.fill(GRAY)

    # Draw button
    pygame.draw.rect(screen, BLUE, btn)
    screen.blit(btn_txt, (btn.x + 50, btn.y + 10))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if btn.collidepoint(event.pos):
                print("Button clicked!")

    pygame.display.flip()

pygame.quit()
sys.exit()