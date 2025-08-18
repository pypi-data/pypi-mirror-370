import pygame
import os

def load_sprite_sheet(path, frame_width, frame_height):
    image = pygame.image.load(path).convert_alpha()
    sheet_width = image.get_width() // frame_width
    frames = []
    for i in range(sheet_width):
        frame = image.subsurface((i * frame_width, 0, frame_width, frame_height))
        frames.append(frame)
    return frames