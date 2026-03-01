import tkinter as tk
from tkinter import messagebox
import random


class Visualizer:
    EMPTY    = 0
    WALL     = 1
    START    = 2
    GOAL     = 3
    VISITED  = 4
    FRONTIER = 5
    PATH     = 6

    COLORS = {
        EMPTY   : "white",
        WALL    : "black",
        START   : "green",
        GOAL    : "red",
        VISITED : "lightblue",
        FRONTIER: "yellow",
        PATH    : "lime green",
    }

    def __init__(self, root, rows, cols):
        self.rows = rows
        self.cols = cols

        self.grid         = [[self.EMPTY] * cols for _ in range(rows)]
        self.start_node   = None
        self.goal_node    = None
        self.current_mode = "wall"

        self.nodes_label  = None
        self.cost_label   = None
        self.time_label   = None

        self.window = tk.Toplevel(root)
        self.window.title("Pathfinding Visualizer")
        self.window.state("zoomed")
        self.window.configure(bg="#f0f0f0")

        # Read screen size after maximizing
        self.window.update_idletasks()
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()

        # Top bar is roughly 120px tall, leave rest for grid
        TOP_H = 120
        grid_area_w = screen_w - 20
        grid_area_h = screen_h - TOP_H - 60  # 60 for taskbar

        self.cell_size = min(grid_area_w // cols, grid_area_h // rows)

        self._build_ui()

    # ------------------------------------------------------------------ #
    #  UI BUILDING
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        # ── Top control bar ──
        top = tk.Frame(self.window, bg="#d0d0d0", bd=1, relief="solid")
        top.pack(side="top", fill="x")
        self._build_top_bar(top)

        # ── Grid area below ──
        grid_frame = tk.Frame(self.window, bg="#f0f0f0")
        grid_frame.pack(side="top", fill="both", expand=True)
        self._build_grid_panel(grid_frame)

    def _build_top_bar(self, parent):

        # ── Section 1: Drawing Tools ──
        draw = tk.LabelFrame(parent, text="Drawing Tools", bg="#d0d0d0", font=("Arial", 9))
        draw.pack(side="left", padx=8, pady=6)

        b = dict(width=9, font=("Arial", 9))
        tk.Button(draw, text="Set Start", **b, command=lambda: self._set_mode("start")).grid(row=0, column=0, padx=3, pady=3)
        tk.Button(draw, text="Set Goal",  **b, command=lambda: self._set_mode("goal")).grid(row=0, column=1, padx=3, pady=3)
        tk.Button(draw, text="Draw Wall", **b, command=lambda: self._set_mode("wall")).grid(row=0, column=2, padx=3, pady=3)
        tk.Button(draw, text="Erase",     **b, command=lambda: self._set_mode("erase")).grid(row=0, column=3, padx=3, pady=3)
        tk.Button(draw, text="Clear All", **b, command=self._clear_grid).grid(row=0, column=4, padx=3, pady=3)

        self.mode_label = tk.Label(draw, text="Mode: Draw Wall",
                                   font=("Arial", 9, "italic"), bg="#d0d0d0", fg="blue")
        self.mode_label.grid(row=1, column=0, columnspan=5, pady=(0, 3))

        # ── Section 2: Random Maze ──
        maze = tk.LabelFrame(parent, text="Random Maze", bg="#d0d0d0", font=("Arial", 9))
        maze.pack(side="left", padx=8, pady=6)

        tk.Label(maze, text="Density %:", font=("Arial", 9), bg="#d0d0d0").grid(row=0, column=0, padx=4, pady=4)
        self.density_var = tk.IntVar(value=30)
        tk.Spinbox(maze, from_=10, to=70, textvariable=self.density_var,
                   width=5, font=("Arial", 9)).grid(row=0, column=1, padx=4)
        tk.Button(maze, text="Generate", width=9, font=("Arial", 9),
                  command=self._generate_maze).grid(row=0, column=2, padx=6, pady=4)

        # ── Section 3: Algorithm ──
        algo = tk.LabelFrame(parent, text="Algorithm", bg="#d0d0d0", font=("Arial", 9))
        algo.pack(side="left", padx=8, pady=6)

        self.algo_var = tk.StringVar(value="A*")
        tk.Radiobutton(algo, text="A* Search",  variable=self.algo_var,
                       value="A*",   bg="#d0d0d0", font=("Arial", 9)).pack(anchor="w", padx=6, pady=2)
        tk.Radiobutton(algo, text="Greedy BFS", variable=self.algo_var,
                       value="GBFS", bg="#d0d0d0", font=("Arial", 9)).pack(anchor="w", padx=6, pady=2)

        # ── Section 4: Heuristic ──
        heur = tk.LabelFrame(parent, text="Heuristic", bg="#d0d0d0", font=("Arial", 9))
        heur.pack(side="left", padx=8, pady=6)

        self.heuristic_var = tk.StringVar(value="Manhattan")
        tk.Radiobutton(heur, text="Manhattan", variable=self.heuristic_var,
                       value="Manhattan", bg="#d0d0d0", font=("Arial", 9)).pack(anchor="w", padx=6, pady=2)
        tk.Radiobutton(heur, text="Euclidean", variable=self.heuristic_var,
                       value="Euclidean", bg="#d0d0d0", font=("Arial", 9)).pack(anchor="w", padx=6, pady=2)

        # ── Section 5: Options ──
        opts = tk.LabelFrame(parent, text="Options", bg="#d0d0d0", font=("Arial", 9))
        opts.pack(side="left", padx=8, pady=6)

        self.dynamic_var = tk.BooleanVar(value=False)
        tk.Checkbutton(opts, text="Dynamic Mode", variable=self.dynamic_var,
                       bg="#d0d0d0", font=("Arial", 9)).pack(padx=6, pady=6)

        # ── Section 6: Run / Reset ──
        run = tk.LabelFrame(parent, text="Run", bg="#d0d0d0", font=("Arial", 9))
        run.pack(side="left", padx=8, pady=6)

        tk.Button(run, text="Run", width=9, bg="#4CAF50", fg="white",
                  font=("Arial", 10, "bold"), command=self._run).grid(row=0, column=0, padx=6, pady=4)
        tk.Button(run, text="Reset", width=9, font=("Arial", 9),
                  command=self._reset_search).grid(row=0, column=1, padx=6, pady=4)

        # ── Section 7: Metrics ──
        met = tk.LabelFrame(parent, text="Metrics", bg="#d0d0d0", font=("Arial", 9))
        met.pack(side="left", padx=8, pady=6)

        tk.Label(met, text="Nodes:", font=("Arial", 9), bg="#d0d0d0").grid(row=0, column=0, padx=4, pady=2, sticky="w")
        self.nodes_label = tk.Label(met, text="0", font=("Arial", 9, "bold"), bg="#d0d0d0", fg="blue")
        self.nodes_label.grid(row=0, column=1, padx=4, sticky="w")

        tk.Label(met, text="Cost:", font=("Arial", 9), bg="#d0d0d0").grid(row=1, column=0, padx=4, pady=2, sticky="w")
        self.cost_label = tk.Label(met, text="0", font=("Arial", 9, "bold"), bg="#d0d0d0", fg="blue")
        self.cost_label.grid(row=1, column=1, padx=4, sticky="w")

        tk.Label(met, text="Time(ms):", font=("Arial", 9), bg="#d0d0d0").grid(row=2, column=0, padx=4, pady=2, sticky="w")
        self.time_label = tk.Label(met, text="0", font=("Arial", 9, "bold"), bg="#d0d0d0", fg="blue")
        self.time_label.grid(row=2, column=1, padx=4, sticky="w")

    def _build_grid_panel(self, parent):
        canvas_w = self.cols * self.cell_size
        canvas_h = self.rows * self.cell_size

        self.canvas = tk.Canvas(parent, width=canvas_w, height=canvas_h,
                                bg="white", bd=1, relief="solid")
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")

        self.canvas.bind("<Button-1>",  self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)

        self._draw_grid()

    # ------------------------------------------------------------------ #
    #  GRID DRAWING
    # ------------------------------------------------------------------ #
    def _draw_grid(self):
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                self._draw_cell(r, c)

    def _draw_cell(self, r, c):
        x1 = c * self.cell_size
        y1 = r * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        color = self.COLORS[self.grid[r][c]]
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

    # ------------------------------------------------------------------ #
    #  MOUSE INTERACTIONS
    # ------------------------------------------------------------------ #
    def _get_cell(self, event):
        c = int(event.x // self.cell_size)
        r = int(event.y // self.cell_size)
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return r, c
        return None, None

    def _on_click(self, event):
        r, c = self._get_cell(event)
        if r is not None:
            self._apply_mode(r, c)

    def _on_drag(self, event):
        if self.current_mode in ("wall", "erase"):
            r, c = self._get_cell(event)
            if r is not None:
                self._apply_mode(r, c)

    def _apply_mode(self, r, c):
        if self.current_mode == "wall":
            if self.grid[r][c] == self.EMPTY:
                self.grid[r][c] = self.WALL

        elif self.current_mode == "erase":
            if self.grid[r][c] == self.START:
                self.start_node = None
            elif self.grid[r][c] == self.GOAL:
                self.goal_node = None
            self.grid[r][c] = self.EMPTY

        elif self.current_mode == "start":
            if self.start_node:
                self.grid[self.start_node[0]][self.start_node[1]] = self.EMPTY
            self.start_node = (r, c)
            self.grid[r][c] = self.START

        elif self.current_mode == "goal":
            if self.goal_node:
                self.grid[self.goal_node[0]][self.goal_node[1]] = self.EMPTY
            self.goal_node = (r, c)
            self.grid[r][c] = self.GOAL

        self._draw_cell(r, c)

    def _set_mode(self, mode):
        self.current_mode = mode
        self.mode_label.config(text=f"Mode: {mode.replace('_', ' ').title()}")

    # ------------------------------------------------------------------ #
    #  MAZE GENERATION
    # ------------------------------------------------------------------ #
    def _generate_maze(self):
        density = self.density_var.get() / 100.0
        self._clear_grid()
        for r in range(self.rows):
            for c in range(self.cols):
                if random.random() < density:
                    self.grid[r][c] = self.WALL
        self._draw_grid()

    # ------------------------------------------------------------------ #
    #  CLEAR & RESET
    # ------------------------------------------------------------------ #
    def _clear_grid(self):
        self.grid       = [[self.EMPTY] * self.cols for _ in range(self.rows)]
        self.start_node = None
        self.goal_node  = None
        self._reset_metrics()
        if hasattr(self, "canvas"):
            self._draw_grid()

    def _reset_search(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] in (self.VISITED, self.FRONTIER, self.PATH):
                    self.grid[r][c] = self.EMPTY
        self._reset_metrics()
        self._draw_grid()

    def _reset_metrics(self):
        if self.nodes_label:
            self.nodes_label.config(text="0")
        if self.cost_label:
            self.cost_label.config(text="0")
        if self.time_label:
            self.time_label.config(text="0")

    # ------------------------------------------------------------------ #
    #  RUN
    # ------------------------------------------------------------------ #
    def _run(self):
        if not self.start_node:
            messagebox.showwarning("Missing", "Please set a Start node (green).")
            return
        if not self.goal_node:
            messagebox.showwarning("Missing", "Please set a Goal node (red).")
            return

        self._reset_search()

        algo      = self.algo_var.get()
        heuristic = self.heuristic_var.get()
        dynamic   = self.dynamic_var.get()

        if dynamic:
            from algorithms.dynamic import DynamicRunner
            runner = DynamicRunner(self, algo, heuristic)
            path   = runner.run()
        else:
            if algo == "A*":
                from algorithms.astar import AStar
                runner = AStar(self, heuristic)
            else:
                from algorithms.gbfs import GBFS
                runner = GBFS(self, heuristic)
            path = runner.run()

        if path is None:
            messagebox.showwarning("No Path", "No path found! Try removing some walls.")

    # ------------------------------------------------------------------ #
    #  PUBLIC HELPERS — called by algorithm classes
    # ------------------------------------------------------------------ #
    def update_cell(self, r, c, state):
        if self.grid[r][c] not in (self.START, self.GOAL):
            self.grid[r][c] = state
            self._draw_cell(r, c)
            self.window.update()

    def update_metrics(self, nodes_visited, path_cost, elapsed_ms):
        self.nodes_label.config(text=str(nodes_visited))
        self.cost_label.config(text=str(path_cost))
        self.time_label.config(text=f"{elapsed_ms:.1f}")

    def get_grid(self):
        return self.grid

    def get_start(self):
        return self.start_node

    def get_goal(self):
        return self.goal_node