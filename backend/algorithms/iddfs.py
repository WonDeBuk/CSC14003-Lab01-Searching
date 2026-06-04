"""
Iterative Deepening Depth-First Search (IDDFS) algorithm.

Combines DFS's space efficiency with BFS's completeness by running
depth-limited DFS with progressively increasing depth limits.
Guarantees the shortest path by hop count (not optimal on weighted grids).

Time:  O(b^d)  where b = branching factor, d = solution depth
Space: O(b*d)  (linear in solution depth)
"""

from typing import Tuple, Optional
import time

from algorithms.base import SearchAlgorithm, SearchNode, SearchResult


class IDDFS(SearchAlgorithm):
    """Iterative Deepening DFS with increasing depth limits."""

    def search(self) -> SearchResult:
        start_time = time.perf_counter()

        # Check if start == goal
        if self.start == self.goal:
            self._record_step("found_goal", self.start)
            elapsed = (time.perf_counter() - start_time) * 1000
            return self._make_result([self.start], 0, elapsed)

        # Maximum possible depth is the number of cells
        max_depth = self.grid.width * self.grid.height

        for depth_limit in range(0, max_depth):
            self._record_step(
                "explore", self.start,
                depth=0,
                iteration=depth_limit,
            )

            result_node = self._depth_limited_search(
                self.start, depth_limit
            )

            if result_node is not None:
                path = self._reconstruct_path(result_node)
                self._record_step(
                    "found_goal", result_node.state,
                    g_cost=result_node.g_cost, depth=result_node.depth,
                    iteration=depth_limit,
                )
                elapsed = (time.perf_counter() - start_time) * 1000
                return self._make_result(path, result_node.g_cost, elapsed)

        # No path found
        self._record_step("no_path", self.start)
        elapsed = (time.perf_counter() - start_time) * 1000
        return self._make_result([], 0, elapsed)

    def _depth_limited_search(
        self,
        start: Tuple[int, int],
        depth_limit: int,
    ) -> Optional[SearchNode]:
        """
        Run a depth-limited DFS from the given start position.

        Uses an iterative stack-based approach rather than recursion
        to avoid Python's recursion limit on large grids.

        Args:
            start: Starting (row, col) position.
            depth_limit: Maximum depth to explore.

        Returns:
            The goal SearchNode if found, else None.
        """
        start_node = SearchNode(state=start, parent=None, g_cost=0, depth=0)
        stack = [start_node]

        # Track visited states WITH depth to allow re-exploration at shallower depths
        visited = {}  # state -> shallowest depth seen

        while stack:
            node = stack.pop()

            # Skip if we've visited this state at a shallower or equal depth
            if node.state in visited and visited[node.state] <= node.depth:
                continue

            visited[node.state] = node.depth
            self._explored_count += 1
            self._record_step(
                "explore", node.state,
                g_cost=node.g_cost, depth=node.depth,
            )

            # Goal test
            if node.state == self.goal:
                return node

            # Don't expand beyond the depth limit
            if node.depth >= depth_limit:
                continue

            neighbors = self.grid.get_neighbors(*node.state)
            for nr, nc in reversed(neighbors):
                neighbor_state = (nr, nc)
                # Only add if not visited at a shallower depth
                if neighbor_state not in visited or visited[neighbor_state] > node.depth + 1:
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

        return None
