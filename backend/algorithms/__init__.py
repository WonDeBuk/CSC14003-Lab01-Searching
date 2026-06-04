"""
Algorithms package.

Exports ALGORITHM_MAP for easy lookup by the API layer.
"""

from algorithms.bfs import BFS
from algorithms.dfs import DFS
from algorithms.ucs import UCS
from algorithms.astar import AStar
from algorithms.greedy_best_first import GreedyBestFirst
from algorithms.iddfs import IDDFS
from algorithms.bidirectional import BidirectionalBFS
from algorithms.ida_star import IDAStar

ALGORITHM_MAP = {
    "bfs": BFS,
    "dfs": DFS,
    "ucs": UCS,
    "astar": AStar,
    "greedy": GreedyBestFirst,
    "iddfs": IDDFS,
    "bidirectional": BidirectionalBFS,
    "ida_star": IDAStar,
}

__all__ = [
    "ALGORITHM_MAP",
    "BFS", "DFS", "UCS", "AStar",
    "GreedyBestFirst", "IDDFS", "BidirectionalBFS", "IDAStar",
]
