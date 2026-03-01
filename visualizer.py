import tkinter as tk
from tkinter import messagebox
import random


class Visualizer:
    # Cell states
    EMPTY    = 0
    WALL     = 1
    START    = 2
    GOAL     = 3
    VISITED  = 4
    FRONTIER = 5
    PATH     = 6

    # Cell colors
    COLORS = {
        EMPTY   : "white",
        WALL    : "black",
        START   : "green",
        GOAL    : "red",
        VISITED : "lightblue",
        FRONTIER: "yellow",
        PATH    : "lime green",
    }

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cell_size = 28

        self.grid = [[self.EMPTY] * cols for _ in range(rows)]
        self.start_node = None
        self.goal_node  = None
        self.current_mode = "wall"

        # Labels initialized to None — set in _build_ui
        self.nodes_label = None
        self.cost_label  = None
        self.time_label  = None

        self.root = tk.Tk()
        self.root.title("Pathfinding Visualizer")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(True, True)

        self._build_ui()
        self.root.mainloop()

    # ------------------------------------------------------------------ #
    #  UI BUILDING
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        # ---- Top instruction label ----
        tk.Label(
            self.root,
            text="Set Start & Goal, draw walls, pick algorithm, then click Run!",
            font=("Arial", 10), bg="#f0f0f0"
        ).pack(pady=4)

        # ---- Control panel ----
        control = tk.Frame(self.root, bg="#f0f0f0")
        control.pack(fill="x", padx=10, pady=4)

        # Row 0 — Drawing tools
        draw_frame = tk.LabelFrame(control, text="Drawing Tools", bg="#f0f0f0", font=("Arial", 9))
        draw_frame.grid(row=0, column=0, padx=6, pady=2, sticky="w")

        tk.Button(draw_frame, text="Set Start", width=9, command=lambda: self._set_mode("start")).grid(row=0, column=0, padx=3, pady=2)
        tk.Button(draw_frame, text="Set Goal",  width=9, command=lambda: self._set_mode("goal")).grid(row=0, column=1, padx=3, pady=2)
        tk.Button(draw_frame, text="Draw Wall", width=9, command=lambda: self._set_mode("wall")).grid(row=0, column=2, padx=3, pady=2)
        tk.Button(draw_frame, text="Erase",     width=9, command=lambda: self._set_mode("erase")).grid(row=0, column=3, padx=3, pady=2)
        tk.Button(draw_frame, text="Clear All", width=9, command=self._clear_grid).grid(row=0, column=4, padx=3, pady=2)

        # Row 0 — Random maze
        maze_frame = tk.LabelFrame(control, text="Random Maze", bg="#f0f0f0", font=("Arial", 9))
        maze_frame.grid(row=0, column=1, padx=6, pady=2, sticky="w")

        tk.Label(maze_frame, text="Density %:", bg="#f0f0f0", font=("Arial", 9)).grid(row=0, column=0, padx=3)
        self.density_var = tk.IntVar(value=30)
        tk.Spinbox(maze_frame, from_=10, to=70, textvariable=self.density_var, width=5).grid(row=0, column=1, padx=3)
        tk.Button(maze_frame, text="Generate", width=8, command=self._generate_maze).grid(row=0, column=2, padx=3, pady=2)

        # Row 1 — Algorithm & Heuristic
        algo_frame = tk.LabelFrame(control, text="Algorithm & Heuristic", bg="#f0f0f0", font=("Arial", 9))
        algo_frame.grid(row=1, column=0, padx=6, pady=2, sticky="w")

        self.algo_var = tk.StringVar(value="A*")
        tk.Radiobutton(algo_frame, text="A* Search",  variable=self.algo_var, value="A*",   bg="#f0f0f0").grid(row=0, column=0, padx=6)
        tk.Radiobutton(algo_frame, text="Greedy BFS", variable=self.algo_var, value="GBFS", bg="#f0f0f0").grid(row=0, column=1, padx=6)

        self.heuristic_var = tk.StringVar(value="Manhattan")
        tk.Radiobutton(algo_frame, text="Manhattan", variable=self.heuristic_var, value="Manhattan", bg="#f0f0f0").grid(row=0, column=2, padx=6)
        tk.Radiobutton(algo_frame, text="Euclidean", variable=self.heuristic_var, value="Euclidean", bg="#f0f0f0").grid(row=0, column=3, padx=6)

        # Row 1 — Dynamic mode & Run
        run_frame = tk.LabelFrame(control, text="Run", bg="#f0f0f0", font=("Arial", 9))
        run_frame.grid(row=1, column=1, padx=6, pady=2, sticky="w")

        self.dynamic_var = tk.BooleanVar(value=False)
        tk.Checkbutton(run_frame, text="Dynamic Mode", variable=self.dynamic_var, bg="#f0f0f0").grid(row=0, column=0, padx=6)
        tk.Button(run_frame, text="Run",   width=10, bg="#4CAF50", fg="white",
                  font=("Arial", 10, "bold"), command=self._run).grid(row=0, column=1, padx=6, pady=4)
        tk.Button(run_frame, text="Reset", width=10,
                  command=self._reset_search).grid(row=0, column=2, padx=6, pady=4)

        # ---- Mode indicator ----
        self.mode_label = tk.Label(
            self.root, text="Mode: Draw Wall",
            font=("Arial", 10, "bold"), bg="#f0f0f0", fg="blue"
        )
        self.mode_label.pack()

        # ---- Metrics dashboard (built BEFORE canvas so labels exist) ----
        metrics_frame = tk.Frame(self.root, bg="#f0f0f0")
        metrics_frame.pack(pady=4)

        tk.Label(metrics_frame, text="Nodes Visited:", bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=0, padx=10)
        self.nodes_label = tk.Label(metrics_frame, text="0", bg="#f0f0f0", font=("Arial", 10, "bold"), fg="blue")
        self.nodes_label.grid(row=0, column=1, padx=4)

        tk.Label(metrics_frame, text="Path Cost:", bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=2, padx=10)
        self.cost_label = tk.Label(metrics_frame, text="0", bg="#f0f0f0", font=("Arial", 10, "bold"), fg="blue")
        self.cost_label.grid(row=0, column=3, padx=4)

        tk.Label(metrics_frame, text="Time (ms):", bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=4, padx=10)
        self.time_label = tk.Label(metrics_frame, text="0", bg="#f0f0f0", font=("Arial", 10, "bold"), fg="blue")
        self.time_label.grid(row=0, column=5, padx=4)

        # ---- Canvas (built AFTER metrics) ----
        canvas_w = self.cols * self.cell_size
        canvas_h = self.rows * self.cell_size
        self.canvas = tk.Canvas(
            self.root, width=canvas_w, height=canvas_h,
            bg="white", bd=1, relief="solid"
        )
        self.canvas.pack(padx=10, pady=6)

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
        c = event.x // self.cell_size
        r = event.y // self.cell_size
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
        self.grid = [[self.EMPTY] * self.cols for _ in range(self.rows)]
        self.start_node = None
        self.goal_node  = None
        self._reset_metrics()
        self._draw_grid() if hasattr(self, 'canvas') else None

    def _reset_search(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] in (self.VISITED, self.FRONTIER, self.PATH):
                    self.grid[r][c] = self.EMPTY
        self._reset_metrics()
        self._draw_grid()

    def _reset_metrics(self):
        # Guard in case labels not built yet
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

        # Algorithm classes will be plugged in here next
        messagebox.showinfo(
            "Ready to Run",
            f"Algorithm : {algo}\n"
            f"Heuristic : {heuristic}\n"
            f"Dynamic   : {dynamic}\n\n"
            f"Start : {self.start_node}\n"
            f"Goal  : {self.goal_node}\n\n"
            "(Algorithm module coming next!)"
        )

    # ------------------------------------------------------------------ #
    #  PUBLIC HELPERS — used by algorithm classes later
    # ------------------------------------------------------------------ #
    def update_cell(self, r, c, state):
        if self.grid[r][c] not in (self.START, self.GOAL):
            self.grid[r][c] = state
            self._draw_cell(r, c)
            self.root.update()

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