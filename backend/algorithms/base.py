"""
Base classes for all search algorithms.

Provides the abstract SearchAlgorithm class and supporting dataclasses
(SearchNode, SearchStep, SearchResult) that every algorithm implementation
must use. This ensures consistent step recording and result formatting
across all algorithms.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import time


@dataclass
class SearchNode:
    """
    A node in the search tree.

    Attributes:
        state: (row, col) position on the grid.
        parent: Reference to the parent node for path reconstruction.
        g_cost: Cost from start to this node.
        h_cost: Heuristic estimate from this node to goal.
        depth: Depth in the search tree (used by IDDFS).
    """
    state: Tuple[int, int]
    parent: Optional['SearchNode']
    g_cost: float = 0.0
    h_cost: float = 0.0
    depth: int = 0

    @property
    def f_cost(self) -> float:
        """Total estimated cost f = g + h."""
        return self.g_cost + self.h_cost

    def __lt__(self, other: 'SearchNode') -> bool:
        """Comparison for priority queue ordering (lower f_cost = higher priority)."""
        return self.f_cost < other.f_cost


@dataclass
class SearchStep:
    """
    A single step in the search process, recorded for visualization.

    The frontend uses these steps to animate the algorithm's behavior,
    showing which cells are explored and which are added to the frontier.
    """
    action: str  # "explore" | "add_to_frontier" | "found_goal" | "no_path"
    state: Tuple[int, int]
    g_cost: float = 0.0
    h_cost: float = 0.0
    f_cost: float = 0.0
    depth: int = 0
    frontier: List[dict] = field(default_factory=list)
    explored_count: int = 0
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """
    The complete result of running a search algorithm.

    Contains the path (if found), performance metrics, and the full
    list of steps for visualization replay.
    """
    algorithm_name: str
    path: List[Tuple[int, int]]
    path_found: bool
    path_cost: float
    nodes_explored: int
    max_frontier_size: int
    execution_time_ms: float
    steps: List[SearchStep]


class SearchAlgorithm(ABC):
    """
    Abstract base class for all search algorithms.

    Subclasses must implement the `search()` method. This base class
    provides helpers for recording steps, reconstructing paths, and
    building the final SearchResult.
    """

    def __init__(self, grid, start: Tuple[int, int], goal: Tuple[int, int]):
        """
        Args:
            grid: A Grid instance with terrain data.
            start: (row, col) start position.
            goal: (row, col) goal position.
        """
        self.grid = grid
        self.start = tuple(start)
        self.goal = tuple(goal)
        self._steps: List[SearchStep] = []
        self._explored_count: int = 0
        self._max_frontier_size: int = 0

    @abstractmethod
    def search(self) -> SearchResult:
        """Run the search algorithm and return the result."""
        pass

    def _record_step(
        self,
        action: str,
        state: Tuple[int, int],
        g_cost: float = 0.0,
        h_cost: float = 0.0,
        depth: int = 0,
        frontier_snapshot: Optional[List[dict]] = None,
        **extra
    ):
        """
        Record a visualization step.

        Args:
            action: One of "explore", "add_to_frontier", "found_goal", "no_path".
            state: The (row, col) cell this step concerns.
            g_cost: Cost from start to this state.
            h_cost: Heuristic cost estimate to goal.
            depth: Search tree depth.
            frontier_snapshot: Optional snapshot of current frontier.
            **extra: Any additional data for the step.
        """
        self._steps.append(SearchStep(
            action=action,
            state=state,
            g_cost=g_cost,
            h_cost=h_cost,
            f_cost=g_cost + h_cost,
            depth=depth,
            frontier=frontier_snapshot or [],
            explored_count=self._explored_count,
            extra=extra if extra else {},
        ))

    def _update_frontier_size(self, current_size: int):
        """Track the maximum frontier size seen so far."""
        if current_size > self._max_frontier_size:
            self._max_frontier_size = current_size

    def _reconstruct_path(self, node: SearchNode) -> List[Tuple[int, int]]:
        """Walk parent pointers to build the path from start to goal."""
        path = []
        while node is not None:
            path.append(node.state)
            node = node.parent
        return list(reversed(path))

    def _make_result(
        self,
        path: List[Tuple[int, int]],
        path_cost: float,
        exec_time: float
    ) -> SearchResult:
        """
        Build the final SearchResult.

        Args:
            path: The solution path (empty if no path found).
            path_cost: Total cost of the path.
            exec_time: Execution time in milliseconds.
        """
        return SearchResult(
            algorithm_name=self.__class__.__name__,
            path=path,
            path_found=len(path) > 0,
            path_cost=path_cost,
            nodes_explored=self._explored_count,
            max_frontier_size=self._max_frontier_size,
            execution_time_ms=exec_time,
            steps=self._steps,
        )
