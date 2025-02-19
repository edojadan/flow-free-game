from colors import COLOR_MAP

def parse_level(level_data):
    """
    Parses a level given in the form [height, width, "encoded_string"].
      - A number in the string = that many empty cells (None).
      - A letter in the string = an endpoint cell of that color.
    Returns (height, width, grid), where grid is a 2D list of size [height][width].
    """
    height, width, encoded = level_data
    cells = []
    row = []
    i = 0

    while i < len(encoded):
        ch = encoded[i]
        if ch.isdigit():
            # Build up the entire number (could be multiple digits)
            num_str = ""
            while i < len(encoded) and encoded[i].isdigit():
                num_str += encoded[i]
                i += 1
            count = int(num_str)
            for _ in range(count):
                row.append(None)
                if len(row) == width:
                    cells.append(row)
                    row = []
        else:
            # A single letter => an endpoint of that color
            color = COLOR_MAP.get(ch, None)
            row.append(color)
            i += 1
            if len(row) == width:
                cells.append(row)
                row = []

    # If row is partially filled, pad it
    if row:
        while len(row) < width:
            row.append(None)
        cells.append(row)

    return height, width, cells


