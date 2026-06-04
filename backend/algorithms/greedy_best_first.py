"""
Greedy Best-First Search algorithm.

Expands the node that appears closest to the goal according to the
heuristic h(n), ignoring path cost g(n). This makes it fast but
NOT optimal — it can find suboptimal or even very long paths.

Time:  O((V + E) log V)
Space: O(V)
"""

import heapq
from typing import Tuple
import time

from algorithms.base import SearchAlgorithm, SearchNode, SearchResult
from utils.heuristics import manhattan_distance


class GreedyBestFirst(SearchAlgorithm):
    """Greedy Best-First Search — prioritizes by heuristic h(n) only."""

    def search(self) -> SearchResult:
        start_time = time.perf_counter()

        h_start = manhattan_distance(self.start, self.goal)
        start_node = SearchNode(
            state=self.start, parent=None,
            g_cost=0, h_cost=h_start, depth=0,
        )

        # Check if start == goal
        if self.start == self.goal:
            self._record_step("found_goal", self.start)
            elapsed = (time.perf_counter() - start_time) * 1000
            return self._make_result([self.start], 0, elapsed)

        # Priority queue ordered by h_cost only
        counter = 0
        frontier = [(h_start, counter, start_node)]
        visited = set()

        self._record_step(
            "add_to_frontier", self.start,
            g_cost=0, h_cost=h_start, depth=0,
        )
        self._update_frontier_size(1)

        while frontier:
            h, _, node = heapq.heappop(frontier)

            if node.state in visited:
                continue

            visited.add(node.state)
            self._explored_count += 1
            self._record_step(
                "explore", node.state,
                g_cost=node.g_cost, h_cost=node.h_cost, depth=node.depth,
            )

            # Goal test
            if node.state == self.goal:
                path = self._reconstruct_path(node)
                self._record_step(
                    "found_goal", node.state,
                    g_cost=node.g_cost, h_cost=0, depth=node.depth,
                )
                elapsed = (time.perf_counter() - start_time) * 1000
                return self._make_result(path, node.g_cost, elapsed)

            for nr, nc in self.grid.get_neighbors(*node.state):
                neighbor_state = (nr, nc)
                if neighbor_state not in visited:
                    move_cost = self.grid.get_cost(nr, nc)
                    h = manhattan_distance(neighbor_state, self.goal)
                    counter += 1
                    child = SearchNode(
                        state=neighbor_state,
                        parent=node,
                        g_cost=node.g_cost + move_cost,
                        h_cost=h,
                        depth=node.depth + 1,
                    )
                    heapq.heappush(frontier, (h, counter, child))
                    self._record_step(
                        "add_to_frontier", neighbor_state,
                        g_cost=child.g_cost, h_cost=h, depth=child.depth,
                    )

            self._update_frontier_size(len(frontier))

        # No path found
        self._record_step("no_path", self.start)
        elapsed = (time.perf_counter() - start_time) * 1000
        return self._make_result([], 0, elapsed)
