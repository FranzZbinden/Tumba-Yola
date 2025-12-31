import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix Grid Visualization")

# Matrix and grid settings
matrix = [
    [0, 1, 0],
    [1, 0, 1],
    [0, 1, 0]
]
rows, cols = len(matrix), len(matrix[0])
cell_size = WIDTH // cols

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    # Draw the grid
    for row in range(rows):
        for col in range(cols):
            color = BLUE if matrix[row][col] == 1 else BLACK
            pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size))
            pygame.draw.rect(screen, WHITE, (col * cell_size, row * cell_size, cell_size, cell_size), 1)  # Grid lines

    pygame.display.flip()

pygame.quit()