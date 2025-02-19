import random
from collections import deque
from colors import COLOR_MAP

def generate_puzzle(height, width, flow_count, max_endpoint_tries=200, max_solver_attempts=50):
    """
    Generate a single-solution puzzle on a (height x width) grid with 'flow_count' flows.
    - We place endpoints randomly up to 'max_endpoint_tries' times.
    - For each placement, we attempt a backtracking solver that enumerates possible solutions
      up to 'max_solver_attempts' times, ensuring we have exactly one solution that fills the board.

    Returns a list [height, width, rle_string] if successful, or None if we can't make a puzzle
    (which is unlikely with high tries).
    """

    color_keys = list(COLOR_MAP.keys())
    random.shuffle(color_keys)  # randomize color picking
    if flow_count > len(color_keys):
        # In practice, you should not exceed the distinct color letters available
        print("Not enough distinct colors for flow_count.")
        return None
    color_choices = color_keys[:flow_count]

    for _ in range(max_endpoint_tries):
        # Create an empty grid of None
        grid = [[None for _ in range(width)] for _ in range(height)]
        
        # Randomly place endpoints
        endpoints = _place_endpoints(grid, color_choices)

        # Now run the robust solver to see if EXACTLY ONE solution fills all cells
        solutions = find_all_solutions_single_coverage(grid, endpoints, max_solutions=2)
        # solutions is a list of solution dictionaries, or empty if none found
        if len(solutions) == 1:
            # We got exactly one solution
            # Convert endpoints to RLE
            rle = grid_to_rle(endpoints, height, width)
            return [height, width, rle]

    # If we exhaust tries, return None (very unlikely with a large try count)
    return None


def _place_endpoints(grid, color_choices):
    """
    Randomly place 2 endpoints for each color in distinct cells.
    Returns { color: [(r1,c1), (r2,c2)], ... }.
    """
    height = len(grid)
    width = len(grid[0])
    used = set()
    color_endpoints = {}

    for color in color_choices:
        color_endpoints[color] = []
        for _ in range(2):
            while True:
                r = random.randint(0, height - 1)
                c = random.randint(0, width - 1)
                if (r,c) not in used:
                    used.add((r,c))
                    color_endpoints[color].append((r,c))
                    break
    return color_endpoints


def find_all_solutions_single_coverage(grid, endpoints, max_solutions=2):
    """
    Attempt to find all solutions (up to 'max_solutions') that:
      - Connect each color's endpoints with a path
      - Fully cover the board with no overlaps or empty cells
    Return a list of solutions. Each solution can be a dict { color: path }.

    If we find >= max_solutions, we stop searching further (for uniqueness check).
    """

    colors_in_order = list(endpoints.keys())
    solutions = []

    # We'll keep a 2D array of 'owner' so we know which color (if any) occupies each cell
    height = len(grid)
    width = len(grid[0])
    owner = [[None for _ in range(width)] for _ in range(height)]

    # Mark endpoints in owner
    for color, (ep1, ep2) in endpoints.items():
        r1,c1 = ep1
        r2,c2 = ep2
        owner[r1][c1] = color
        owner[r2][c2] = color

    # We'll store the partial path for each color
    partial_paths = {color: [] for color in colors_in_order}

    def backtrack(color_index):
        if len(solutions) >= max_solutions:
            return  # already have enough solutions

        if color_index == len(colors_in_order):
            # All colors assigned. Check coverage
            if _all_filled(owner):
                # Build solution dict from the ownership
                sol = {}
                for col in colors_in_order:
                    # Extract path cells belonging to col
                    path_cells = []
                    for rr in range(height):
                        for cc in range(width):
                            if owner[rr][cc] == col:
                                path_cells.append((rr,cc))
                    sol[col] = path_cells
                solutions.append(sol)
            return

        color = colors_in_order[color_index]
        ep1, ep2 = endpoints[color]
        # We do a DFS to find all possible ways to connect ep1->ep2 with no overlap
        # (or we can do BFS, but DFS is fine for enumerating paths).

        # First collect a path from ep1 to ep2
        visited = set()
        path_stack = [(ep1, [ep1])]
        visited.add(ep1)

        while path_stack and len(solutions) < max_solutions:
            (r,c), path = path_stack.pop()
            if (r,c) == ep2:
                # Found a path for this color
                # Mark these cells as owned by 'color'
                for (pr, pc) in path:
                    owner[pr][pc] = color

                # Move to next color
                backtrack(color_index + 1)

                # Unmark
                for (pr, pc) in path:
                    if (pr, pc) != ep1 and (pr, pc) != ep2:
                        owner[pr][pc] = None
                continue

            # Explore neighbors
            for nr,nc in _neighbors(r, c, height, width):
                if (nr,nc) not in visited:
                    # We can occupy (nr,nc) if it's either ep2 or currently free
                    if (nr,nc) == ep2 or owner[nr][nc] is None:
                        visited.add((nr,nc))
                        path_stack.append(((nr,nc), path + [(nr,nc)]))
    # end of backtrack function

    backtrack(0)
    return solutions


def _neighbors(r, c, height, width):
    """Up/down/left/right neighbors within grid bounds."""
    for nr, nc in [(r-1,c),(r+1,c),(r,c-1),(r,c+1)]:
        if 0 <= nr < height and 0 <= nc < width:
            yield (nr,nc)

def _all_filled(owner_grid):
    """Return True if no None cells remain in 'owner_grid'."""
    for row in owner_grid:
        for cell in row:
            if cell is None:
                return False
    return True


def grid_to_rle(endpoints, height, width):
    """
    Convert just the endpoints into an RLE string.
    All non-endpoint cells become '.'.
    Then we do run-length encoding of '.' segments and preserve letters for endpoints.
    """
    # Build a 1D list representing row-major cells
    # Mark endpoints with their letter, everything else '.' 
    cell_chars = []
    # We need a quick reverse lookup from RGB to letter
    color_to_letter = {}
    for letter, rgb in COLOR_MAP.items():
        color_to_letter[rgb] = letter

    # Build a 2D list of '.' first
    layout = [['.' for _ in range(width)] for _ in range(height)]
    for color, (ep1, ep2) in endpoints.items():
        rgb = COLOR_MAP[color]
        letter = color_to_letter[rgb]
        r1,c1 = ep1
        r2,c2 = ep2
        layout[r1][c1] = letter
        layout[r2][c2] = letter

    # Flatten and do RLE
    flattened = []
    for r in range(height):
        for c in range(width):
            flattened.append(layout[r][c])

    rle = []
    dot_count = 0
    for ch in flattened:
        if ch == '.':
            dot_count += 1
        else:
            if dot_count > 0:
                rle.append(str(dot_count))
                dot_count = 0
            rle.append(ch)
    if dot_count > 0:
        rle.append(str(dot_count))

    return ''.join(rle)


def _find_letter_for_color(rgb_tuple):
    """Find which single letter in COLOR_MAP corresponds to the given (R,G,B)."""
    for letter, color_val in COLOR_MAP.items():
        if color_val == rgb_tuple:
            return letter
    return '.'  # fallback (shouldn't happen if color_map is consistent)

