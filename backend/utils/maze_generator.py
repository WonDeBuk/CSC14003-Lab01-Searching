"""
Maze and terrain generator for the search visualizer.

Uses recursive division to carve wall structures, then scatters
varied terrain (grass, swamp) to create interesting weighted-graph
test cases for the search algorithms.
"""

import random
from typing import List, Tuple

from models.grid import TerrainType


def generate_maze(
    width: int = 20,
    height: int = 20,
    wall_density: float = 0.3,
    terrain_variety: bool = True,
) -> Tuple[List[List[int]], List[int], List[int]]:
    """
    Generate a random maze with optional terrain variety.

    The algorithm:
    1. Start with an empty grid (all ROAD).
    2. Apply recursive division to create wall structures.
    3. Optionally scatter grass and swamp patches.
    4. Place start (top-left region) and goal (bottom-right region),
       ensuring both are on passable terrain.

    Args:
        width: Number of columns (5–50).
        height: Number of rows (5–50).
        wall_density: Fraction of cells that become walls (0.0–0.8).
        terrain_variety: Whether to add grass/swamp terrain.

    Returns:
        (grid_2d, start, goal) where grid_2d is a list-of-lists of
        TerrainType ints, and start/goal are [row, col] lists.
    """
    grid = [[TerrainType.ROAD] * width for _ in range(height)]

    # ── Step 1: Add walls via recursive division ──────────────────
    _recursive_division(grid, 0, 0, width, height, wall_density)

    # ── Step 2: Scatter terrain variety ───────────────────────────
    if terrain_variety:
        _add_terrain_patches(grid, width, height)

    # ── Step 3: Pick start and goal on passable cells ─────────────
    start = _find_passable_cell(grid, width, height, region="top_left")
    goal = _find_passable_cell(grid, width, height, region="bottom_right")

    # Make sure start and goal are clear ROAD
    grid[start[0]][start[1]] = TerrainType.ROAD
    grid[goal[0]][goal[1]] = TerrainType.ROAD

    return grid, start, goal


def _recursive_division(
    grid: List[List[int]],
    x: int, y: int,
    w: int, h: int,
    density: float,
):
    """
    Recursively divide the grid region with walls, leaving random passages.

    For regions large enough, pick a random orientation (horizontal or
    vertical), draw a wall across the region, punch a passage hole,
    then recurse into the two sub-regions.
    """
    min_size = 4  # Don't subdivide regions smaller than this

    if w < min_size or h < min_size:
        return

    # Decide orientation based on shape
    if w > h:
        orientation = "vertical"
    elif h > w:
        orientation = "horizontal"
    else:
        orientation = random.choice(["horizontal", "vertical"])

    if random.random() > density * 1.5:
        return  # Probabilistically skip subdivision for sparser mazes

    if orientation == "horizontal":
        # Draw a horizontal wall at a random row
        wall_row = y + random.randint(2, h - 3) if h > 4 else y + h // 2
        passage_col = x + random.randint(0, w - 1)

        for col in range(x, x + w):
            if col != passage_col and 0 <= wall_row < len(grid) and 0 <= col < len(grid[0]):
                grid[wall_row][col] = TerrainType.WALL

        # Add extra passages to avoid overly blocked mazes
        extra_passages = max(1, w // 5)
        for _ in range(extra_passages):
            pc = x + random.randint(0, w - 1)
            if 0 <= wall_row < len(grid) and 0 <= pc < len(grid[0]):
                grid[wall_row][pc] = TerrainType.ROAD

        # Recurse into the two sub-regions
        _recursive_division(grid, x, y, w, wall_row - y, density)
        _recursive_division(grid, x, wall_row + 1, w, y + h - wall_row - 1, density)
    else:
        # Draw a vertical wall at a random column
        wall_col = x + random.randint(2, w - 3) if w > 4 else x + w // 2
        passage_row = y + random.randint(0, h - 1)

        for row in range(y, y + h):
            if row != passage_row and 0 <= row < len(grid) and 0 <= wall_col < len(grid[0]):
                grid[row][wall_col] = TerrainType.WALL

        extra_passages = max(1, h // 5)
        for _ in range(extra_passages):
            pr = y + random.randint(0, h - 1)
            if 0 <= pr < len(grid) and 0 <= wall_col < len(grid[0]):
                grid[pr][wall_col] = TerrainType.ROAD

        _recursive_division(grid, x, y, wall_col - x, h, density)
        _recursive_division(grid, wall_col + 1, y, x + w - wall_col - 1, h, density)


def _add_terrain_patches(
    grid: List[List[int]],
    width: int,
    height: int,
):
    """
    Scatter grass and swamp patches across the grid.

    Patches are small clusters (2–4 cells) seeded at random positions.
    Only ROAD cells are converted; walls are left intact.
    """
    num_patches = (width * height) // 8

    for _ in range(num_patches):
        terrain = random.choice([TerrainType.GRASS, TerrainType.GRASS, TerrainType.SWAMP])
        r = random.randint(0, height - 1)
        c = random.randint(0, width - 1)

        if grid[r][c] != TerrainType.WALL:
            grid[r][c] = terrain

            # Grow the patch to 1–3 adjacent cells
            for _ in range(random.randint(1, 3)):
                dr, dc = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                nr, nc = r + dr, c + dc
                if 0 <= nr < height and 0 <= nc < width and grid[nr][nc] == TerrainType.ROAD:
                    grid[nr][nc] = terrain


def _find_passable_cell(
    grid: List[List[int]],
    width: int,
    height: int,
    region: str,
) -> List[int]:
    """
    Find a passable cell in the specified corner region of the grid.

    Args:
        region: "top_left" or "bottom_right".

    Returns:
        [row, col] of a passable cell.
    """
    margin_r = max(1, height // 4)
    margin_c = max(1, width // 4)

    if region == "top_left":
        row_range = range(0, margin_r)
        col_range = range(0, margin_c)
    else:
        row_range = range(height - margin_r, height)
        col_range = range(width - margin_c, width)

    # Try random cells in the region first
    for _ in range(100):
        r = random.choice(list(row_range))
        c = random.choice(list(col_range))
        if grid[r][c] != TerrainType.WALL:
            return [r, c]

    # Fallback: scan the region systematically
    for r in row_range:
        for c in col_range:
            if grid[r][c] != TerrainType.WALL:
                return [r, c]

    # Last resort: force a passable cell
    r = list(row_range)[0]
    c = list(col_range)[0]
    grid[r][c] = TerrainType.ROAD
    return [r, c]
