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
            # A letter representing an endpoint cell
            color = COLOR_MAP.get(ch, None)
            row.append(color)
            i += 1
            if len(row) == width:
                cells.append(row)
                row = []

    # If there is a partially filled row, pad it with None
    if row:
        while len(row) < width:
            row.append(None)
        cells.append(row)

    # Diagnostic prints
    total_cells = sum(len(r) for r in cells)
    expected = height * width
    print(f"Parsed grid: {len(cells)} rows, expected {height} rows.")
    for idx, r in enumerate(cells):
        print(f"Row {idx} length: {len(r)}")
    print(f"Total cells parsed: {total_cells}, expected: {expected}")

    # Assert that we have the right number of cells.
    assert total_cells == expected, f"Level data error: expected {expected} cells but got {total_cells}."

    return height, width, cells

