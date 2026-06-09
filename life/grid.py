

import os
import pickle
from enum import Enum
from typing import Dict, List, Optional, Tuple

from . import settings


class GridType(Enum):
    Bounded = 1
    Toroidal = 2


class Cell:
    _alive = False

    @property
    def alive(self) -> bool:
        return self._alive

    def flip(self):
        self._alive = not self._alive


class Grid:
    def __init__(self):
        self._width: int = settings.DEFAULT_GRID_CONFIGURATION["SIZE"]["width"]
        self._height: int = settings.DEFAULT_GRID_CONFIGURATION["SIZE"]["height"]
        self._cells: List[Cell] = []
        self._cell_map: Dict[int, Dict[int, int]] = {}
        self._type: GridType = GridType.Bounded
        self._generation: int = 0
        self._initial_configuration: List[List[bool]] = []
        self._current_grid_name: str = settings.CURRENT_GRID_NAME
        self._create_grid_directory()
        self.load_grid()

    def _set_up_cells(self, cell_values: Optional[List[bool]] = None):
        self._cells.clear()
        self._cell_map.clear()

        for y in range(self._height):
            self._cell_map[y] = {}
            for x in range(self._width):
                cell = Cell()
                if cell_values and cell_values[y * self._width + x]:
                    cell.flip()
                self._cells.append(cell)
                self._cell_map[y][x] = len(self._cells) - 1

    def _create_grid_directory(self):
        if not os.path.isdir(settings.USER_SAVE_FOLDER):
            os.makedirs(settings.USER_SAVE_FOLDER)

    def save_grid(self, save_name: Optional[str] = None, file_path: Optional[str] = None) -> None:
        
        self._create_grid_directory()

        if file_path is not None:
            save_name, ext = os.path.splitext(os.path.basename(file_path))
            if ext.lower() != ".grid":
                file_path += ".grid"
            
        else:
            if save_name is None:
                save_name = self._current_grid_name
            file_path = os.path.join(settings.USER_SAVE_FOLDER, f"{save_name}.grid")

        user_save = {
            "SIZE": {
                "width": self._width,
                "height": self._height
            },
            "CELLS": [cell.alive for cell in self._cells]
        }

        with open(file_path, "wb") as f:
            pickle.dump(user_save, f)

        save_name_file = os.path.join(settings.USER_SAVE_FOLDER, "current_grid.cg")
        with open(save_name_file, "w") as f:
            f.write(save_name)

    def load_grid(self, grid_name: Optional[str] = None, file_path: Optional[str] = None) -> None:
        if file_path is not None:
            file_path_to_load = file_path
            grid_name = os.path.splitext(os.path.basename(file_path))[0]
        else:
            if grid_name is None:
                save_name_file = os.path.join(settings.USER_SAVE_FOLDER, "current_grid.cg")
                if os.path.isfile(save_name_file):
                    with open(save_name_file, "r") as f:
                        grid_name = f.read().strip()
                else:
                    grid_name = settings.CURRENT_GRID_NAME
            if grid_name is not None:
                self._current_grid_name = grid_name
                grid_name = self._current_grid_name

            file_path_to_load = os.path.join(settings.USER_SAVE_FOLDER, f"{grid_name}.grid")

        file_loaded = False
        if os.path.isfile(file_path_to_load):
            try:
                with open(file_path_to_load, "rb") as f:
                    data = pickle.load(f)
                    self._width = data["SIZE"]["width"]
                    self._height = data["SIZE"]["height"]
                    self._set_up_cells(data["CELLS"])
                    file_loaded = True
                    self._current_grid_name = grid_name
            except Exception as e:
                print(f"Error loading grid from '{file_path_to_load}': {e}")

        if not file_loaded:
            self._width = settings.DEFAULT_GRID_CONFIGURATION["SIZE"]["width"]
            self._height = settings.DEFAULT_GRID_CONFIGURATION["SIZE"]["height"]
            self._current_grid_name = settings.CURRENT_GRID_NAME
            self._set_up_cells(settings.DEFAULT_GRID_CONFIGURATION["CELLS"])
        else:
            # if the file path was not in the "user_grids" folder, copy it there for future use
            if file_path is not None and not file_path.startswith(settings.USER_SAVE_FOLDER):
                self.save_grid(save_name=grid_name)

    @property
    def size(self) -> Tuple[int, int]:
        return self._width, self._height

    @property
    def type(self) -> GridType:
        return self._type
    
    @type.setter
    def type(self, grid_type: GridType) -> None:
        if not isinstance(grid_type, GridType):
            raise ValueError("Grid type must be an instance of GridType enum")
        self._type = grid_type

    def resize(self, width: int, height: int) -> None:
        if not (isinstance(width, int) and width > 0 and isinstance(height, int) and height > 0):
            raise ValueError("Width and height must be positive integers")
        if width > settings.MAX_GRID_SIZE or height > settings.MAX_GRID_SIZE:
            raise ValueError(f"Size cannot exceed {settings.MAX_GRID_SIZE}x{settings.MAX_GRID_SIZE}")
        self._width = width
        self._height = height
        self._generation = 0
        self._set_up_cells()
        self.save_grid()

    @property
    def generation(self) -> int:
        return self._generation

    def get_cell(self, x: int, y: int) -> Cell:
        if x < 0 or x >= self._width:
            raise IndexError("X coordinate out of bounds")
        if y < 0 or y >= self._height:
            raise IndexError("Y coordinate out of bounds")
        return self._cells[self._cell_map[y][x]]

    def flip_cell(self, x: int, y: int) -> None:
        if x < 0 or x >= self._width:
            raise IndexError("X coordinate out of bounds")
        if y < 0 or y >= self._height:
            raise IndexError("Y coordinate out of bounds")
        self._cells[self._cell_map[y][x]].flip()
    
    def _count_live_neighbors(self, x: int, y: int) -> int:
        count = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if self._type == GridType.Toroidal:
                    nx = (x + dx) % self._width
                    ny = (y + dy) % self._height
                else:
                    nx = x + dx
                    ny = y + dy
                if 0 <= nx < self._width and 0 <= ny < self._height:
                    cell = self._cells[self._cell_map[ny][nx]]
                    if cell.alive:
                        count += 1
        return count
    
    def iterate_generation(self) -> None:
        if self._generation == 0:
            self.save_grid(save_name='initial')
        new_states = [[self.get_cell(x, y).alive for x in range(self._width)] for y in range(self._height)]
        for y in range(self._height):
            for x in range(self._width):
                live_neighbors = self._count_live_neighbors(x, y)
                if self.get_cell(x, y).alive:
                    if live_neighbors < 2 or live_neighbors > 3:
                        new_states[y][x] = False
                else:
                    if live_neighbors == 3:
                        new_states[y][x] = True
        for y in range(self._height):
            for x in range(self._width):
                if new_states[y][x] != self.get_cell(x, y).alive:
                    self.get_cell(x, y).flip()
        
        self._generation += 1

    def reset(self) -> None:
        self._generation = 0
        self.load_grid('initial')

    @property
    def cells(self) -> List[Cell]:
        return self._cells
    
    @property
    def all_cells_dead(self) -> bool:
        return all(not cell.alive for cell in self._cells)
    
__all__ = ["Grid", "GridType"]
