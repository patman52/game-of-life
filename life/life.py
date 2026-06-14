"""
Conway's Game of Life implemented in Python using Pygame. 

Author P Tunis
"""


import time
from math import sqrt
from typing import List, Optional, Tuple

import pygame

from . import settings
from .file_dialog_helper import choose_file_save_path, get_file_path
from .grid import Grid, GridType
from .image_to_grid import image_to_grid, load_image

MAX_SCREEN_RATIO = 0.9
PANEL_WIDTH = 200
SMALL_BUTTON_WIDTH = 30
BUTTON_HEIGHT = 30
BUTTON_WIDTH = 160
MED_BUTTON_WIDTH = 80
MIN_GEN_SECONDS = 0.1
MAX_GEN_SECONDS = 1.0

class Life:
    def __init__(self):
        pygame.init()
        self.caption: str = "Conway's Game of Life"
        self.fps: int = 24
        self.seconds_per_generation: float = 0.5
        self.last_generation_time: float = 0.0
        self.clock = pygame.time.Clock()
        self.grid = Grid()
        self._show_grid_lines: bool = True

        self.screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h) 
        self.screen: pygame.Surface = pygame.display.set_mode((self.screen_size[0]*MAX_SCREEN_RATIO, 
                                                               self.screen_size[1]*MAX_SCREEN_RATIO),
                                                              pygame.RESIZABLE)

        self.font_sm = pygame.font.SysFont(None, 22)
        self.font_lg = pygame.font.SysFont(None, 32)
        self._pending_width: int = self.grid.size[0]
        self._pending_height: int = self.grid.size[1]
        self._w_minus_rect = pygame.Rect(0, 0, SMALL_BUTTON_WIDTH, BUTTON_HEIGHT)
        self._w_plus_rect = pygame.Rect(0, 0, SMALL_BUTTON_WIDTH, BUTTON_HEIGHT)
        self._h_minus_rect = pygame.Rect(0, 0, SMALL_BUTTON_WIDTH, BUTTON_HEIGHT)
        self._h_plus_rect = pygame.Rect(0, 0, SMALL_BUTTON_WIDTH, BUTTON_HEIGHT)
        self._resize_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self._bounded_rect = pygame.Rect(0, 0, MED_BUTTON_WIDTH, BUTTON_HEIGHT)
        self._toroidal_rect = pygame.Rect(0, 0, MED_BUTTON_WIDTH, BUTTON_HEIGHT)
        self._save_rect = pygame.Rect(0, 0, MED_BUTTON_WIDTH, BUTTON_HEIGHT)
        self._load_rect = pygame.Rect(0, 0, MED_BUTTON_WIDTH, BUTTON_HEIGHT)
        self._close_image_panel_rect = pygame.Rect(0, 0, SMALL_BUTTON_WIDTH, BUTTON_HEIGHT)

        # image to grid 
        self._image_to_grid_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.show_image_to_grid_panel: bool = False
        self.image: Optional[pygame.Surface] = None
        self.image_grid_values: Optional[List[bool]] = None
        self.image_grid_original_width: int = 0
        self.image_grid_original_height: int = 0
        self.image_grid_width: int = 0
        self.image_grid_height: int = 0
        self.bw_image_preview: Optional[pygame.Surface] = None
        self._grid_preview_minus_rect = pygame.Rect(0, 0, SMALL_BUTTON_WIDTH, BUTTON_HEIGHT)
        self._grid_preview_plus_rect = pygame.Rect(0, 0, SMALL_BUTTON_WIDTH, BUTTON_HEIGHT)
        self.image_grid_preview_scale: float = 1.0
        self._apply_image_scale_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self._apply_image_grid_rect = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)

        self._slider_pressed: bool = False
        self._slider_pos: Optional[int] = None
        self._slider_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._slider_radius: int = 8

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
                # if the size of the grid is small enough, draw a border around each cell
                if self._show_grid_lines:
                    pygame.draw.rect(self.screen, (25, 25, 25), rect, 1)

    def _resize_image_to_grid(self) -> None:
        if self.image is None:
            return
        self.image_grid_width = int(self.image_grid_original_width * self.image_grid_preview_scale)
        self.image_grid_height = int(self.image_grid_original_height * self.image_grid_preview_scale)
        self.image_grid_values, self.bw_image_preview = image_to_grid(self.image, self.image_grid_width, self.image_grid_height)

    def draw_image_to_grid_panel(self) -> None:
        # todo image alignment, exit button, resize button, apply button, etc.
        w = self.screen.get_width() - PANEL_WIDTH
        h = self.screen.get_height() - PANEL_WIDTH
        x = PANEL_WIDTH/2
        panel_x = x + w - PANEL_WIDTH
        y = PANEL_WIDTH/2
        outer_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, (45, 45, 45), outer_rect)
    
        # draw panel
        pygame.draw.rect(self.screen, (80, 80, 80), (panel_x, y, PANEL_WIDTH, h))
        pygame.draw.line(self.screen, (90, 90, 90), (panel_x, y), (panel_x , y + h), 2)
        pygame.draw.rect(self.screen, (0, 0, 0), outer_rect, 5)

        # draw the image and the bw preview side by side
       
        img_w, img_h = self.image.get_size()
        ratio = img_w / img_h
        if img_w > img_h:
            target_w = w/4
            target_h = target_w / ratio
        else:
            target_h = h*.75
            target_w = target_h * ratio
        gap = (w - PANEL_WIDTH - target_w*2) / 3
        original_img_x = x + gap
        original_img_y = y + (h - target_h) / 2
        bw_img_x = original_img_x + target_w + gap
        bw_img_y = original_img_y

        self.screen.blit(pygame.transform.scale(self.image, (int(target_w), int(target_h))), (original_img_x, original_img_y))
        self.screen.blit(pygame.transform.scale(self.bw_image_preview, (int(target_w), int(target_h))), (bw_img_x, bw_img_y))

        # draw labels above the original and bw previews
        original_surf = self.font_sm.render("Original", True, (220, 220, 220))
        bw_surf = self.font_sm.render("Grid Preview", True, (220, 220, 220))
        self._draw_bounded_text(original_surf, pygame.Rect(original_img_x, original_img_y - 30, target_w, 20))
        self._draw_bounded_text(bw_surf, pygame.Rect(bw_img_x, bw_img_y - 30, target_w, 20))

        # draw the current image size underneath the original
        size_text = f"Current Image Size: {img_w} x {img_h}"
        size_surf = self.font_sm.render(size_text, True, (220, 220, 220))
        self._draw_bounded_text(size_surf, pygame.Rect(original_img_x, original_img_y + target_h + 10, target_w, 20))

        # draw the grid preview size underneath the bw preview
        preview_size_text = f"Grid Preview Size: {self.image_grid_width} x {self.image_grid_height}"
        preview_size_surf = self.font_sm.render(preview_size_text, True, (220, 220, 220))
        self._draw_bounded_text(preview_size_surf, pygame.Rect(bw_img_x, bw_img_y + target_h + 10, target_w, 20))

        # draw close button in top right corner of panel 
        self._draw_button(self._close_image_panel_rect, (panel_x + PANEL_WIDTH - 30, y + 10), (200, 50, 50), "X", (255, 255, 255))

        # draw a plus and minus button to adjust the grid preview % size
        gap = (PANEL_WIDTH - SMALL_BUTTON_WIDTH*2) / 3
        self._draw_button(self._grid_preview_minus_rect, (panel_x + gap, y + 60), settings.BTN_BG, "-", settings.TXT_COL)
        self._draw_button(self._grid_preview_plus_rect, (panel_x + PANEL_WIDTH - gap - SMALL_BUTTON_WIDTH, y + 60), settings.BTN_BG, "+", settings.TXT_COL)
        
        # draw label for grid preview size adjustment
        preview_scale_text = f"Grid Preview Scale: {int(self.image_grid_preview_scale*100)}%"
        preview_scale_surf = self.font_sm.render(preview_scale_text, True, (220, 220, 220))
        self._draw_bounded_text(preview_scale_surf, pygame.Rect(panel_x, y + 100, PANEL_WIDTH, 20))

        # draw apply button to set the current grid to the image preview
        apply_col = (55, 110, 55) if not self.playing else (65, 65, 65)
        self._draw_button(self._apply_image_scale_rect, (panel_x + PANEL_WIDTH/2, y + 130), apply_col, "Apply Grid", settings.TXT_COL)

        # draw send to grid button that applies the current preview grid to the main grid, resizing the main grid if necessary
        self._draw_button(self._apply_image_grid_rect, (panel_x + PANEL_WIDTH/2, y + 180), apply_col, "Apply Image as Grid", settings.TXT_COL)

    def _draw_bounded_text(self, bounded_text_surf: pygame.Surface, rect: pygame.Rect) -> None:
        self.screen.blit(bounded_text_surf, (rect.centerx - bounded_text_surf.get_width() // 2,
                                             rect.centery - bounded_text_surf.get_height() // 2))

    def _draw_button(self, 
                     rect: pygame.Rect, 
                     position_size: Tuple[int, int], 
                     bg_color: Tuple[int, int, int], 
                     text: Optional[str] = None,  
                     text_color: Tuple[int, int, int] = (220, 220, 220),
                     justify_x: str = 'c'
        ) -> None:
        x, y = position_size

        if justify_x == 'c':
            x_0 = x - rect.width // 2
        elif justify_x == 'l':
            x_0 = x
        elif justify_x == 'r':
            x_0 = x - rect.width
        else:
            raise ValueError("justify_x must be 'c', 'l', or 'r'")

        rect.topleft = (x_0, y)

        pygame.draw.rect(self.screen, bg_color, rect)
        if text is not None:
            text_surf = self.font_sm.render(text, True, text_color)
            self._draw_bounded_text(text_surf, rect)

    def _determine_point_in_circle(self, point: tuple[float], center: tuple[float], radius: float) -> bool:
        """ 
        finding if a point is in a circle
        (x - center_x)² + (y - center_y)² < radius².
        """
        return sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2) < radius

    def _determine_mouse_over_slider(self, mouse_pos: Tuple[int, int]) -> bool:
        return self._determine_point_in_circle(mouse_pos, (self._slider_pos, self._slider_rect.centery), self._slider_radius)

    def _calculate_slider_ratio(self, new_position: Optional[int] = None) -> float:
        if new_position is not None:
            self._slider_pos = new_position
            # calculate ratio based on slider position
            ratio = (self._slider_pos - self._slider_rect.left) / self._slider_rect.width
            # convert ratio to seconds per generation
            self.seconds_per_generation = MIN_GEN_SECONDS + ratio * (MAX_GEN_SECONDS - MIN_GEN_SECONDS)     
        else:
            ratio = (self.seconds_per_generation - MIN_GEN_SECONDS) / (MAX_GEN_SECONDS - MIN_GEN_SECONDS)
        return ratio

    def _update_slider_position(self, mouse_x: int) -> None:
        self._slider_pos = max(self._slider_rect.left, min(mouse_x, self._slider_rect.right))
        self._calculate_slider_ratio(new_position=self._slider_pos)

    def _draw_slider(self) -> None:
        px = self._grid_area_width()
        ratio = self._calculate_slider_ratio()
        # draw label Generation Speed above the slider
        label_surf = self.font_sm.render("Generation Speed", True, (220, 220, 220))
        self._draw_bounded_text(label_surf, pygame.Rect(px, 570 - 30, PANEL_WIDTH, 20))

        self._slider_pos = int(px + 15 + ratio * (PANEL_WIDTH - 30))
        self._slider_rect = pygame.Rect(px + 15, 570, PANEL_WIDTH - 30, 10)
        pygame.draw.rect(self.screen, (100, 100, 100), self._slider_rect)
        pygame.draw.circle(self.screen, (200, 50, 50), (self._slider_pos, self._slider_rect.centery), self._slider_radius)

        # draw label for slider
        slider_label = f"{self.seconds_per_generation:.1f} seconds/generation"
        slider_label_surf = self.font_sm.render(slider_label, True, (220, 220, 220))
        self._draw_bounded_text(slider_label_surf, pygame.Rect(px, 570 + 10 + 5, PANEL_WIDTH, 20))

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

        # Width row: W: [-] value [+]
        self._draw_button(self._w_minus_rect, (px + 65, 124), settings.BTN_BG, "-", settings.TXT_COL)
        self._draw_button(self._w_plus_rect, (px + 125, 124), settings.BTN_BG, "+", settings.TXT_COL)

        self.screen.blit(self.font_sm.render("W:", True, settings.TXT_COL), (px + 10, 128))
        self.screen.blit(self.font_sm.render(str(self._pending_width), True, settings.TXT_COL), (px + 83, 128))

        # Height row: H: [-] value [+]
        self.screen.blit(self.font_sm.render("H:", True, settings.TXT_COL), (px + 10, 168))
        self._draw_button(self._h_minus_rect, (px + 65, 164), settings.BTN_BG, "-", settings.TXT_COL)
        self._draw_button(self._h_plus_rect, (px + 125, 164), settings.BTN_BG, "+", settings.TXT_COL)
        self.screen.blit(self.font_sm.render(str(self._pending_height), True, settings.TXT_COL), (px + 83, 168))

        # Apply Size button (greyed out while playing)
        apply_col = (55, 110, 55) if not self.playing else (65, 65, 65)
        self._draw_button(self._resize_rect, (px + 100, 210), apply_col, "Apply Size", settings.TXT_COL)
        
        # grid type controls (bounded or toroidal)
        pygame.draw.line(self.screen, (80, 80, 80), (px + 10, 260), (px + PANEL_WIDTH - 10, 260), 1)
        self.screen.blit(self.font_sm.render("Grid Type", True, (160, 160, 160)), (px + 10, 275))
        self._bounded_rect = pygame.Rect(px + 15, 310, 80, 30)
        self._toroidal_rect = pygame.Rect(px + 105, 310, 80, 30)
        pygame.draw.rect(self.screen, settings.SELECTED_BG if self.grid.type == GridType.Bounded else settings.BTN_BG, self._bounded_rect)
        pygame.draw.rect(self.screen, settings.SELECTED_BG if self.grid.type == GridType.Toroidal else settings.BTN_BG, self._toroidal_rect)
        bounded_surf = self.font_sm.render("Bounded", True, settings.TXT_COL)
        toroidal_surf = self.font_sm.render("Toroidal", True, settings.TXT_COL)
        self._draw_bounded_text(bounded_surf, self._bounded_rect)
        self._draw_bounded_text(toroidal_surf, self._toroidal_rect)

        # Save and Load buttons
        pygame.draw.line(self.screen, (80, 80, 80), (px + 10, 360), (px + PANEL_WIDTH - 10, 360), 1)
        self.screen.blit(self.font_sm.render("Save / Load Grid", True, (160, 160, 160)), (px + 10, 375))
        self._draw_button(self._save_rect, (px + 15, 400), settings.BTN_BG, "Save", settings.TXT_COL, justify_x='l')
        self._draw_button(self._load_rect, (px + 105, 400), settings.BTN_BG, "Load", settings.TXT_COL, justify_x='l')

        # image to grid button
        pygame.draw.line(self.screen, (80, 80, 80), (px + 10, 445), (px + PANEL_WIDTH - 10, 445), 1)
        self.screen.blit(self.font_sm.render("Import from Image", True, (160, 160, 160)), (px + 10, 460))
        self._draw_button(self._image_to_grid_rect, (px + 15, 485), settings.BTN_BG, "Image to Grid", settings.TXT_COL, justify_x='l')

        # draw help text at the bottom
        help_text = "Space: Play/Pause | R: Reset | L: Toggle Grid Lines"
        help_surf = self.font_sm.render(help_text, True, (160, 160, 160))
        self._draw_bounded_text(help_surf, pygame.Rect(px/2-PANEL_WIDTH, self.screen.get_height() - 30, px, 20))
        
        pygame.draw.line(self.screen, (80, 80, 80), (px + 10, 525), (px + PANEL_WIDTH - 10, 525), 1)
        self._draw_slider()

    def _save_grid_to_file(self) -> None:
        file_path = choose_file_save_path()
        if file_path:
            self.grid.save_grid(file_path=file_path)
        else:
            print("Save cancelled")
    
    def _load_grid_from_file(self) -> None:
        file_path = get_file_path()
        if file_path:
            self.grid.load_grid(file_path=file_path)
            self._pending_width, self._pending_height = self.grid.size
            self._calculate_cell_size()
        else:
            print("Load cancelled")

    def _load_image_to_grid(self) -> None:
        image_path = get_file_path(file_type='image')
        if image_path:
            self.show_image_to_grid_panel = True
        try:
            self.image = load_image(image_path)
        except Exception as e:
            print(f"Error loading image: {e}")
            self.show_image_to_grid_panel = False
            return
        img_width, img_height = self.image.get_size()
        ratio = img_width / img_height
        # set to max grid size
        if img_width > img_height:
            target_w = min(img_width, settings.MAX_GRID_SIZE)
            target_h = int(target_w / ratio)
        else:
            target_h = min(img_height, settings.MAX_GRID_SIZE)
            target_w = int(target_h * ratio)

        self.image_grid_values, self.bw_image_preview = image_to_grid(self.image, target_w, target_h)
        self.image_grid_original_width = target_w
        self.image_grid_width = target_w
        self.image_grid_original_height = target_h
        self.image_grid_height = target_h

    def _adjust_grid_preview_scale(self, delta: float) -> None:
        new_scale = self.image_grid_preview_scale + delta
        if 0.0 <= new_scale <= 1.0:
            self.image_grid_preview_scale = new_scale

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
                elif event.key == pygame.K_l:
                    self._show_grid_lines = not self._show_grid_lines
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # lock certain UI elements while playing or if the grid has been iterated at least once
                lock_elements = self.playing or self.grid.generation > 0
                mouse_pos = pygame.mouse.get_pos()
                mouse_x, mouse_y = mouse_pos
                if not self.show_image_to_grid_panel:
                    if mouse_x >= self._grid_area_width():
                        if self._w_minus_rect.collidepoint(mouse_pos) and not lock_elements:
                            self._pending_width = max(1, self._pending_width - 1)
                        elif self._w_plus_rect.collidepoint(mouse_pos) and not lock_elements:
                            self._pending_width = min(settings.MAX_GRID_SIZE, self._pending_width + 1)
                        elif self._h_minus_rect.collidepoint(mouse_pos) and not lock_elements:
                            self._pending_height = max(1, self._pending_height - 1)
                        elif self._h_plus_rect.collidepoint(mouse_pos) and not lock_elements:
                            self._pending_height = min(settings.MAX_GRID_SIZE, self._pending_height + 1)
                        elif self._resize_rect.collidepoint(mouse_pos) and not lock_elements:
                            self.grid.resize(self._pending_width, self._pending_height)
                            self._calculate_cell_size()
                        elif self._bounded_rect.collidepoint(mouse_pos) and not lock_elements:
                            self.grid.type = GridType.Bounded
                        elif self._toroidal_rect.collidepoint(mouse_pos) and not lock_elements:
                            self.grid.type = GridType.Toroidal
                        elif self._save_rect.collidepoint(mouse_pos) and not lock_elements:
                            self._save_grid_to_file()
                        elif self._load_rect.collidepoint(mouse_pos) and not lock_elements:
                            self._load_grid_from_file()
                        elif self._image_to_grid_rect.collidepoint(mouse_pos) and not lock_elements:
                            self._load_image_to_grid()
                        # allow for dragging the slider to adjust generation speed, even while playing
                        elif not self._slider_pressed and self._determine_mouse_over_slider(mouse_pos):
                            self._slider_pressed = True
                    else:
                        grid_x = (mouse_x - self.padding_x) // self.cell_size
                        grid_y = (mouse_y - self.padding_y) // self.cell_size
                        if 0 <= grid_x < self.grid.size[0] and 0 <= grid_y < self.grid.size[1]:
                            self.grid.flip_cell(grid_x, grid_y)
                else:
                    if self._close_image_panel_rect.collidepoint(mouse_pos):
                        self.show_image_to_grid_panel = False
                        self.image = None
                        self.bw_image_preview = None
                        self.image_grid_values = None
                    elif self._grid_preview_minus_rect.collidepoint(mouse_pos):
                        self._adjust_grid_preview_scale(-0.1)
                      
                    elif self._grid_preview_plus_rect.collidepoint(mouse_pos):
                        self._adjust_grid_preview_scale(0.1)
                    elif self._apply_image_scale_rect.collidepoint(mouse_pos):
                        self._resize_image_to_grid()
                    elif self._apply_image_grid_rect.collidepoint(mouse_pos):
                        if self.image_grid_values is not None:
                            self.grid.resize(self.image_grid_width, self.image_grid_height, self.image_grid_values)
                            self._calculate_cell_size()
                            self.show_image_to_grid_panel = False
            elif event.type == pygame.MOUSEBUTTONUP:
                if self._slider_pressed:
                    self._slider_pressed = False

            if self._slider_pressed and pygame.mouse.get_pressed()[0]:  # if left mouse button is still held down
                mouse_x, _ = pygame.mouse.get_pos()
                self._update_slider_position(mouse_x)

    def main(self) -> None:
        self.last_generation_time = time.time()
        while True: # main game loop
            self.screen.fill(settings.BACKGROUND_COLOR)
            self.event_loop()
            self.draw_grid()
            self.draw_panel()
            if self.playing:
                if self.grid.all_cells_dead:
                    self.playing = False
                    continue
                current_time = time.time()
                if current_time - self.last_generation_time >= self.seconds_per_generation:
                    self.grid.iterate_generation()
                    self.last_generation_time = current_time

            if self.show_image_to_grid_panel:
                self.draw_image_to_grid_panel()
            pygame.display.flip()
            self.clock.tick(self.fps)
