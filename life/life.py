import time
from typing import Tuple

import pygame

from . import settings
from .grid import Grid

MAX_SCREEN_RATIO = 0.9
PANEL_WIDTH = 200

class Life:
    def __init__(self):
        pygame.init()
        self.caption: str = "Conway's Game of Life"
        self.fps: int = 24
        self.seconds_per_generation: float = 0.5
        self.last_generation_time: float = 0.0
        self.clock = pygame.time.Clock()
        self.grid = Grid()

        self.screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h) 
        self.screen: pygame.Surface = pygame.display.set_mode((self.screen_size[0]*MAX_SCREEN_RATIO, 
                                                               self.screen_size[1]*MAX_SCREEN_RATIO),
                                                              pygame.RESIZABLE)

        self.font_sm = pygame.font.SysFont(None, 22)
        self.font_lg = pygame.font.SysFont(None, 32)
        self._pending_width: int = self.grid.size[0]
        self._pending_height: int = self.grid.size[1]
        self._w_minus_rect = pygame.Rect(0, 0, 0, 0)
        self._w_plus_rect = pygame.Rect(0, 0, 0, 0)
        self._h_minus_rect = pygame.Rect(0, 0, 0, 0)
        self._h_plus_rect = pygame.Rect(0, 0, 0, 0)
        self._resize_rect = pygame.Rect(0, 0, 0, 0)
        self.playing: bool = False
        self.cell_size: int = 0
        self.padding_x: int = 0
        self.padding_y: float = 0
        self._calculate_cell_size()


    def _grid_area_width(self) -> int:
        return self.screen.get_width() - PANEL_WIDTH

    def _calculate_cell_size(self) -> None:
        grid_width, grid_height = self.grid.size
        grid_area_width = self._grid_area_width()
        grid_area_height = self.screen.get_height()
        # Divide by (n + 1) so the leftover space is always >= one full cell,
        # i.e. >= half a cell of padding on each side.
        self.cell_size = min(grid_area_width // (grid_width + 1),
                             grid_area_height // (grid_height + 1))
        # Center the grid within the available area.
        self.padding_x = (grid_area_width - self.cell_size * grid_width) // 2
        self.padding_y = (grid_area_height - self.cell_size * grid_height) // 2

    def draw_grid(self) -> None:
        for y in range(self.grid.size[1]):
            for x in range(self.grid.size[0]):
                cell = self.grid.get_cell(x, y)
                color = (0, 0, 0) if cell.alive else (200, 200, 200)
                rect = pygame.Rect(x * self.cell_size + self.padding_x, y * self.cell_size + self.padding_y, 
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def draw_panel(self) -> None:
        px = self._grid_area_width()
        pygame.draw.rect(self.screen, (45, 45, 45), pygame.Rect(px, 0, PANEL_WIDTH, self.screen.get_height()))
        pygame.draw.line(self.screen, (90, 90, 90), (px, 0), (px, self.screen.get_height()), 2)

        # Generation counter
        self.screen.blit(self.font_sm.render("Generation", True, (160, 160, 160)), (px + 10, 15))
        self.screen.blit(self.font_lg.render(str(self.grid.generation), True, (220, 210, 70)), (px + 10, 40))

        pygame.draw.line(self.screen, (80, 80, 80), (px + 10, 84), (px + PANEL_WIDTH - 10, 84), 1)

        # Grid size controls
        self.screen.blit(self.font_sm.render("Grid Size", True, (160, 160, 160)), (px + 10, 95))

        btn_bg = (85, 85, 85)
        txt_col = (220, 220, 220)

        # Width row: W: [-] value [+]
        self.screen.blit(self.font_sm.render("W:", True, txt_col), (px + 10, 128))
        self._w_minus_rect = pygame.Rect(px + 52, 124, 26, 26)
        self._w_plus_rect = pygame.Rect(px + 112, 124, 26, 26)
        pygame.draw.rect(self.screen, btn_bg, self._w_minus_rect)
        pygame.draw.rect(self.screen, btn_bg, self._w_plus_rect)
        minus_surf = self.font_sm.render("-", True, txt_col)
        plus_surf = self.font_sm.render("+", True, txt_col)
        self.screen.blit(minus_surf, (self._w_minus_rect.centerx - minus_surf.get_width() // 2,
                                      self._w_minus_rect.centery - minus_surf.get_height() // 2))
        self.screen.blit(plus_surf, (self._w_plus_rect.centerx - plus_surf.get_width() // 2,
                                     self._w_plus_rect.centery - plus_surf.get_height() // 2))
        self.screen.blit(self.font_sm.render(str(self._pending_width), True, txt_col), (px + 83, 128))

        # Height row: H: [-] value [+]
        self.screen.blit(self.font_sm.render("H:", True, txt_col), (px + 10, 168))
        self._h_minus_rect = pygame.Rect(px + 52, 164, 26, 26)
        self._h_plus_rect = pygame.Rect(px + 112, 164, 26, 26)
        pygame.draw.rect(self.screen, btn_bg, self._h_minus_rect)
        pygame.draw.rect(self.screen, btn_bg, self._h_plus_rect)
        self.screen.blit(minus_surf, (self._h_minus_rect.centerx - minus_surf.get_width() // 2,
                                      self._h_minus_rect.centery - minus_surf.get_height() // 2))
        self.screen.blit(plus_surf, (self._h_plus_rect.centerx - plus_surf.get_width() // 2,
                                     self._h_plus_rect.centery - plus_surf.get_height() // 2))
        self.screen.blit(self.font_sm.render(str(self._pending_height), True, txt_col), (px + 83, 168))

        # Apply Size button (greyed out while playing)
        apply_col = (55, 110, 55) if not self.playing else (65, 65, 65)
        self._resize_rect = pygame.Rect(px + 15, 210, 170, 34)
        pygame.draw.rect(self.screen, apply_col, self._resize_rect)
        apply_surf = self.font_sm.render("Apply Size", True, txt_col)
        self.screen.blit(apply_surf, (self._resize_rect.centerx - apply_surf.get_width() // 2,
                                      self._resize_rect.centery - apply_surf.get_height() // 2))

    def event_loop(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.VIDEORESIZE:
                self._calculate_cell_size()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.playing = not self.playing
                elif event.key == pygame.K_r and not self.playing:
                    self.grid.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.playing or self.grid.generation > 0:
                    return
                mouse_pos = pygame.mouse.get_pos()
                mouse_x, mouse_y = mouse_pos
                if mouse_x >= self._grid_area_width():
                    if self._w_minus_rect.collidepoint(mouse_pos):
                        self._pending_width = max(1, self._pending_width - 1)
                    elif self._w_plus_rect.collidepoint(mouse_pos):
                        self._pending_width = min(settings.MAX_GRID_SIZE, self._pending_width + 1)
                    elif self._h_minus_rect.collidepoint(mouse_pos):
                        self._pending_height = max(1, self._pending_height - 1)
                    elif self._h_plus_rect.collidepoint(mouse_pos):
                        self._pending_height = min(settings.MAX_GRID_SIZE, self._pending_height + 1)
                    elif self._resize_rect.collidepoint(mouse_pos):
                        self.grid.resize(self._pending_width, self._pending_height)
                        self._calculate_cell_size()
                else:
                    grid_x = (mouse_x - self.padding_x) // self.cell_size
                    grid_y = (mouse_y - self.padding_y) // self.cell_size
                    if 0 <= grid_x < self.grid.size[0] and 0 <= grid_y < self.grid.size[1]:
                        self.grid.flip_cell(grid_x, grid_y)

    def main(self) -> None:
        self.last_generation_time = time.time()
        while True: # main game loop
            self.screen.fill(settings.BACKGROUND_COLOR)
            self.event_loop()
            self.draw_grid()
            self.draw_panel()
            pygame.display.flip()
            if self.playing:
                if self.grid.all_cells_dead:
                    self.playing = False
                    continue
                current_time = time.time()
                if current_time - self.last_generation_time >= self.seconds_per_generation:
                    self.grid.iterate_generation()
                    self.last_generation_time = current_time
            self.clock.tick(self.fps)
