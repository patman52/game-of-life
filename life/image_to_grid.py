
from typing import List, Tuple

import pygame


def image_to_grid(img: pygame.Surface, width: int, height: int, threshold: int = 128) -> Tuple[List[bool], pygame.Surface]:
    
    img = pygame.transform.scale(img, (width, height))
    bw = img.convert()  # ensure consistent pixel format

    result = []
    for y in range(height):
        for x in range(width):
            r, g, b, *_ = bw.get_at((x, y))
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            color = (0, 0, 0) if luminance < threshold else (255, 255, 255)
            bw.set_at((x, y), color)
            result.append(luminance < threshold)  # dark = True (alive), light = False (dead)
    return result, bw


def load_image(path: str) -> pygame.Surface:
    img = pygame.image.load(path)
    return img

__all__ = [
    "image_to_grid",
    "load_image",
]
