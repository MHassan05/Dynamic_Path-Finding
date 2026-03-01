import random
import time
from algorithms.astar import AStar
from algorithms.gbfs  import GBFS


class DynamicRunner:
    """
    Wraps A* or GBFS with dynamic obstacle spawning.
    While the agent moves along the path, new walls may randomly
    appear. If one blocks the current path, the agent re-plans
    from its current position.
    """

    SPAWN_PROB   = 0.15   # 15% chance a new wall spawns each step
    STEP_DELAY   = 0.08   # seconds between each agent step (for animation)

    def __init__(self, visualizer, algo_name, heuristic_name):
        self.viz           = visualizer
        self.algo_name     = algo_name
        self.heuristic_name = heuristic_name

    def _make_algo(self):
        if self.algo_name == "A*":
            return AStar(self.viz, self.heuristic_name)
        else:
            return GBFS(self.viz, self.heuristic_name)

    def _spawn_obstacle(self, current_path_set):
        """
        Randomly place a wall on an empty cell.
        Returns True if the new wall landed on the current path.
        """
        empty_cells = [
            (r, c)
            for r in range(self.viz.rows)
            for c in range(self.viz.cols)
            if self.viz.grid[r][c] == self.viz.EMPTY
        ]

        if not empty_cells:
            return False

        r, c = random.choice(empty_cells)
        self.viz.grid[r][c] = self.viz.WALL
        self.viz.update_cell(r, c, self.viz.WALL)

        return (r, c) in current_path_set

    def run(self):
        start_time    = time.time()
        total_visited = 0
        total_cost    = 0

        current_start = self.viz.get_start()
        goal          = self.viz.get_goal()

        while True:
            # Plan a path from current position to goal
            # Temporarily move start marker if re-planning mid-way
            original_start = self.viz.start_node
            self.viz.start_node = current_start

            algo = self._make_algo()
            path = algo.run()

            # Restore original start marker
            self.viz.start_node = original_start

            if path is None:
                # No path exists at all
                self.viz.update_metrics(total_visited, 0,
                                        (time.time() - start_time) * 1000)
                return None

            total_visited += len(path)
            path_set = set(path)

            # Walk along the path step by step
            for i, step in enumerate(path):
                time.sleep(self.STEP_DELAY)

                # Color current agent position
                self.viz.update_cell(step[0], step[1], self.viz.PATH)
                current_start = step

                # Try spawning a random obstacle
                if random.random() < self.SPAWN_PROB:
                    remaining_path = set(path[i:])
                    blocked = self._spawn_obstacle(remaining_path)

                    if blocked:
                        # Re-plan from current position
                        total_cost += i + 1
                        break

                # Reached goal
                if step == goal:
                    total_cost += i + 1
                    elapsed = (time.time() - start_time) * 1000
                    self.viz.update_metrics(total_visited, total_cost, elapsed)
                    return path
            else:
                # Loop finished without break = goal reached
                elapsed = (time.time() - start_time) * 1000
                self.viz.update_metrics(total_visited, total_cost, elapsed)
                return path