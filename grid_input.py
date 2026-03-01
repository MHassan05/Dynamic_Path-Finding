import tkinter as tk
from tkinter import messagebox


class GridInputWindow:
    def __init__(self, window, callback):
        self.window = window      # this is a Toplevel passed from main.py
        self.callback = callback

        self.window.title("Pathfinding Agent - Setup")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.window.configure(bg="#1e1e2e")

        self.rows_var = tk.StringVar(value="8")
        self.cols_var = tk.StringVar(value="8")

        self._build_ui()

    def _build_ui(self):
        tk.Label(
            self.window,
            text="Dynamic Pathfinding Agent",
            font=("Arial", 16, "bold"),
            bg="#1e1e2e", fg="#cdd6f4"
        ).pack(pady=20)

        tk.Label(
            self.window,
            text="Enter Grid Dimensions",
            font=("Arial", 11),
            bg="#1e1e2e", fg="#a6adc8"
        ).pack(pady=5)

        input_frame = tk.Frame(self.window, bg="#1e1e2e")
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Rows:", font=("Arial", 12),
                 bg="#1e1e2e", fg="#cdd6f4", width=8, anchor="e"
        ).grid(row=0, column=0, padx=5, pady=8)

        tk.Entry(input_frame, textvariable=self.rows_var,
                 font=("Arial", 12), width=10,
                 bg="#313244", fg="#cdd6f4",
                 insertbackground="white", relief="flat", bd=4
        ).grid(row=0, column=1, padx=5, pady=8)

        tk.Label(input_frame, text="Columns:", font=("Arial", 12),
                 bg="#1e1e2e", fg="#cdd6f4", width=8, anchor="e"
        ).grid(row=1, column=0, padx=5, pady=8)

        tk.Entry(input_frame, textvariable=self.cols_var,
                 font=("Arial", 12), width=10,
                 bg="#313244", fg="#cdd6f4",
                 insertbackground="white", relief="flat", bd=4
        ).grid(row=1, column=1, padx=5, pady=8)

        tk.Label(self.window,
                 text="(Min: 8x8  |  Max: 20x20)",
                 font=("Arial", 9),
                 bg="#1e1e2e", fg="#6c7086"
        ).pack()

        tk.Button(
            self.window,
            text="Continue",
            font=("Arial", 12, "bold"),
            bg="#89b4fa", fg="#1e1e2e",
            activebackground="#74c7ec",
            relief="flat", padx=20, pady=6,
            cursor="hand2",
            command=self._on_continue
        ).pack(pady=15)

    def _on_continue(self):
        rows, cols = self._validate()
        if rows is None:
            return
        self.window.destroy()     # close setup window
        self.callback(rows, cols) # hand off to main.py

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

        if rows < 8 or cols < 8:
            messagebox.showerror("Error", "Minimum grid size is 8x8!")
            return None, None

        if rows > 20 or cols > 20:
            messagebox.showerror("Error", "Maximum grid size is 20x20!")
            return None, None

        return rows, cols