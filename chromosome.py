"""Hybrid real-integer chromosome.

For every UAV u and waypoint k we store 5 genes:
    x, y     real   waypoint position on the grid
    speed    real   speed multiplier for the leg that ends at this waypoint  [0.5, 2.0]
    power    real   sensor power level for that leg                           [0.0, 1.0]
    sensor   binary sensor ON/OFF schedule bit for that leg                   {0, 1}
Shape: real (n_uav, n_wp, 4) + bits (n_uav, n_wp)  ->  n_uav * n_wp * 5 genes in total.
"""
import numpy as np

SPEED_MIN, SPEED_MAX = 0.5, 2.0


class Chromosome:
    def __init__(self, real, bits):
        self.real = real      # [..., 0]=x, 1]=y, 2]=speed, 3]=power]
        self.bits = bits      # sensor schedule (0/1)
        self.fitness = None   # cached fitness value

    @classmethod
    def random(cls, env, n_uav, n_wp, rng):
        real = np.empty((n_uav, n_wp, 4))
        real[..., 0:2] = rng.uniform(0, env.size - 1, (n_uav, n_wp, 2))
        real[..., 2] = rng.uniform(SPEED_MIN, SPEED_MAX, (n_uav, n_wp))
        real[..., 3] = rng.uniform(0, 1, (n_uav, n_wp))
        bits = rng.integers(0, 2, (n_uav, n_wp))
        c = cls(real, bits)
        c.repair(env)
        return c

    def copy(self):
        c = Chromosome(self.real.copy(), self.bits.copy())
        c.fitness = self.fitness
        return c

    def repair(self, env):
        """Repair mechanism: clip genes to legal bounds and push waypoints out of no-fly zones."""
        r = self.real
        r[..., 0:2] = np.clip(r[..., 0:2], 0, env.size - 1)
        r[..., 2] = np.clip(r[..., 2], SPEED_MIN, SPEED_MAX)
        r[..., 3] = np.clip(r[..., 3], 0.0, 1.0)
        for (x0, y0, x1, y1) in env.no_fly_rects:
            for u in range(r.shape[0]):
                for k in range(r.shape[1]):
                    x, y = r[u, k, 0], r[u, k, 1]
                    if x0 <= x < x1 and y0 <= y < y1:
                        # move to the nearest rectangle edge
                        d = [x - x0, x1 - x, y - y0, y1 - y]
                        m = int(np.argmin(d))
                        if m == 0: r[u, k, 0] = x0 - 0.5
                        elif m == 1: r[u, k, 0] = x1 + 0.5
                        elif m == 2: r[u, k, 1] = y0 - 0.5
                        else: r[u, k, 1] = y1 + 0.5
        r[..., 0:2] = np.clip(r[..., 0:2], 0, env.size - 1)
        self.fitness = None
