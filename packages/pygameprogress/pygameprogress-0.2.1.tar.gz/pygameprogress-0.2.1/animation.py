import pygame

def generate_pixel_frame(color):
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    # Head
    pygame.draw.rect(surf, color, (12, 4, 8, 8))
    # Body
    pygame.draw.rect(surf, (color[0]//2, color[1]//2, color[2]//2), (12, 12, 8, 12))
    # Legs
    pygame.draw.rect(surf, color, (10, 24, 4, 6))
    pygame.draw.rect(surf, color, (18, 24, 4, 6))
    return surf

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, frame_width, frame_height, num_frames, fps=10):
        super().__init__()
        self.frames = [generate_pixel_frame((100 + i*30, 200 - i*20, 100 + i*10)) for i in range(num_frames)]
        self.index = 0
        self.fps = fps
        self.timer = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()

    def update(self):
        self.timer += 1
        if self.timer >= (60 // self.fps):
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]
            self.timer = 0