import tkinter as tk
from tkinter import messagebox


class GridInputWindow:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback   # main.py passes on_setup_done here

        self.root.title("Pathfinding Agent - Setup")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.rows_var = tk.StringVar(value="20")
        self.cols_var = tk.StringVar(value="20")

        self._build_ui()

    def _build_ui(self):
        tk.Label(
            self.root,
            text="Dynamic Pathfinding Agent",
            font=("Arial", 16, "bold"),
            bg="#1e1e2e",
            fg="#cdd6f4"
        ).pack(pady=20)

        tk.Label(
            self.root,
            text="Enter Grid Dimensions",
            font=("Arial", 11),
            bg="#1e1e2e",
            fg="#a6adc8"
        ).pack(pady=5)

        input_frame = tk.Frame(self.root, bg="#1e1e2e")
        input_frame.pack(pady=20)

        tk.Label(
            input_frame, text="Rows:", font=("Arial", 12),
            bg="#1e1e2e", fg="#cdd6f4", width=8, anchor="e"
        ).grid(row=0, column=0, padx=5, pady=8)

        tk.Entry(
            input_frame, textvariable=self.rows_var,
            font=("Arial", 12), width=10,
            bg="#313244", fg="#cdd6f4",
            insertbackground="white", relief="flat", bd=4
        ).grid(row=0, column=1, padx=5, pady=8)

        tk.Label(
            input_frame, text="Columns:", font=("Arial", 12),
            bg="#1e1e2e", fg="#cdd6f4", width=8, anchor="e"
        ).grid(row=1, column=0, padx=5, pady=8)

        tk.Entry(
            input_frame, textvariable=self.cols_var,
            font=("Arial", 12), width=10,
            bg="#313244", fg="#cdd6f4",
            insertbackground="white", relief="flat", bd=4
        ).grid(row=1, column=1, padx=5, pady=8)

        tk.Label(
            self.root,
            text="(Min: 5x5  |  Max: 50x50)",
            font=("Arial", 9),
            bg="#1e1e2e",
            fg="#6c7086"
        ).pack()

        tk.Button(
            self.root,
            text="Continue →",
            font=("Arial", 12, "bold"),
            bg="#89b4fa",
            fg="#1e1e2e",
            activebackground="#74c7ec",
            activeforeground="#1e1e2e",
            relief="flat",
            padx=20,
            pady=6,
            cursor="hand2",
            command=self._on_continue
        ).pack(pady=15)

    def _on_continue(self):
        rows, cols = self._validate()
        if rows is None:
            return
        self.root.destroy()        # close setup window
        self.callback(rows, cols)  # hand control back to main.py

    def _validate(self):
        rows_val = self.rows_var.get().strip()
        cols_val = self.cols_var.get().strip()

        if not rows_val or not cols_val:
            messagebox.showerror("Error", "Please enter both Rows and Columns!")
            return None, None

        if not rows_val.isdigit() or not cols_val.isdigit():
            messagebox.showerror("Error", "Rows and Columns must be whole numbers!")
            return None, None

        rows, cols = int(rows_val), int(cols_val)

        if rows < 5 or cols < 5:
            messagebox.showerror("Error", "Minimum grid size is 5x5!")
            return None, None

        if rows > 50 or cols > 50:
            messagebox.showerror("Error", "Maximum grid size is 50x50!")
            return None, None

        return rows, cols