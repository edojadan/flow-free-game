import random
import math

def baseMatrix(n, letters):
    """
    Generate an initial state for an n×n grid.
    Each row becomes a chain with all cells in that row.
    Each chain is a dictionary with:
      - "cells": list of positions (tuples (row, col), 1-indexed)
      - "color": fixed letter (from letters)
    """
    chains = []
    for i in range(n):
        chain = {
            "cells": [],
            "color": letters[i]
        }
        for j in range(n):
            # Store positions as (row, col), 1-indexed
            chain["cells"].append((i + 1, j + 1))
        chains.append(chain)
    return chains

def edgeSwitch(chains, chain_limit):
    """
    For each chain, examine its tails (first and last positions).
    If a tail of one chain is adjacent (distance 1) to a tail of another chain
    (provided that donor chain has more than chain_limit cells), then with 50% chance,
    remove that tail from the donor chain and attach it to the receiving chain.
    
    This function does not alter a chain’s fixed color.
    """
    switched = False
    for i in range(len(chains)):
        if switched:
            break
        # For the receiving chain, try both its first (index 0) and last (index -1) cell.
        for k1 in (-1, 0):
            if switched:
                break
            p = chains[i]["cells"][k1]  # position tuple (row, col)
            for j in range(len(chains)):
                if switched:
                    break
                if i == j:
                    continue
                # Only consider donor chains that have more than chain_limit cells.
                if len(chains[j]["cells"]) <= chain_limit:
                    continue
                for k2 in (-1, 0):
                    if switched:
                        break
                    pprime = chains[j]["cells"][k2]
                    # Check adjacency: distance squared equals 1 (horizontal or vertical neighbor)
                    if (p[0] - pprime[0])**2 + (p[1] - pprime[1])**2 == 1:
                        if random.random() > 0.5:
                            # Remove the tail from donor chain j.
                            removed = chains[j]["cells"].pop(k2)
                            # Attach it to receiving chain i.
                            if k1 == -1:
                                chains[i]["cells"].append(removed)
                            elif k1 == 0:
                                chains[i]["cells"].insert(0, removed)
                            switched = True
    return chains

def generate_flow_solution(n, iter_count, chain_limit, letters):
    """
    Generate a complete flow solution by starting with the base matrix and applying edgeSwitch repeatedly.
    """
    chains = baseMatrix(n, letters)
    for _ in range(iter_count):
        chains = edgeSwitch(chains, chain_limit)
        random.shuffle(chains)  # Shuffle chains to remove bias
    return chains

def create_puzzle_grid(solution, n):
    """
    From the flow solution (list of chains), create an n×n grid where only the endpoints
    (first and last cell of each chain) are marked with the chain's fixed color.
    Coordinates are converted from 1-indexed to 0-indexed.
    """
    grid = [[None for _ in range(n)] for _ in range(n)]
    for chain in solution:
        if not chain["cells"]:
            continue
        start = chain["cells"][0]
        end = chain["cells"][-1]
        r1, c1 = start[0] - 1, start[1] - 1
        r2, c2 = end[0] - 1, end[1] - 1
        grid[r1][c1] = chain["color"]
        grid[r2][c2] = chain["color"]
    return grid

def encode_grid(grid):
    """
    Encode the grid into a run-length string.
    Consecutive empty cells (None) are replaced by their count (as digits),
    and cells with a letter are output directly.
    """
    encoded = ""
    count = 0
    for row in grid:
        for cell in row:
            if cell is None:
                count += 1
            else:
                if count > 0:
                    encoded += str(count)
                    count = 0
                encoded += cell
    if count > 0:
        encoded += str(count)
    return encoded

def generate_level(n=6, iter_count=None, chain_limit=None):
    """
    Generate a new Flow puzzle level.
    
    Parameters:
      n          : grid dimension (n x n)
      iter_count : number of iterations for edgeSwitch (default: 10 * n)
      chain_limit: minimum chain length for switching (default: max(1, n - 4))
    
    Returns:
      A list [n, n, encoded_string] compatible with parse_level().
      Each color (letter) appears exactly twice (one pair per chain).
    """
    if iter_count is None:
        iter_count = 10 * n
    if chain_limit is None:
        chain_limit = max(1, n - 4)
    letters = list("abcdefghijklmnopqrstuvwxyz")[:n]
    solution = generate_flow_solution(n, iter_count, chain_limit, letters)
    puzzle_grid = create_puzzle_grid(solution, n)
    encoded = encode_grid(puzzle_grid)
    return [n, n, encoded]

# --- Testing Block ---
if __name__ == "__main__":
    # For reproducibility, you might set a fixed seed:
    random.seed(42)
    level_data = generate_level(n=6)
    print("Generated level data:")
    print(level_data)