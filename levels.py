import random
from colors import COLOR_MAP

def encode_grid(grid):
    """
    Encodes a grid (a 2D list) into a run-length encoded string.
    Empty cells (None) are represented by a number (the count of consecutive empties)
    while a cell with a color is represented by the corresponding letter.
    """
    # Build an inverse mapping from color tuple to letter.
    inv_color_map = {v: k for k, v in COLOR_MAP.items()}
    flat = []
    for row in grid:
        for cell in row:
            if cell is None:
                flat.append("")
            else:
                flat.append(inv_color_map.get(cell, "?"))
    
    encoded = ""
    i = 0
    while i < len(flat):
        if flat[i] == "":
            count = 0
            while i < len(flat) and flat[i] == "":
                count += 1
                i += 1
            encoded += str(count)
        else:
            encoded += flat[i]
            i += 1
    return encoded

def generate_level(height, width, num_colors):
    """
    Generates a level by randomly placing 'num_colors' pairs of endpoints on a grid.
    The grid is initially empty (all None), and for each chosen color (randomly picked
    from COLOR_MAP keys) two distinct cells are marked.
    
    Returns a level in the format [height, width, encoded_string].
    Note: This simple generator does not guarantee that a valid, solvable puzzle exists.
    """
    # Create an empty grid.
    grid = [[None for _ in range(width)] for _ in range(height)]
    
    # Choose a subset of available letters (colors)
    available_letters = list(COLOR_MAP.keys())
    random.shuffle(available_letters)
    chosen = available_letters[:num_colors]
    
    # Place two endpoints for each chosen color
    for letter in chosen:
        placed = 0
        while placed < 2:
            r = random.randint(0, height - 1)
            c = random.randint(0, width - 1)
            if grid[r][c] is None:
                grid[r][c] = COLOR_MAP[letter]
                placed += 1

    encoded = encode_grid(grid)
    return [height, width, encoded]

# Generate a list of levels.
LEVELS = []

def generate_levels(num_levels, height, width, num_colors):
    """
    Generates 'num_levels' levels for a grid of size height x width with 'num_colors' pairs.
    Stores the generated level data in the global LEVELS variable and returns it.
    """
    global LEVELS
    LEVELS = []
    for _ in range(num_levels):
        level = generate_level(height, width, num_colors)
        LEVELS.append(level)
    return LEVELS

if __name__ == "__main__":
    # Example: Generate 5 levels for a 6x5 board with 3 color pairs.
    levels = generate_levels(5, 6, 5, 3)
    for lvl in levels:
        print(lvl)

