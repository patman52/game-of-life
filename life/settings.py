



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

USER_SAVE_FOLDER = "_user_saves"


__all__ = [
    "BACKGROUND_COLOR",
    "CURRENT_GRID_NAME",
    "DEFAULT_GRID_CONFIGURATION",
    "MAX_GRID_SIZE",
    "USER_SAVE_FOLDER",
]