import os
import pickle
from enum import Enum
from typing import List, Tuple

MAX_SIZE = 100


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
        self._width: int = 10
        self._height: int = 10
        self._cells: List[List[Cell]] = []
        self._type: GridType = GridType.Bounded
        self._generation: int = 0
        self._initial_configuration: List[List[bool]] = []
        self._load_initial_configuration()


    def _set_up_cells(self):
        self._cells: List[List[Cell]] = [[Cell() for _ in range(self._width)] for _ in range(self._height)]
        
    def _save_initial_configuration(self) -> None:
        self._initial_configuration = [[cell.alive for cell in row] for row in self._cells]
        with open("initial_configuration.pkl", "wb") as f:
            pickle.dump(self._initial_configuration, f)
    
    def _load_initial_configuration(self) -> None:
        if os.path.isfile("initial_configuration.pkl"):
            with open("initial_configuration.pkl", "rb") as f:
                self._initial_configuration = pickle.load(f)
                self._width = len(self._initial_configuration[0])
                self._height = len(self._initial_configuration) 
            self._set_up_cells()
            for y in range(self._height):
                for x in range(self._width):
                    if self._initial_configuration[y][x] != self._cells[y][x].alive:
                        self._cells[y][x].flip()
        else:
            self._set_up_cells()
            self._initial_configuration = [[False for _ in range(self._width)] for _ in range(self._height)]

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
        if width > MAX_SIZE or height > MAX_SIZE:
            raise ValueError(f"Size cannot exceed {MAX_SIZE}x{MAX_SIZE}")
        self._width = width
        self._height = height
        self._generation = 0
        self._set_up_cells()
        self._save_initial_configuration()
        self._load_initial_configuration()

    @property
    def generation(self) -> int:
        return self._generation

    def flip_cell(self, x: int, y: int) -> None:
        if x < 0 or x >= self._width:
            raise IndexError("X coordinate out of bounds")
        if y < 0 or y >= self._height:
            raise IndexError("Y coordinate out of bounds")
        self._cells[y][x].flip()
    
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
                    if self._cells[ny][nx].alive:
                        count += 1
        return count
    
    def iterate_generation(self) -> None:
        if self._generation == 0:
            self._save_initial_configuration()
        new_states = [[cell.alive for cell in row] for row in self._cells]
        for y in range(self._height):
            for x in range(self._width):
                live_neighbors = self._count_live_neighbors(x, y)
                if self._cells[y][x].alive:
                    if live_neighbors < 2 or live_neighbors > 3:
                        new_states[y][x] = False
                else:
                    if live_neighbors == 3:
                        new_states[y][x] = True
        for y in range(self._height):
            for x in range(self._width):
                if new_states[y][x] != self._cells[y][x].alive:
                    self._cells[y][x].flip()
        
        self._generation += 1

    def reset(self) -> None:
        self._load_initial_configuration()
        self._generation = 0
        for x, row in enumerate(self._initial_configuration):
            for y, alive in enumerate(row):
                if self._initial_configuration[y][x] != self._cells[y][x].alive:
                    self._cells[y][x].flip()

    @property
    def cells(self) -> List[List[Cell]]:
        return self._cells
    
__all__ = ["Grid", "GridType", "MAX_SIZE"]
