
from typing import Optional, Tuple

import pygame

from . import settings

SMALL_BUTTON_WIDTH = 30
BUTTON_HEIGHT = 30
BUTTON_WIDTH = 160
MED_BUTTON_WIDTH = 80

class Button:
    def __init__(self, 
                 screen: pygame.Surface,
                 screen_name: str,
                 position: Tuple[int, int],
                 width: int = BUTTON_WIDTH,
                 height: int = BUTTON_HEIGHT,
                 method: Optional[callable] = None,
                 bg_color: Tuple[int, int, int] = settings.BTN_BG, 
                 pressed_color: Tuple[int, int, int] = settings.SELECTED_BG, 
                 deactivated_color: Tuple[int, int, int] = settings.DEACTIVATED_BG,
                 text: Optional[str] = None, 
                 text_color: Tuple[int, int, int] = (220, 220, 220),
                 font: Optional[pygame.font.Font] = pygame.font.SysFont(None, 22),
                 activate_on_press: bool = False,
                 latch: bool = False,
                 lock_while_playing: bool = True,
                 border_radius: int = 5
        ):
        self.rect: pygame.Rect = pygame.Rect(position, (width, height))
        self.screen: pygame.Surface = screen
        self.screen_name: str = screen_name
        self.bg_color: Tuple[int, int, int] = bg_color
        self.pressed_color: Tuple[int, int, int] = pressed_color
        self.deactivated_color: Tuple[int, int, int] = deactivated_color
        self.text: Optional[str] = text
        self.text_color: Tuple[int, int, int] = text_color
        self.font: Optional[pygame.font.Font] = font
        self.method: Optional[callable] = method
        self.activate_on_press: bool = activate_on_press
        self._latch: bool = latch
        self._pressed: bool = False
        self.lock_while_playing: bool = lock_while_playing
        self._active: bool = True
        self.border_radius: int = border_radius

    @property
    def pressed(self) -> bool:
        return self._pressed
    
    def press(self) -> None:
        if not self._active:
            return
        self._pressed = True
        if self.activate_on_press and self.method is not None:
            self.method()

    def release(self) -> None:
        if not self._active:
            return
        if not self._latch:
            self._pressed = False

    def flip_active(self) -> None:
        self._active = not self._active

    def run_method(self) -> None:
        if not self._active:
            return
        if self.method is not None:
            self.method()

    def update(self, x: Optional[int] = None, y: Optional[int] = None, w: Optional[int] = None, h: Optional[int] = None) -> None:
        if x is not None:
            self.rect.x = x
        if y is not None:
            self.rect.y = y
        if w is not None:
            self.rect.width = w
        if h is not None:
            self.rect.height = h
    
    def draw(self) -> None:
        if not self._active:
            color = self.deactivated_color
        else:
            color = self.pressed_color if self._pressed else self.bg_color
        pygame.draw.rect(self.screen, color, self.rect, border_radius=self.border_radius)
        if self.text is not None:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            self.screen.blit(text_surf, text_rect)

    def collide(self, mouse_pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_pos)
    

__all__ = [
    "Button",
    "SMALL_BUTTON_WIDTH",
    "BUTTON_HEIGHT",
    "BUTTON_WIDTH",
    "MED_BUTTON_WIDTH",
]
