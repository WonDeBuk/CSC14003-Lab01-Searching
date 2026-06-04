"""
Uniform Cost Search (UCS) algorithm.

Expands nodes in order of increasing path cost (g-cost) using a
min-heap priority queue. Guarantees the optimal (lowest-cost) path
on weighted graphs.

Equivalent to Dijkstra's algorithm when searching for a single goal.

Time:  O((V + E) log V)
Space: O(V)
"""

import heapq
from typing import Tuple
import time

from algorithms.base import SearchAlgorithm, SearchNode, SearchResult


class UCS(SearchAlgorithm):
    """Uniform Cost Search using a min-heap ordered by g-cost."""

    def search(self) -> SearchResult:
        start_time = time.perf_counter()

        start_node = SearchNode(state=self.start, parent=None, g_cost=0, depth=0)

        # Check if start == goal
        if self.start == self.goal:
            self._record_step("found_goal", self.start)
            elapsed = (time.perf_counter() - start_time) * 1000
            return self._make_result([self.start], 0, elapsed)

        # Priority queue entries: (g_cost, tie_breaker, node)
        counter = 0
        frontier = [(0.0, counter, start_node)]
        # Best known cost to reach each state
        best_cost = {self.start: 0.0}

        self._record_step("add_to_frontier", self.start, g_cost=0, depth=0)
        self._update_frontier_size(1)

        while frontier:
            g, _, node = heapq.heappop(frontier)

            # Skip if we've already found a cheaper path to this state
            if g > best_cost.get(node.state, float('inf')):
                continue

            self._explored_count += 1
            self._record_step(
                "explore", node.state,
                g_cost=node.g_cost, depth=node.depth,
            )

            # Goal test at expansion (UCS guarantees optimality this way)
            if node.state == self.goal:
                path = self._reconstruct_path(node)
                self._record_step(
                    "found_goal", node.state,
                    g_cost=node.g_cost, depth=node.depth,
                )
                elapsed = (time.perf_counter() - start_time) * 1000
                return self._make_result(path, node.g_cost, elapsed)

            for nr, nc in self.grid.get_neighbors(*node.state):
                neighbor_state = (nr, nc)
                move_cost = self.grid.get_cost(nr, nc)
                new_g = node.g_cost + move_cost

                # Only add to frontier if this is a cheaper path
                if new_g < best_cost.get(neighbor_state, float('inf')):
                    best_cost[neighbor_state] = new_g
                    counter += 1
                    child = SearchNode(
                        state=neighbor_state,
                        parent=node,
                        g_cost=new_g,
                        depth=node.depth + 1,
                    )
                    heapq.heappush(frontier, (new_g, counter, child))
                    self._record_step(
                        "add_to_frontier", neighbor_state,
                        g_cost=new_g, depth=child.depth,
                    )

            self._update_frontier_size(len(frontier))

        # No path found
        self._record_step("no_path", self.start)
        elapsed = (time.perf_counter() - start_time) * 1000
        return self._make_result([], 0, elapsed)
