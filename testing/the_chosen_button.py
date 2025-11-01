import pygame
import sys

#Initialize Pygame
pygame.init()

#Screen dimensions
WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix of Buttons")
MIDDLE = 1

#Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

#Button dimensions
BUTTON_WIDTH, BUTTON_HEIGHT = 100, 100
ROWS, COLS = 3, 3  # Matrix size (4x5)
DIVIDER = 10

#Create a matrix of button positions
buttons = []
for row in range(ROWS):
    button_row = []
    for col in range(COLS):
        x = col * (BUTTON_WIDTH + DIVIDER) + 200
        y = row * (BUTTON_HEIGHT + DIVIDER) + 170
        button_row.append(pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT))
    buttons.append(button_row)

# Main loop
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for row in buttons:
                for button in row:
                    if button.collidepoint(event.pos):
                        print(f"Button at {button.topleft} clicked!")

    # Draw buttons
    for row in buttons:
        for button in row:
            pygame.draw.rect(screen, GRAY, button)
            pygame.draw.rect(screen, BLACK, button, 2)  # Border

    pygame.display.flip()

pygame.quit()
sys.exit()