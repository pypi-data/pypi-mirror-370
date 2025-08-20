import pygame
import pygame
import os

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

def create_sprite():
    pygame.init()
    grid_size = 64
    scale = 8
    palette_height = 40
    screen = pygame.display.set_mode((grid_size * scale, grid_size * scale + palette_height))
    pygame.display.set_caption("Sprite Editor")
    clock = pygame.time.Clock()

    pixels = [[(0, 0, 0, 0) for _ in range(grid_size)] for _ in range(grid_size)]
    current_color = (255, 255, 255)
    sprite_name = "default"

    palette = [
        (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0),
        (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)
    ]

    def draw_palette():
        for i, color in enumerate(palette):
            rect = pygame.Rect(i * 40, grid_size * scale, 40, palette_height)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, 2)

    def save_sprite(name):
        os.makedirs("sprites", exist_ok=True)
        surf = pygame.Surface((grid_size, grid_size), pygame.SRCALPHA)
        for y in range(grid_size):
            for x in range(grid_size):
                surf.set_at((x, y), pixels[y][x])
        pygame.image.save(surf, f"sprites/{name}.png")
        print(f"✅ Saved to sprites/{name}.png")

    def load_sprite(name):
        path = f"sprites/{name}.png"
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            for y in range(grid_size):
                for x in range(grid_size):
                    pixels[y][x] = img.get_at((x, y))
            print(f"📂 Loaded sprites/{name}.png")
        else:
            print(f"⚠️ File not found: {path}")

    running = True
    while running:
        screen.fill((30, 30, 30))
        for y in range(grid_size):
            for x in range(grid_size):
                color = pixels[y][x]
                if color[3] > 0:
                    pygame.draw.rect(screen, color, (x * scale, y * scale, scale, scale))

        draw_palette()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_sprite(sprite_name)
                elif event.key == pygame.K_l:
                    load_sprite(sprite_name)
                elif event.key == pygame.K_n:
                    sprite_name = input("📝 Enter sprite name: ")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if my < grid_size * scale:
                    gx, gy = mx // scale, my // scale
                    if 0 <= gx < grid_size and 0 <= gy < grid_size:
                        if event.button == 1:
                            pixels[gy][gx] = current_color + (255,)
                        elif event.button == 3:
                            pixels[gy][gx] = (0, 0, 0, 0)
                else:
                    index = mx // 40
                    if 0 <= index < len(palette):
                        current_color = palette[index]
                        print(f"🎨 Selected color: {current_color}")

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def custom_sprite(name="default", size=32):
    path = f"sprites/{name}.png"
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found. Run create_sprite() and save it first.")
    raw = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(raw, (size, size))