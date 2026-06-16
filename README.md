# game-of-life
Conway's Game of Life made via pygame

https://github.com/user-attachments/assets/072cb932-ad3b-44fe-a113-2d669bda016a

## Getting Started

Install pygame or run `pip install -r requirements`

### Tkinter setup (Linux and macOS)

The game uses tkinter for loading and saving grids. 

Linux:

- Ubuntu or Debian: `sudo apt install python3-tk`
- Fedora: `sudo dnf install python3-tkinter`
- Arch: `sudo pacman -S tk`

macOS:

- If you installed Python from python.org, Tkinter is usually already included.
- If you use Homebrew Python and Tkinter is missing, run:
    - `brew install tcl-tk`
    - `brew reinstall python`

Verify Tkinter:

`python3 -m tkinter`


To launch the game, simply run `python main.py`

## Play the Game

### Basic Key Commands:
- **p**: starts/pauses the game
- **l**: turns on and off the grind lines between cells
- **r**: resets the grid to the initial starting point. Play must be paused.

### Adjusting Grid:
Adjust the width and height of the grid using the plus or minus buttons. Press the apply size buton to apply (this will reset all cells). 

Click on sets to 'flip' them from dead to alive and vice versa.

### Grid Types
- **Bounded**: The grid is bounded around the edges and only cells directly adjacent to each other factor into cell generation 'life' status.
- ** Toroidal**: The right-left / upper-lower boundaries of the grid are 'stitched' together, meaning cells on opposite edges affect generation 'life' status.

### Saving / Loading Grids

Grids can saved to local '.grid' files to be re-loaded at later points. 

### Image To Grid
Loads an image file (png, jpg, bmp, gif, etc.) and converts the image to a grid. The image is first downsized and then converted to pure black and white (alive or dead) based on the average luminence of each pixel. This enables the user to load and play the game of life with photos. 
