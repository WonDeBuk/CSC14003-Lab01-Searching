"""
Breadth-First Search (BFS) algorithm.

Explores nodes level by level using a FIFO queue. Guarantees the shortest
path in terms of number of edges (hops), but does NOT account for edge
weights — so it is NOT optimal on weighted grids.

Time:  O(V + E)
Space: O(V)
"""

from collections import deque
from typing import Tuple
import time

from algorithms.base import SearchAlgorithm, SearchNode, SearchResult


class BFS(SearchAlgorithm):
    """Breadth-First Search using a FIFO queue."""

    def search(self) -> SearchResult:
        start_time = time.perf_counter()

        start_node = SearchNode(state=self.start, parent=None, g_cost=0, depth=0)

        # Check if start == goal
        if self.start == self.goal:
            self._record_step("found_goal", self.start)
            elapsed = (time.perf_counter() - start_time) * 1000
            return self._make_result([self.start], 0, elapsed)

        frontier: deque = deque([start_node])
        visited = {self.start}

        self._record_step("add_to_frontier", self.start, depth=0)
        self._update_frontier_size(1)

        while frontier:
            node = frontier.popleft()
            self._explored_count += 1
            self._record_step(
                "explore", node.state,
                g_cost=node.g_cost, depth=node.depth,
            )

            for nr, nc in self.grid.get_neighbors(*node.state):
                neighbor_state = (nr, nc)

                if neighbor_state in visited:
                    continue

                move_cost = self.grid.get_cost(nr, nc)
                child = SearchNode(
                    state=neighbor_state,
                    parent=node,
                    g_cost=node.g_cost + move_cost,
                    depth=node.depth + 1,
                )

                if neighbor_state == self.goal:
                    self._explored_count += 1
                    path = self._reconstruct_path(child)
                    self._record_step(
                        "found_goal", neighbor_state,
                        g_cost=child.g_cost, depth=child.depth,
                    )
                    elapsed = (time.perf_counter() - start_time) * 1000
                    return self._make_result(path, child.g_cost, elapsed)

                visited.add(neighbor_state)
                frontier.append(child)
                self._record_step(
                    "add_to_frontier", neighbor_state,
                    g_cost=child.g_cost, depth=child.depth,
                )

            self._update_frontier_size(len(frontier))

        # No path found
        self._record_step("no_path", self.start)
        elapsed = (time.perf_counter() - start_time) * 1000
        return self._make_result([], 0, elapsed)
