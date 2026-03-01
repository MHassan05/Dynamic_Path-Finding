import math


def manhattan(a, b):
    """Manhattan distance: sum of absolute differences in row and col."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a, b):
    """Euclidean distance: straight line distance between two points."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def get_heuristic(name):
    """Returns the heuristic function by name string."""
    if name == "Manhattan":
        return manhattan
    elif name == "Euclidean":
        return euclidean
    else:
        raise ValueError(f"Unknown heuristic: {name}")