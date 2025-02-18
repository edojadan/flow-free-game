# level_notation.py

from colors import COLOR_MAP

def parse_level(level_data):
    """
    Parses a level given in the form [height, width, "encoded_string"].
    In the encoded string:
      - A number means that many empty cells (None).
      - A letter means an endpoint cell of that letter's color.
    Returns (height, width, grid), where grid is a 2D list.
    """
    height, width, encoded = level_data
    cells = []
    row = []
    i = 0

    while i < len(encoded):
        ch = encoded[i]
        if ch.isdigit():
            # Collect the full number (could be multiple digits)
            num_str = ""
            while i < len(encoded) and encoded[i].isdigit():
                num_str += encoded[i]
                i += 1
            num = int(num_str)
            for _ in range(num):
                row.append(None)
                if len(row) == width:
                    cells.append(row)
                    row = []
        else:
            # It's a letter
            color = COLOR_MAP.get(ch, None)
            row.append(color)
            i += 1
            if len(row) == width:
                cells.append(row)
                row = []

    # If row not complete, fill up
    if row:
        while len(row) < width:
            row.append(None)
        cells.append(row)

    return height, width, cells
