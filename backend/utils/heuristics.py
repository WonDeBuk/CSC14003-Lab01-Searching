"""
Heuristic functions for informed search algorithms.

All heuristics take two (row, col) tuples and return a non-negative float
estimate of the distance between them. They must be admissible (never
overestimate) to guarantee optimality in A* and IDA*.
"""

from typing import Tuple


def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """
    Manhattan (L1) distance between two grid cells.

    This is admissible for 4-directional movement with minimum cost 1
    because the shortest possible path between two points on a grid
    requires at least |Δrow| + |Δcol| moves.

    Args:
        a: (row, col) of the first cell.
        b: (row, col) of the second cell.

    Returns:
        The Manhattan distance as a float.
    """
    return float(abs(a[0] - b[0]) + abs(a[1] - b[1]))
