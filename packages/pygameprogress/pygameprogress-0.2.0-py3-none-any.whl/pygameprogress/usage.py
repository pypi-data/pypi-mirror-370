import pygame
from pygameprogress import ProgressBar

pygame.init()
screen = pygame.display.set_mode((400, 300))
clock = pygame.time.Clock()

bar = ProgressBar(x=50, y=100, width=300, height=30, color=(0, 255, 0))

progress = 0.0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    progress = min(progress + 0.005, 1.0)
    bar.set_progress(progress)

    screen.fill((30, 30, 30))
    bar.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()