"""
Helper for loading and saving files in the Game of Life application via a tkinter file dialog.

Author: P Tunis
"""


import tkinter as tk
from tkinter import filedialog

from . import settings


FILE_TYPES = {
    'grid': ("Grid Files", "*.grid"),
    'image': ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
}

def get_file_path(file_type: str = 'grid') -> str:
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[FILE_TYPES[file_type], ("All Files", "*.*")],
        initialdir=settings.USER_SAVE_FOLDER
    )
    return file_path

def choose_file_save_path(file_type: str = 'grid') -> str:
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.asksaveasfilename(
        title="Select a file",
        filetypes=[FILE_TYPES[file_type], ("All Files", "*.*")],
        initialdir=settings.USER_SAVE_FOLDER
    )
    return file_path

__all__ = [
    "get_file_path",
    "choose_file_save_path",
]