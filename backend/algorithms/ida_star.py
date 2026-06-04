"""
Iterative Deepening A* (IDA*) algorithm.

Combines A*'s heuristic guidance with iterative deepening's linear
space usage. Each iteration performs a depth-first search with an
f-cost threshold. If no solution is found, the threshold is raised
to the minimum f-cost that exceeded the current threshold.

Guarantees optimal paths with admissible heuristics. Uses O(bd) space.

Time:  O(b^d) worst case, but often much better with good heuristics
Space: O(b*d) — linear in solution depth
"""

from typing import Tuple, Optional
import time

from algorithms.base import SearchAlgorithm, SearchNode, SearchResult
from utils.heuristics import manhattan_distance


class IDAStar(SearchAlgorithm):
    """IDA* — Iterative Deepening A* with f-cost thresholds."""

    def search(self) -> SearchResult:
        start_time = time.perf_counter()

        # Check if start == goal
        if self.start == self.goal:
            self._record_step("found_goal", self.start)
            elapsed = (time.perf_counter() - start_time) * 1000
            return self._make_result([self.start], 0, elapsed)

        # Initial threshold is h(start)
        threshold = manhattan_distance(self.start, self.goal)
        start_node = SearchNode(
            state=self.start, parent=None,
            g_cost=0, h_cost=threshold, depth=0,
        )

        iteration = 0
        while True:
            self._record_step(
                "explore", self.start,
                g_cost=0, h_cost=start_node.h_cost,
                depth=0, threshold=threshold, iteration=iteration,
            )

            result, min_exceeded = self._bounded_dfs(start_node, threshold)

            if result is not None:
                # Found the goal
                path = self._reconstruct_path(result)
                self._record_step(
                    "found_goal", result.state,
                    g_cost=result.g_cost, h_cost=0, depth=result.depth,
                    threshold=threshold, iteration=iteration,
                )
                elapsed = (time.perf_counter() - start_time) * 1000
                return self._make_result(path, result.g_cost, elapsed)

            if min_exceeded == float('inf'):
                # No path exists
                break

            # Raise the threshold to the minimum f-cost that exceeded it
            threshold = min_exceeded
            iteration += 1

        self._record_step("no_path", self.start)
        elapsed = (time.perf_counter() - start_time) * 1000
        return self._make_result([], 0, elapsed)

    def _bounded_dfs(
        self,
        node: SearchNode,
        threshold: float,
    ) -> Tuple[Optional[SearchNode], float]:
        """
        Iterative (stack-based) depth-first search bounded by f-cost threshold.

        Returns:
            (goal_node, min_exceeded) where:
            - goal_node is the goal SearchNode if found, else None
            - min_exceeded is the smallest f-cost that exceeded the threshold
              (used to set the next iteration's threshold)
        """
        # Use an iterative stack to avoid Python recursion limits
        # Stack entries: (node, is_processed)
        stack = [(node, False)]
        min_exceeded = float('inf')

        # Track visited states with their best g-cost to avoid redundant work
        visited = {}

        while stack:
            current, processed = stack.pop()

            f = current.g_cost + current.h_cost

            # If f exceeds threshold, track it and skip
            if f > threshold:
                min_exceeded = min(min_exceeded, f)
                continue

            # Skip if we've already visited with a better or equal g-cost
            if current.state in visited and visited[current.state] <= current.g_cost:
                continue

            visited[current.state] = current.g_cost
            self._explored_count += 1
            self._record_step(
                "explore", current.state,
                g_cost=current.g_cost, h_cost=current.h_cost,
                depth=current.depth,
            )

            # Goal test
            if current.state == self.goal:
                return current, threshold

            # Push neighbors (reversed so first neighbor is explored first)
            neighbors = self.grid.get_neighbors(*current.state)
            for nr, nc in reversed(neighbors):
                neighbor_state = (nr, nc)
                move_cost = self.grid.get_cost(nr, nc)
                new_g = current.g_cost + move_cost
                h = manhattan_distance(neighbor_state, self.goal)

                child = SearchNode(
                    state=neighbor_state,
                    parent=current,
                    g_cost=new_g,
                    h_cost=h,
                    depth=current.depth + 1,
                )

                child_f = new_g + h
                if child_f > threshold:
                    min_exceeded = min(min_exceeded, child_f)
                    continue

                if neighbor_state not in visited or visited[neighbor_state] > new_g:
                    stack.append((child, False))
                    self._record_step(
                        "add_to_frontier", neighbor_state,
                        g_cost=new_g, h_cost=h, depth=child.depth,
                    )

            self._update_frontier_size(len(stack))

        return None, min_exceeded
