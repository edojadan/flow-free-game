LEVELS = [
    [6, 5, "1d2a4b2b1c2c10da"], # The example from the original code
]

def get_level(index=0):
    """Return a level from the list by index (wrap if out of range)."""
    return LEVELS[index % len(LEVELS)]
