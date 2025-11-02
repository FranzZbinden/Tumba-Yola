import pygame
import sys
import button as btn

pygame.init()

WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix of Buttons")

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

BUTTON_WIDTH, BUTTON_HEIGHT = 100, 100
ROWS, COLS = 3, 3
DIVIDER = 10


# Create grid of buttons
buttons = []
for vertical_index in range(ROWS):
    row = []
    for horizontal_index in range(COLS):
        x = horizontal_index * (BUTTON_WIDTH + DIVIDER) # x, y = cordinates in pixels
        y = vertical_index * (BUTTON_HEIGHT + DIVIDER) 
        row.append(btn.Button(vertical_index, horizontal_index, x, y, BUTTON_WIDTH, BUTTON_HEIGHT)) 
    buttons.append(row)

# (T0-DO) def running():
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for row in buttons:
                for button in row:
                    if button.is_clicked(event.pos):
                        print(f"Button {button.index} clicked") # return the 2d index

    for row in buttons:
        for button in row:
            button.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
