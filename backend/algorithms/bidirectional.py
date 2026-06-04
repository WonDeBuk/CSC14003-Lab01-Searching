"""
Bidirectional BFS algorithm.

Runs two simultaneous BFS searches: one from the start and one from
the goal. When the two frontiers meet (a node is in both visited sets),
the path is reconstructed by joining the two partial paths.

Finds the shortest path by hop count. On weighted grids, the path
may not be cost-optimal.

Time:  O(b^(d/2))  — much faster than unidirectional BFS
Space: O(b^(d/2))
"""

from collections import deque
from typing import Tuple, Dict, Optional
import time

from algorithms.base import SearchAlgorithm, SearchNode, SearchResult


class BidirectionalBFS(SearchAlgorithm):
    """Bidirectional BFS — two frontiers expanding toward each other."""

    def search(self) -> SearchResult:
        start_time = time.perf_counter()

        # Check if start == goal
        if self.start == self.goal:
            self._record_step("found_goal", self.start)
            elapsed = (time.perf_counter() - start_time) * 1000
            return self._make_result([self.start], 0, elapsed)

        # Forward search from start
        fwd_frontier: deque = deque()
        fwd_parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}
        fwd_cost: Dict[Tuple[int, int], float] = {}

        fwd_frontier.append(self.start)
        fwd_parent[self.start] = None
        fwd_cost[self.start] = 0.0

        # Backward search from goal
        bwd_frontier: deque = deque()
        bwd_parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}
        bwd_cost: Dict[Tuple[int, int], float] = {}

        bwd_frontier.append(self.goal)
        bwd_parent[self.goal] = None
        bwd_cost[self.goal] = 0.0

        self._record_step("add_to_frontier", self.start, depth=0, direction="forward")
        self._record_step("add_to_frontier", self.goal, depth=0, direction="backward")

        meeting_point: Optional[Tuple[int, int]] = None

        while fwd_frontier and bwd_frontier:
            # ── Expand forward frontier ──────────────────────────
            if fwd_frontier:
                meeting_point = self._expand_frontier(
                    fwd_frontier, fwd_parent, fwd_cost,
                    bwd_parent, "forward"
                )
                if meeting_point is not None:
                    break

            # ── Expand backward frontier ─────────────────────────
            if bwd_frontier:
                meeting_point = self._expand_frontier(
                    bwd_frontier, bwd_parent, bwd_cost,
                    fwd_parent, "backward"
                )
                if meeting_point is not None:
                    break

            self._update_frontier_size(len(fwd_frontier) + len(bwd_frontier))

        if meeting_point is not None:
            # Reconstruct the full path through the meeting point
            path = self._build_bidirectional_path(
                meeting_point, fwd_parent, bwd_parent
            )
            path_cost = self._calculate_path_cost(path)
            self._record_step(
                "found_goal", meeting_point,
                g_cost=path_cost,
            )
            elapsed = (time.perf_counter() - start_time) * 1000
            return self._make_result(path, path_cost, elapsed)

        # No path found
        self._record_step("no_path", self.start)
        elapsed = (time.perf_counter() - start_time) * 1000
        return self._make_result([], 0, elapsed)

    def _expand_frontier(
        self,
        frontier: deque,
        parent: Dict,
        cost: Dict,
        other_parent: Dict,
        direction: str,
    ) -> Optional[Tuple[int, int]]:
        """
        Expand one level of a BFS frontier.

        Returns the meeting-point state if the frontiers intersect, else None.
        """
        if not frontier:
            return None

        node_state = frontier.popleft()
        self._explored_count += 1
        self._record_step(
            "explore", node_state,
            g_cost=cost.get(node_state, 0),
            direction=direction,
        )

        for nr, nc in self.grid.get_neighbors(*node_state):
            neighbor = (nr, nc)
            if neighbor not in parent:
                move_cost = self.grid.get_cost(nr, nc)
                parent[neighbor] = node_state
                cost[neighbor] = cost[node_state] + move_cost
                frontier.append(neighbor)

                self._record_step(
                    "add_to_frontier", neighbor,
                    g_cost=cost[neighbor],
                    direction=direction,
                )

                # Check if this node has been visited by the other search
                if neighbor in other_parent:
                    return neighbor

        return None

    def _build_bidirectional_path(
        self,
        meeting: Tuple[int, int],
        fwd_parent: Dict,
        bwd_parent: Dict,
    ):
        """
        Build the complete path by tracing parents from meeting point
        backward to start, and forward to goal.
        """
        # Forward half: meeting → start (reversed)
        fwd_path = []
        state = meeting
        while state is not None:
            fwd_path.append(state)
            state = fwd_parent[state]
        fwd_path.reverse()

        # Backward half: meeting → goal
        bwd_path = []
        state = bwd_parent[meeting]
        while state is not None:
            bwd_path.append(state)
            state = bwd_parent[state]

        return fwd_path + bwd_path

    def _calculate_path_cost(self, path) -> float:
        """Sum the terrain costs along a path (cost of entering each cell except start)."""
        if len(path) <= 1:
            return 0.0
        total = 0.0
        for r, c in path[1:]:
            total += self.grid.get_cost(r, c)
        return total
