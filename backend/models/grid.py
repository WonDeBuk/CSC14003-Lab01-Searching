"""
Grid model for the search algorithm visualizer.

Defines terrain types with associated movement costs and a Grid class
that provides neighbor lookups and cost calculations for pathfinding.
"""

from enum import IntEnum
from typing import List, Tuple, Dict


class TerrainType(IntEnum):
    """Terrain types with increasing movement difficulty."""
    ROAD = 0    # cost = 1 (easiest)
    GRASS = 1   # cost = 3
    SWAMP = 2   # cost = 5
    WALL = 3    # impassable


TERRAIN_COSTS: Dict[TerrainType, int] = {
    TerrainType.ROAD: 1,
    TerrainType.GRASS: 3,
    TerrainType.SWAMP: 5,
}


# 4-directional movement: up, down, left, right
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class Grid:
    """
    A 2D grid world for pathfinding algorithms.

    Each cell has a terrain type that determines its traversal cost.
    Walls are impassable. The grid uses (row, col) coordinates where
    row 0 is the top and col 0 is the left.
    """

    def __init__(self, width: int = 20, height: int = 20):
        """
        Initialize a grid filled with ROAD terrain.

        Args:
            width: Number of columns.
            height: Number of rows.
        """
        self.width = width
        self.height = height
        self.cells: List[List[int]] = [[TerrainType.ROAD] * width for _ in range(height)]

    def in_bounds(self, row: int, col: int) -> bool:
        """Check if (row, col) is within the grid boundaries."""
        return 0 <= row < self.height and 0 <= col < self.width

    def is_passable(self, row: int, col: int) -> bool:
        """Check if a cell is not a wall."""
        return self.cells[row][col] != TerrainType.WALL

    def get_cost(self, row: int, col: int) -> float:
        """
        Get the movement cost of entering a cell.

        Returns:
            The terrain cost, or infinity for walls.
        """
        terrain = TerrainType(self.cells[row][col])
        return TERRAIN_COSTS.get(terrain, float('inf'))

    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Get all passable 4-directional neighbors of a cell.

        Args:
            row: Row of the cell.
            col: Column of the cell.

        Returns:
            List of (row, col) tuples for passable neighbors.
        """
        neighbors = []
        for dr, dc in DIRECTIONS:
            nr, nc = row + dr, col + dc
            if self.in_bounds(nr, nc) and self.is_passable(nr, nc):
                neighbors.append((nr, nc))
        return neighbors

    @classmethod
    def from_2d_array(cls, data: List[List[int]]) -> 'Grid':
        """
        Create a Grid from a 2D list of terrain values.

        Args:
            data: 2D list where each value is a TerrainType integer.

        Returns:
            A new Grid instance.
        """
        if not data or not data[0]:
            return cls(0, 0)
        height = len(data)
        width = len(data[0])
        grid = cls(width, height)
        grid.cells = [row[:] for row in data]
        return grid

    def is_valid(self, row: int, col: int) -> bool:
        """Check if a cell is in bounds and passable (not a wall)."""
        return self.in_bounds(row, col) and self.is_passable(row, col)

    def to_2d_array(self) -> List[List[int]]:
        """Convert the grid to a plain 2D list."""
        return [row[:] for row in self.cells]
