"""
Conway's Game of Life implemented in Python using Pygame. 

Author P Tunis
"""


import time
from math import sqrt
from typing import Dict, List, Optional, Tuple

import pygame
pygame.init()

from . import settings
from .button import Button, BUTTON_WIDTH, MED_BUTTON_WIDTH, SMALL_BUTTON_WIDTH, BUTTON_HEIGHT
from .file_dialog_helper import choose_file_save_path, get_file_path
from .grid import Grid, GridType
from .image_to_grid import image_to_grid, load_image

MAX_SCREEN_RATIO = 0.9
PANEL_WIDTH = 200

MIN_GEN_SECONDS = 0.1
MAX_GEN_SECONDS = 1.0


class Life:
    def __init__(self):
        pygame.display.set_caption("Conway's Game of Life")
        self.fps: int = settings.FPS
        self.seconds_per_generation: float = 0.5
        self.last_generation_time: float = 0.0
        self.clock = pygame.time.Clock()
        self.grid = Grid()
        self._show_grid_lines: bool = True

        self.screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h) 
        self.screen: pygame.Surface = pygame.display.set_mode((self.screen_size[0]*MAX_SCREEN_RATIO, 
                                                               self.screen_size[1]*MAX_SCREEN_RATIO),
                                                              pygame.RESIZABLE)

        settings.BASE_PANEL_POS[0] = self.screen.get_width() - PANEL_WIDTH

        self.buttons: Dict[str, Button] = {}
        self.selected_button: Optional[str] = None

        self.font_sm = pygame.font.SysFont(None, 22)
        self.font_lg = pygame.font.SysFont(None, 32)
        self._pending_width: int = self.grid.size[0]
        self._pending_height: int = self.grid.size[1]

        # image to grid 
        self.show_image_to_grid_panel: bool = False
        self.image: Optional[pygame.Surface] = None
        self.image_grid_values: Optional[List[bool]] = None
        self.image_grid_original_width: int = 0
        self.image_grid_original_height: int = 0
        self.image_grid_width: int = 0
        self.image_grid_height: int = 0
        self.bw_image_preview: Optional[pygame.Surface] = None
        self.image_grid_preview_scale: float = 1.0
        self.image_grid_brightness_scale: float = 1.0
        self._image_inverted: bool = False

        self._slider_pressed: bool = False
        self._slider_pos: Optional[int] = None
        self._slider_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._slider_radius: int = 8

        self.playing: bool = False
        self.cell_size: int = 0
        self.padding_x: int = 0
        self.padding_y: float = 0
        self._calculate_cell_size()
        self._setup_buttons()
        self._sync_grid_type_buttons()

    def _setup_buttons(self) -> None:

        button_x = (PANEL_WIDTH - BUTTON_WIDTH)/2
        small_button_x_left = 45
        small_button_x_right = 120

        self.buttons["w_minus"] = Button(
            position=(small_button_x_left, 124),
            width=SMALL_BUTTON_WIDTH,
            screen=self.screen,
            screen_name="main", 
            text="-",
            method=lambda: setattr(self, '_pending_width', max(1, self._pending_width - 1))
        )
        self.buttons["w_plus"] = Button(
            position=(small_button_x_right, 124),
            width=SMALL_BUTTON_WIDTH,
            screen=self.screen,
            screen_name="main",
            text="+",
            method=lambda: setattr(self, '_pending_width', min(settings.MAX_GRID_SIZE, self._pending_width + 1))
        )
        self.buttons["h_minus"] = Button(
            position=(small_button_x_left, 164),
            width=SMALL_BUTTON_WIDTH,
            screen=self.screen,
            screen_name="main",
            text="-",
            method=lambda: setattr(self, '_pending_height', max(1, self._pending_height - 1))
        )
        self.buttons["h_plus"] = Button(
            position=(small_button_x_right, 164),
            width=SMALL_BUTTON_WIDTH,
            screen=self.screen,
            screen_name="main",
            text="+",
            method=lambda: setattr(self, '_pending_height', min(settings.MAX_GRID_SIZE, self._pending_height + 1))
        )
        self.buttons["resize"] = Button(
            position=(button_x, 210),
            screen=self.screen,
            screen_name="main",
            text="Apply Size",
            method=self._resize_grid
        )   
        self.buttons["bounded"] = Button(
            position=(button_x, 310),
            width=MED_BUTTON_WIDTH,
            screen=self.screen,
            screen_name="main",
            text="Bounded",
            method=self._set_bounded_grid_type,
            latch=True,
            activate_on_press=True
        )   
        self.buttons["toroidal"] = Button(
            position=(button_x + 90, 310),
            width=MED_BUTTON_WIDTH,
            screen=self.screen,
            screen_name="main",
            text="Toroidal",
            method=self._set_toroidal_grid_type,
            latch=True,
            activate_on_press=True
        )   
        self.buttons["save"] = Button(
            position=(button_x, 400),
            width=MED_BUTTON_WIDTH,
            screen=self.screen,
            screen_name="main",
            text="Save",
            method=self._save_grid_to_file
        )
        self.buttons["load"] = Button(
            position=(button_x + 90, 400),
            width=MED_BUTTON_WIDTH,
            screen=self.screen,
            screen_name="main",
            text="Load",
            method=self._load_grid_from_file
        )   
        self.buttons["image_to_grid"] = Button(
            position=(button_x, 485),
            width=BUTTON_WIDTH,
            screen=self.screen,
            screen_name="main",
            text="Image to Grid",
            method=self._load_image_to_grid
        )

        self.buttons["close_image_panel"] = Button(
            position=(PANEL_WIDTH - SMALL_BUTTON_WIDTH - 15, 25),
            width=SMALL_BUTTON_WIDTH,
            bg_color=(200, 50, 50),
            screen=self.screen,
            screen_name="image_panel",
            text="X",
            method=lambda: setattr(self, 'show_image_to_grid_panel', False)
        )
        self.buttons["grid_preview_minus"] = Button(
            position=(15, 75),
            width=SMALL_BUTTON_WIDTH,
            screen=self.screen,
            screen_name="image_panel",
            text="-",
            method=lambda: self._adjust_grid_preview_scale(-0.05)
        )
        self.buttons["grid_preview_plus"] = Button(
            position=(PANEL_WIDTH - SMALL_BUTTON_WIDTH - 15, 75),
            width=SMALL_BUTTON_WIDTH,
            screen=self.screen,
            screen_name="image_panel",
            text="+",
            method=lambda: self._adjust_grid_preview_scale(0.05)
        )
        self.buttons["apply_image_scale"] = Button(
            position=(button_x, 140),
            width=BUTTON_WIDTH,
            screen=self.screen,
            screen_name="image_panel",
            text="Apply Scale",
            method=self._resize_image_to_grid
        )

        self.buttons["grid_preview_minus_brightness"] = Button(
            position=(15, 190),
            width=SMALL_BUTTON_WIDTH,
            screen=self.screen,
            screen_name="image_panel",
            text="-",
            method=lambda: self._adjust_grid_preview_brightness(-0.05)
        )
        self.buttons["grid_preview_plus_brightness"] = Button(
            position=(PANEL_WIDTH - SMALL_BUTTON_WIDTH - 15, 190),
            width=SMALL_BUTTON_WIDTH,
            screen=self.screen,
            screen_name="image_panel",
            text="+",
            method=lambda: self._adjust_grid_preview_brightness(0.05)
        )

        self.buttons["apply_image_grid_brightness"] = Button(
            position=(button_x, 260),
            width=BUTTON_WIDTH,
            screen=self.screen,
            screen_name="image_panel",
            text="Apply Brightness",
            method=self._apply_image_grid_brightness
        )

        self.buttons["invert_image"] = Button(
            position=(button_x, 320),
            width=BUTTON_WIDTH,
            screen=self.screen,
            screen_name="image_panel",
            text="Invert Image",
            method=self._invert_image
        )

        self.buttons["apply_image_grid"] = Button(
            position=(button_x, 380),
            width=BUTTON_WIDTH,
            screen=self.screen,
            screen_name="image_panel",
            text="Create Grid",
            method=self._apply_image_grid_as_current_grid
        )

    def _grid_area_width(self) -> int:
        return self.screen.get_width() - PANEL_WIDTH

    def _calculate_cell_size(self) -> None:
        min_y_padding = 30
        grid_width, grid_height = self.grid.size
        grid_area_width = self._grid_area_width()
        grid_area_height = self.screen.get_height() - min_y_padding
        # Divide by (n + 1) so the leftover space is always >= one full cell,
        # i.e. >= half a cell of padding on each side.
        self.cell_size = min(grid_area_width // (grid_width + 1),
                             grid_area_height // (grid_height + 1))
        # Center the grid within the available area.
        self.padding_x = (grid_area_width - self.cell_size * grid_width) // 2
        self.padding_y = (grid_area_height - self.cell_size * grid_height) // 2 + min_y_padding // 2

    def draw_grid(self) -> None:
        for y in range(self.grid.size[1]):
            for x in range(self.grid.size[0]):
                cell = self.grid.get_cell(x, y)
                color = (0, 0, 0) if cell.alive else (200, 200, 200)
                rect = pygame.Rect(x * self.cell_size + self.padding_x, y * self.cell_size + self.padding_y, 
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, rect)
                if self._show_grid_lines:
                    pygame.draw.rect(self.screen, (25, 25, 25), rect, 1)

    def _resize_image_to_grid(self) -> None:
        if self.image is None:
            return
        self.image_grid_width = int(self.image_grid_original_width * self.image_grid_preview_scale)
        self.image_grid_height = int(self.image_grid_original_height * self.image_grid_preview_scale)
        self.image_grid_values, self.bw_image_preview = image_to_grid(
            self.image, self.image_grid_width, self.image_grid_height, invert=self._image_inverted)

    def _draw_bounded_text(self, text: str, color: Tuple[int, int, int], rect: pygame.Rect) -> None:
        bounded_text_surf = self.font_sm.render(text, True, color)
       
        self.screen.blit(bounded_text_surf, (rect.centerx - bounded_text_surf.get_width() // 2,
                                             rect.centery - bounded_text_surf.get_height() // 2))

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
        px = settings.BASE_PANEL_POS[0]
        ratio = self._calculate_slider_ratio()
        # draw label Generation Speed above the slider
        self._draw_bounded_text("Generation Speed", (220, 220, 220), pygame.Rect(px, 570 - 30, PANEL_WIDTH, 20))

        self._slider_pos = int(px + 15 + ratio * (PANEL_WIDTH - 30))
        self._slider_rect = pygame.Rect(px + 15, 570, PANEL_WIDTH - 30, 10)
        pygame.draw.rect(self.screen, (100, 100, 100), self._slider_rect)
        pygame.draw.circle(self.screen, (200, 50, 50), (self._slider_pos, self._slider_rect.centery), self._slider_radius)

        # draw label for slider
        slider_label = f"{self.seconds_per_generation:.1f} seconds/generation"
        self._draw_bounded_text(slider_label, (220, 220, 220), pygame.Rect(px, 570 + 10 + 5, PANEL_WIDTH, 20))

    def draw_buttons(self) -> None:
        for button in self.buttons.values(): 
            # print(f"Drawing button {button.screen_name}, show_image_to_grid_panel={self.show_image_to_grid_panel}")
            if self.show_image_to_grid_panel and button.screen_name == "image_panel":
                button.draw()
            elif not self.show_image_to_grid_panel and button.screen_name == "main":
                button.draw()

    def _draw_image_to_grid_panel(self) -> None:
        """
        Draw the image-to-grid panel, including the original image, the grid preview, and related controls.
        """
        w = self.screen.get_width() - PANEL_WIDTH
        h = self.screen.get_height()

        # draw the image and the bw preview side by side       
        img_w, img_h = self.image.get_size()
        ratio = img_w / img_h
        if img_w > img_h:
            target_w = w/4
            target_h = target_w / ratio
        else:
            target_h = h*.75
            target_w = target_h * ratio
        gap = (w - target_w*2) / 3
        original_img_x = gap
        original_img_y = (h - target_h) / 2
        bw_img_x = original_img_x + target_w + gap
        bw_img_y = original_img_y

        # draw the original and bw images
        self.screen.blit(pygame.transform.scale(self.image, (int(target_w), int(target_h))), (original_img_x, original_img_y))
        self.screen.blit(pygame.transform.scale(self.bw_image_preview, (int(target_w), int(target_h))), (bw_img_x, bw_img_y))

        # draw labels above the original and bw previews
        self._draw_bounded_text("Original", (220, 220, 220), pygame.Rect(original_img_x, original_img_y - 30, target_w, 20))
        self._draw_bounded_text("Grid Preview", (220, 220, 220), pygame.Rect(bw_img_x, bw_img_y - 30, target_w, 20))

        # draw the current image size underneath the original
        size_text = f"Current Image Size: {img_w} x {img_h}"
        self._draw_bounded_text(size_text, (220, 220, 220), pygame.Rect(original_img_x, original_img_y + target_h + 10, target_w, 20))

        # draw the grid preview size underneath the bw preview
        preview_size_text = f"Grid Preview Size: {self.image_grid_width} x {self.image_grid_height}"
        self._draw_bounded_text(preview_size_text, (220, 220, 220), pygame.Rect(bw_img_x, bw_img_y + target_h + 10, target_w, 20))

        # draw a plus and minus button to adjust the grid preview % size
        gap = (PANEL_WIDTH - SMALL_BUTTON_WIDTH*2) / 3

        # draw label for grid preview size adjustment
        preview_scale_text = f"Scale: {int(self.image_grid_preview_scale*100)}%"
        self._draw_bounded_text(preview_scale_text, (220, 220, 220), pygame.Rect(settings.BASE_PANEL_POS[0], 110, PANEL_WIDTH, 20))

        # draw label for grid preview brightness adjustment
        preview_brightness_text = f"Brightness: {int(self.image_grid_brightness_scale*100)}%"
        self._draw_bounded_text(preview_brightness_text, (220, 220, 220), pygame.Rect(settings.BASE_PANEL_POS[0], 230, PANEL_WIDTH, 20))

    def _draw_panel_divider(self, y: int) -> None:
        px = settings.BASE_PANEL_POS[0]
        pygame.draw.line(self.screen, (80, 80, 80), (px + 10, y), (px + PANEL_WIDTH - 10, y), 1)

    def _draw_main_panel(self) -> None:
        settings.BASE_PANEL_POS = (self.screen.get_width() - PANEL_WIDTH, 0)
        px = settings.BASE_PANEL_POS[0]
        # Generation counter
        self.screen.blit(self.font_sm.render("Generation", True, (160, 160, 160)), (px + 10, 15))
        self.screen.blit(self.font_lg.render(str(self.grid.generation), True, (220, 210, 70)), (px + 10, 40))

        self._draw_panel_divider(84)

        # Grid size controls
        self.screen.blit(self.font_sm.render("Grid Size", True, (160, 160, 160)), (px + 10, 95))

        self.screen.blit(self.font_sm.render("W:", True, settings.TXT_COL), (px + 10, 128))
        self.screen.blit(self.font_sm.render(str(self._pending_width), True, settings.TXT_COL), (px + 83, 128))

        # Height row: H: [-] value [+]
        self.screen.blit(self.font_sm.render("H:", True, settings.TXT_COL), (px + 10, 168))
        self.screen.blit(self.font_sm.render(str(self._pending_height), True, settings.TXT_COL), (px + 83, 168))

        # grid type controls (bounded or toroidal)
        self._draw_panel_divider(260)
        self.screen.blit(self.font_sm.render("Grid Type", True, (160, 160, 160)), (px + 10, 275))

        # Save and Load buttons
        self._draw_panel_divider(360)
        self.screen.blit(self.font_sm.render("Save / Load Grid", True, (160, 160, 160)), (px + 10, 375))

        # image to grid button
        self._draw_panel_divider(445)
        self.screen.blit(self.font_sm.render("Import from Image", True, (160, 160, 160)), (px + 10, 460))

        # draw help text at the bottom
        help_text = "Space: Play/Pause | R: Reset | L: Toggle Grid Lines"
        self._draw_bounded_text(help_text, (160, 160, 160), pygame.Rect(settings.BASE_PANEL_POS[0]/2-PANEL_WIDTH, self.screen.get_height() - 25, settings.BASE_PANEL_POS[0], 20))
        
        self._draw_panel_divider(525)
        self._draw_slider()

    def draw_panel(self) -> None:
        """
        Draw the side panel, including the main panel or the image-to-grid panel based on the current state.
        """
        pygame.draw.rect(self.screen, (45, 45, 45), pygame.Rect(settings.BASE_PANEL_POS[0], 0, PANEL_WIDTH, self.screen.get_height()))
        pygame.draw.line(self.screen, (90, 90, 90), (settings.BASE_PANEL_POS[0], 0), (settings.BASE_PANEL_POS[0], self.screen.get_height()), 2)

        if not self.show_image_to_grid_panel:
            self._draw_main_panel()
        else:
            self._draw_image_to_grid_panel()

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
            self._sync_grid_type_buttons()
        else:
            print("Load cancelled")

    def _load_image_to_grid(self) -> None:
        image_path = get_file_path(file_type='image')
        if image_path:
            self.show_image_to_grid_panel = True
            self.screen.fill(settings.BACKGROUND_COLOR)
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
        # normalize to multiple of 0.05 for easier use
        new_scale = round(new_scale / 0.05) * 0.05
        if 0.0 <= new_scale <= 1.0:
            self.image_grid_preview_scale = new_scale

    def _apply_image_grid_as_current_grid(self) -> None:
        if self.image_grid_values is not None:
            self.grid.resize(self.image_grid_width, self.image_grid_height, self.image_grid_values)
            self._calculate_cell_size()
            self.show_image_to_grid_panel = False
            self._image_grid_values = None
            self._bw_image_preview = None
            self.image = None
            self.image_grid_preview_scale: float = 1.0
            self.image_grid_brightness_scale: float = 1.0

    def _adjust_grid_preview_brightness(self, delta: float) -> None:
        if self.bw_image_preview is None:
            return
        new_scale = self.image_grid_brightness_scale + delta
        # normalize to multiple of 0.05 for easier use
        new_scale = round(new_scale / 0.05) * 0.05
        if 0.1 <= new_scale <= 2.0:
            self.image_grid_brightness_scale = new_scale

    def _apply_image_grid_brightness(self) -> None:
        if self.image is None:
            return
        threshold = int(128 / self.image_grid_brightness_scale)  # adjust threshold based on brightness scale
        self.image_grid_values, self.bw_image_preview = image_to_grid(
            self.image, 
            self.image_grid_width, 
            self.image_grid_height, 
            threshold=threshold,
            invert=self._image_inverted
       )

    def _invert_image(self) -> None:
        self._image_inverted = not self._image_inverted
        self.image_grid_values, self.bw_image_preview = image_to_grid(
            self.image, 
            self.image_grid_width, 
            self.image_grid_height, 
            invert=self._image_inverted
        )

    def _sync_grid_type_buttons(self) -> None:
        bounded_button = self.buttons.get("bounded")
        toroidal_button = self.buttons.get("toroidal")
        if bounded_button is None or toroidal_button is None:
            return
        bounded_button._pressed = self.grid.type == GridType.Bounded
        toroidal_button._pressed = self.grid.type == GridType.Toroidal

    def _set_grid_type(self, grid_type: GridType) -> None:
        self.grid.type = grid_type
        self._sync_grid_type_buttons()

    def _set_bounded_grid_type(self) -> None:
        self._set_grid_type(GridType.Bounded)

    def _set_toroidal_grid_type(self) -> None:
        self._set_grid_type(GridType.Toroidal)

    def _resize_grid(self) -> None:
        print(f"Resizing grid to {self._pending_width} x {self._pending_height}")
        self.grid.resize(self._pending_width, self._pending_height)
        self._calculate_cell_size()

    def _flip_buttons_active_state(self) -> None:
        for button in self.buttons.values():
            button.flip_active()

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
                    if self.playing and self.grid.generation == 0:
                        self._flip_buttons_active_state()
                elif event.key == pygame.K_r and not self.playing:
                    if self.grid.generation != 0:
                        self._flip_buttons_active_state()
                    self.grid.reset()   
                elif event.key == pygame.K_l:
                    self._show_grid_lines = not self._show_grid_lines
            elif pygame.mouse.get_pressed()[0]:
                # lock certain UI elements while playing or if the grid has been iterated at least once
                lock_elements = self.playing or self.grid.generation > 0
                mouse_pos = pygame.mouse.get_pos()
                mouse_x, mouse_y = mouse_pos

                if mouse_x < settings.BASE_PANEL_POS[0]:  # only allow interaction with grid if clicking to the left of the panel
                    grid_x = (mouse_x - self.padding_x) // self.cell_size
                    grid_y = (mouse_y - self.padding_y) // self.cell_size
                    if 0 <= grid_x < self.grid.size[0] and 0 <= grid_y < self.grid.size[1]:
                        self.grid.flip_cell(grid_x, grid_y)
                else:
                    for button_name, button in self.buttons.items():
                        if self.show_image_to_grid_panel and button.screen_name != "image_panel":
                            continue
                        elif not self.show_image_to_grid_panel and button.screen_name != "main":
                            continue
                        
                        if button.lock_while_playing and lock_elements:
                            continue

                        if button.collide(mouse_pos):
                            button.press()
                            self.selected_button = button_name
                            break  # only allow one button press per click

                if self._slider_pressed:
                    self._update_slider_position(mouse_x)
                elif not self._slider_pressed and self._determine_mouse_over_slider(mouse_pos):
                    self._slider_pressed = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if self._slider_pressed:
                    self._slider_pressed = False
                if self.selected_button is not None:
                    button = self.buttons[self.selected_button]
                    # check if the mouse is still over the button on release, and if so, execute its method
                    if button.collide(pygame.mouse.get_pos()) and not button.activate_on_press:
                        button.run_method()

                    button.release()  # reset button state if mouse released off the button
                    self.selected_button = None

    def main(self) -> None:
        self.last_generation_time = time.time()
        while True: # main game loop
            self.screen.fill(settings.BACKGROUND_COLOR)
            self.event_loop()

            if not self.show_image_to_grid_panel:
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

            self.draw_buttons()
            pygame.display.flip()
            self.clock.tick(self.fps)
