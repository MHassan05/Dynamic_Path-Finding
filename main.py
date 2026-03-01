import tkinter as tk
from grid_input import GridInputWindow
from visualizer import Visualizer


def on_setup_done(rows, cols):
    Visualizer(rows, cols)


def main():
    root = tk.Tk()
    app = GridInputWindow(root, callback=on_setup_done)
    root.mainloop()


if __name__ == "__main__":
    main()