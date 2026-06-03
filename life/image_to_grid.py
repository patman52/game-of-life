
from typing import List

import pygame


def image_to_grid(img: pygame.Surface, width: int, height: int) -> List[bool]:
    
    img = pygame.transform.scale(img, (width, height))
    img = img.convert()  # ensure consistent pixel format

    result = []
    for y in range(height):
        for x in range(width):
            r, g, b, *_ = img.get_at((x, y))
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            result.append(luminance < 128)  # dark = True (alive), light = False (dead)
    return result


def load_image(path: str) -> pygame.Surface:
    img = pygame.image.load(path)
    return img

