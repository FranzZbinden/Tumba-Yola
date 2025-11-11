import pygame
import sys
import subprocess
import time

pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Waiting...")

font = pygame.font.SysFont("arial", 36)
BG_COLOR = (30, 61, 89)
TEXT_COLOR = (255, 255, 255)

clock = pygame.time.Clock()
angle = 0
loading_img = pygame.Surface((60, 60), pygame.SRCALPHA)
pygame.draw.circle(loading_img, (245, 166, 35), (30, 30), 25, 5)

start_time = time.time()
username = sys.argv[1] if len(sys.argv) > 1 else "Player"

while True:
    screen.fill(BG_COLOR)
    text = font.render("Waiting for one player...", True, TEXT_COLOR)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100))

    # Loading icon (rotating circle)
    rotated = pygame.transform.rotate(loading_img, angle)
    rect = rotated.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
    screen.blit(rotated, rect)
    angle = (angle + 5) % 360

    # Simular espera de 5 segundos
    if time.time() - start_time > 5:
        pygame.quit()
        subprocess.Popen(["python", "client.py", username])
        sys.exit()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.flip()
    clock.tick(30)