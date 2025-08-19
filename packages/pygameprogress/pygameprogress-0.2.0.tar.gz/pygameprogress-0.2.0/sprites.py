import pygame

def load_player_sprite():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.rect(surf, (255, 220, 180), (10, 4, 12, 12))  # Head

    pygame.draw.rect(surf, (100, 200, 100), (10, 16, 12, 12))  # Body

    pygame.draw.rect(surf, (60, 60, 60), (8, 28, 6, 4))        # Left leg

    pygame.draw.rect(surf, (60, 60, 60), (18, 28, 6, 4))       # Right leg

    return surf

def load_sprite_sheet(path, frame_width, frame_height):
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    for i in range(sheet.get_width() // frame_width):
        frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
        frames.append(frame)
    return frames