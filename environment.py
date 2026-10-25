"""Hazard grid: discretised 2D map holding priority zones, hazards, no-fly zones and targets."""
import numpy as np


class Environment:
    """A size x size grid. Arrays are indexed [y, x]; world coordinates are (x, y) in cell units."""

    def __init__(self, size=50, seed=7):
        self.size = size
        rng = np.random.default_rng(seed)
        ys, xs = np.mgrid[0:size, 0:size]
        self.cells = np.column_stack([xs.ravel(), ys.ravel()]).astype(float)  # (size*size, 2)

        # Priority map: low background value + three high-priority disaster zones (weights 3, 2.5, 2)
        self.priority = np.full((size, size), 0.2)
        for (x0, y0, x1, y1, w) in [(30, 32, 44, 46, 3.0), (6, 28, 18, 42, 2.5), (28, 6, 42, 18, 2.0)]:
            self.priority[y0:y1, x0:x1] = w

        # Hazard map: Gaussian "pockets" (e.g. high wind / radiation), values in [0, 1]
        self.hazard = np.zeros((size, size))
        for (cx, cy, r) in [(36, 38, 5), (22, 22, 6), (12, 36, 4), (36, 12, 4)]:
            self.hazard = np.maximum(self.hazard, np.exp(-(((xs - cx) ** 2 + (ys - cy) ** 2) / (2 * (r / 2) ** 2))))

        # No-fly zones: rectangles (x0, y0, x1, y1)
        self.no_fly_rects = [(18, 8, 26, 16), (20, 34, 28, 42)]
        self.no_fly = np.zeros((size, size), dtype=bool)
        for (x0, y0, x1, y1) in self.no_fly_rects:
            self.no_fly[y0:y1, x0:x1] = True

        # Targets (e.g. survivors / hotspots) sampled inside priority zones, with a few outside
        pts = []
        for (x0, y0, x1, y1, _) in [(30, 32, 44, 46, 3), (6, 28, 18, 42, 3), (28, 6, 42, 18, 3)]:
            for _ in range(4):
                pts.append((rng.uniform(x0, x1), rng.uniform(y0, y1)))
        self.targets = np.array(pts)
        self.base = np.array([2.0, 2.0])  # all UAVs launch from here

    def in_no_fly(self, xy):
        """Boolean array: are the (N,2) points inside a no-fly zone?"""
        xy = np.atleast_2d(xy)
        ix = np.clip(xy[:, 0].astype(int), 0, self.size - 1)
        iy = np.clip(xy[:, 1].astype(int), 0, self.size - 1)
        return self.no_fly[iy, ix]
