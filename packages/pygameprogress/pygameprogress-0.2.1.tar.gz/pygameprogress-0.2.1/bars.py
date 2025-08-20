import pygame
import importlib

def create_bar_surface(width, height, fill_ratio, fill_color, bg_color, border_color):
    surf = pygame.Surface((width, height))
    surf.fill(bg_color)
    fill_width = int(width * fill_ratio)
    for x in range(fill_width):
        for y in range(height):
            if x % 2 == 0 and y % 2 == 0:
                surf.set_at((x, y), fill_color)
    pygame.draw.rect(surf, border_color, (0, 0, width, height), 1)
    return surf

class ProgressBar:
    def __init__(self, x, y, width, height, max_value, color=(0, 255, 0), bg_color=(50, 50, 50)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_value = max_value
        self.current_value = 0
        self.color = color
        self.bg_color = bg_color

    def set_progress(self, value):
        self.current_value = max(0, min(value, self.max_value))

    def draw(self, surface):
        ratio = self.current_value / self.max_value
        bar = create_bar_surface(self.width, self.height, ratio, self.color, self.bg_color, (255, 255, 255))
        surface.blit(bar, (self.x, self.y))

class HealthBar(ProgressBar):
    def __init__(self, x, y, width, height, max_health):
        super().__init__(x, y, width, height, max_health, color=(255, 0, 0))
        self.flash_timer = 0

    def damage(self, amount):
        self.set_progress(self.current_value - amount)
        self.flash_timer = 10

    def heal(self, amount):
        self.set_progress(self.current_value + amount)

    def draw(self, surface):
        if self.flash_timer > 0:
            flash = create_bar_surface(self.width, self.height, 1.0, (255, 255, 255), self.bg_color, (255, 255, 255))
            surface.blit(flash, (self.x, self.y))
            self.flash_timer -= 1
        else:
            ratio = self.current_value / self.max_value
            bar = create_bar_surface(self.width, self.height, ratio, self.color, self.bg_color, (255, 255, 255))
            surface.blit(bar, (self.x, self.y))