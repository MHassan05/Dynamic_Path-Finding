import tkinter as tk
from grid_input import GridInputWindow
from visualizer import Visualizer


def main():
    root = tk.Tk()
    root.withdraw()   # hide the root window — we use it only as the Tk() base

    def on_setup_done(rows, cols):
        viz = Visualizer(root, rows, cols)
        # When visualizer window is closed, exit the whole app
        viz.window.protocol("WM_DELETE_WINDOW", root.destroy)

    # Show setup window as a Toplevel too
    setup = tk.Toplevel(root)
    GridInputWindow(setup, callback=on_setup_done)

    root.mainloop()


if __name__ == "__main__":
    main()