import heapq
import time
from algorithms.heuristics import get_heuristic


class GBFS:
    def __init__(self, visualizer, heuristic_name):
        self.viz       = visualizer
        self.heuristic = get_heuristic(heuristic_name)

    def get_neighbors(self, row, col):
        """Returns valid 4-directional neighbors (up, down, left, right)."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < self.viz.rows and 0 <= c < self.viz.cols:
                if self.viz.grid[r][c] != self.viz.WALL:
                    neighbors.append((r, c))
        return neighbors

    def reconstruct_path(self, came_from, current):
        """Traces back from goal to start using came_from map."""
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def run(self):
        start      = self.viz.get_start()
        goal       = self.viz.get_goal()
        start_time = time.time()

        # Priority queue: (h_score, node) — only heuristic, no g cost
        open_heap = []
        heapq.heappush(open_heap, (self.heuristic(start, goal), start))

        open_set   = {start}
        closed_set = set()
        came_from  = {}

        nodes_visited = 0

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if current in closed_set:
                continue

            open_set.discard(current)
            closed_set.add(current)
            nodes_visited += 1

            # Color as visited (blue)
            self.viz.update_cell(current[0], current[1], self.viz.VISITED)

            # Goal reached
            if current == goal:
                path      = self.reconstruct_path(came_from, current)
                path_cost = len(path)
                elapsed   = (time.time() - start_time) * 1000

                # Color final path green
                for r, c in path:
                    self.viz.update_cell(r, c, self.viz.PATH)

                self.viz.update_metrics(nodes_visited, path_cost, elapsed)
                return path

            # Explore neighbors
            for neighbor in self.get_neighbors(current[0], current[1]):
                if neighbor in closed_set or neighbor in open_set:
                    continue

                came_from[neighbor] = current
                h = self.heuristic(neighbor, goal)
                heapq.heappush(open_heap, (h, neighbor))
                open_set.add(neighbor)

                # Color as frontier (yellow)
                self.viz.update_cell(neighbor[0], neighbor[1], self.viz.FRONTIER)

        # No path found
        elapsed = (time.time() - start_time) * 1000
        self.viz.update_metrics(nodes_visited, 0, elapsed)
        return None