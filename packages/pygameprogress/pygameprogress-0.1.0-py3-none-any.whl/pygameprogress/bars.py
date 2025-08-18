import pygame

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
    def __init__(self, x, y, width, height, max_value):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.current_value = max_value

    def update(self, value):
        self.current_value = max(0, min(value, self.max_value))

    def draw(self, surface):
        ratio = self.current_value / self.max_value
        bar = create_bar_surface(self.rect.width, self.rect.height, ratio, (0, 255, 0), (30, 30, 30), (80, 80, 80))
        surface.blit(bar, self.rect.topleft)

class HealthBar(ProgressBar):
    def __init__(self, x, y, width, height, max_health):
        super().__init__(x, y, width, height, max_health)
        self.flash_timer = 0

    def damage(self, amount):
        self.update(self.current_value - amount)
        self.flash_timer = 10

    def heal(self, amount):
        self.update(self.current_value + amount)

    def draw(self, surface):
        if self.flash_timer > 0:
            flash = create_bar_surface(self.rect.width, self.rect.height, 1.0, (255, 255, 255), (30, 30, 30), (80, 80, 80))
            surface.blit(flash, self.rect.topleft)
            self.flash_timer -= 1
        else:
            ratio = self.current_value / self.max_value
            bar = create_bar_surface(self.rect.width, self.rect.height, ratio, (255, 0, 0), (30, 30, 30), (80, 80, 80))
            surface.blit(bar, self.rect.topleft)