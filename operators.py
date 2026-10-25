"""Selection, crossover, mutation and diversity operators tailored to spatial genes."""
import numpy as np
from .chromosome import Chromosome


def tournament_selection(pop, tournament_size, rng):
    """Pick the fittest of `tournament_size` random individuals (larger size = higher selection pressure)."""
    idx = rng.integers(0, len(pop), tournament_size)
    return pop[max(idx, key=lambda i: pop[i].fitness)]


def crossover(p1, p2, rng):
    """Per-UAV crossover. Each route uses either
       (a) segment-swap: swap the waypoint tail after a random cut point, or
       (b) geometric (blend) crossover: child = a*p1 + (1-a)*p2 on x, y, speed, power."""
    c1, c2 = p1.copy(), p2.copy()
    n_uav, n_wp = p1.bits.shape
    for u in range(n_uav):
        if rng.random() < 0.5:                       # segment swap
            cut = rng.integers(1, n_wp)
            c1.real[u, cut:], c2.real[u, cut:] = p2.real[u, cut:].copy(), p1.real[u, cut:].copy()
            c1.bits[u, cut:], c2.bits[u, cut:] = p2.bits[u, cut:].copy(), p1.bits[u, cut:].copy()
        else:                                        # geometric blend
            a = rng.uniform(0.2, 0.8)
            r1 = a * p1.real[u] + (1 - a) * p2.real[u]
            r2 = (1 - a) * p1.real[u] + a * p2.real[u]
            c1.real[u], c2.real[u] = r1, r2
            mask = rng.random(n_wp) < 0.5            # uniform crossover on the binary part
            c1.bits[u] = np.where(mask, p1.bits[u], p2.bits[u])
            c2.bits[u] = np.where(mask, p2.bits[u], p1.bits[u])
    c1.fitness = c2.fitness = None
    return c1, c2


def mutate(c, env, rate, sigma, rng):
    """Spatial mutation:
       - Gaussian shift of coordinates (step `sigma` cells), speed and power genes
       - random-reset of a waypoint (large jump, escapes local optima)
       - bit-flip of the sensor schedule
       - swap of two waypoints in a route (changes visiting order)"""
    n_uav, n_wp = c.bits.shape
    m = rng.random((n_uav, n_wp)) < rate
    c.real[..., 0:2] += m[..., None] * rng.normal(0, sigma, (n_uav, n_wp, 2))
    c.real[..., 2] += m * rng.normal(0, 0.2, (n_uav, n_wp))
    c.real[..., 3] += m * rng.normal(0, 0.15, (n_uav, n_wp))
    reset = rng.random((n_uav, n_wp)) < rate / 5
    c.real[reset, 0:2] = rng.uniform(0, env.size - 1, (reset.sum(), 2))
    flip = rng.random((n_uav, n_wp)) < rate / 2
    c.bits = np.where(flip, 1 - c.bits, c.bits)
    for u in range(n_uav):
        if rng.random() < rate:
            i, j = rng.choice(n_wp, 2, replace=False)
            c.real[u, [i, j]] = c.real[u, [j, i]]
    c.repair(env)
    return c


def diversity(pop):
    """Population diversity = mean std-dev of waypoint coordinates across individuals."""
    X = np.array([c.real[..., 0:2] for c in pop])
    return float(X.std(axis=0).mean())
