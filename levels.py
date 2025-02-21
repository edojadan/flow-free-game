import random
from level_generator import generate_level

def get_random_level():
    return generate_level(rows=6, cols=5)

LEVELS = [
    [6, 5, "1d2a4b2b1c2c10da"], # The example from the original code
]
"""
def get_level(index=0):
    # Replace the hardcoded level with a generated one.
    return generate_level(rows=6, cols=5)
    Return a level from the list by index (wrap if out of range).
    #return LEVELS[index % len(LEVELS)] may put back in 

"""
def get_level(index=0):
    # Generate a 6×6 puzzle using our new generator
    return generate_level(n=random.randint(6,10))
