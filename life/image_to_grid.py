"""
Helper functions to convert images to grid data for Conway's Game of Life.

Author: P Tunis
"""

from typing import List, Tuple

import pygame


def image_to_grid(
        img: pygame.Surface, 
        width: int, 
        height: int, 
        threshold: int = 128, 
        invert: bool = False
    ) -> Tuple[List[bool], pygame.Surface]:
    """
    Convert a pygame Surface image to a grid of boolean values representing alive and dead cells.

    Args:
        img (pygame.Surface): The original input image.
        width (int): The width of the output grid.
        height (int): The height of the output grid.
        threshold (int, optional): The luminance threshold to determine alive/dead cells. Defaults to 128. 
                                   Less than this value is considered dark (alive), greater is considered light (dead).
        invert (bool, optional): If True, invert the alive/dead mapping. Defaults to False.

    Returns:
        Tuple[List[bool], pygame.Surface]: A tuple containing the grid of boolean values and the processed image.
    """

    img = pygame.transform.scale(img, (width, height))
    bw = img.convert()  # ensure consistent pixel format

    result = []
    for y in range(height):
        for x in range(width):
            r, g, b, *_ = bw.get_at((x, y))
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            if invert:
                result.append(luminance >= threshold)  # dark = False (dead), light = True (alive)
                color = (0, 0, 0) if luminance >= threshold else (255, 255, 255)
            else:
                result.append(luminance < threshold)  # dark = True (alive), light = False (dead)
                color = (0, 0, 0) if luminance < threshold else (255, 255, 255)

            bw.set_at((x, y), color)

    return result, bw


def load_image(path: str) -> pygame.Surface:
    """
    Load an image from the specified file path as a pygame Surface.

    Args:
        path (str): The file path to the image.

    Returns:
        pygame.Surface: The loaded image as a pygame Surface.
    """
    img = pygame.image.load(path)
    return img

__all__ = [
    "image_to_grid",
    "load_image",
]
