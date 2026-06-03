
import tkinter as tk
from tkinter import filedialog

from . import settings

def pick_grid_file() -> str:
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select a grid file",
        filetypes=[("Grid Files", "*.grid"), ("All Files", "*.*")],
        initialdir=settings.USER_SAVE_FOLDER
    )
    return file_path

def choose_grid_file_path() -> str:
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.asksaveasfilename(
        title="Select a grid file",
        filetypes=[("Grid Files", "*.grid"), ("All Files", "*.*")],
        initialdir=settings.USER_SAVE_FOLDER
    )
    return file_path

__all__ = [
    "pick_grid_file",
    "choose_grid_file_path",
]