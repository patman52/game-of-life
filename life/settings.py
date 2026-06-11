



BACKGROUND_COLOR = (0, 20, 30)

DEFAULT_GRID_CONFIGURATION = {
    "SIZE": {
        "width": 5,
        "height": 5
    },
    "CELLS": [
        False, False, False, False, False,
        False, False, False, False, False,
        False, True,  True,  True,  False,
        False, False, False, False, False,
        False, False, False, False, False
    ]
}

MAX_GRID_SIZE = 200
CURRENT_GRID_NAME = "default"

USER_SAVE_FOLDER = "user_grids"

# object colors
BTN_BG = (85, 85, 85)       # button background color
SELECTED_BG = (55, 110, 55) # background color when button is selected
TXT_COL = (220, 220, 220)   # text color for buttons and labels in the control panel


__all__ = [
    "BACKGROUND_COLOR",
    "CURRENT_GRID_NAME",
    "DEFAULT_GRID_CONFIGURATION",
    "MAX_GRID_SIZE",
    "USER_SAVE_FOLDER",
    "BTN_BG",
    "SELECTED_BG",
    "TXT_COL",  
]