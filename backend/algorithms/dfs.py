"""
Depth-First Search (DFS) algorithm.

Explores as deep as possible along each branch before backtracking,
using a LIFO stack. Does NOT guarantee the shortest or optimal path.

Time:  O(V + E)
Space: O(V) worst case, O(b*m) typical where b=branching, m=max depth
"""

from typing import Tuple
import time

from algorithms.base import SearchAlgorithm, SearchNode, SearchResult


class DFS(SearchAlgorithm):
    """Depth-First Search using a LIFO stack."""

    def search(self) -> SearchResult:
        start_time = time.perf_counter()

        start_node = SearchNode(state=self.start, parent=None, g_cost=0, depth=0)

        # Check if start == goal
        if self.start == self.goal:
            self._record_step("found_goal", self.start)
            elapsed = (time.perf_counter() - start_time) * 1000
            return self._make_result([self.start], 0, elapsed)

        stack = [start_node]
        visited = set()

        self._record_step("add_to_frontier", self.start, depth=0)
        self._update_frontier_size(1)

        while stack:
            node = stack.pop()

            if node.state in visited:
                continue

            visited.add(node.state)
            self._explored_count += 1
            self._record_step(
                "explore", node.state,
                g_cost=node.g_cost, depth=node.depth,
            )

            if node.state == self.goal:
                path = self._reconstruct_path(node)
                self._record_step(
                    "found_goal", node.state,
                    g_cost=node.g_cost, depth=node.depth,
                )
                elapsed = (time.perf_counter() - start_time) * 1000
                return self._make_result(path, node.g_cost, elapsed)

            # Push neighbors in reverse order so the first neighbor
            # (up) is explored first (it ends up on top of the stack)
            neighbors = self.grid.get_neighbors(*node.state)
            for nr, nc in reversed(neighbors):
                neighbor_state = (nr, nc)
                if neighbor_state not in visited:
                    move_cost = self.grid.get_cost(nr, nc)
                    child = SearchNode(
                        state=neighbor_state,
                        parent=node,
                        g_cost=node.g_cost + move_cost,
                        depth=node.depth + 1,
                    )
                    stack.append(child)
                    self._record_step(
                        "add_to_frontier", neighbor_state,
                        g_cost=child.g_cost, depth=child.depth,
                    )

            self._update_frontier_size(len(stack))

        # No path found
        self._record_step("no_path", self.start)
        elapsed = (time.perf_counter() - start_time) * 1000
        return self._make_result([], 0, elapsed)
