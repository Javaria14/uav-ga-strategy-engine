"""Baseline: pure random search with the same number of fitness evaluations as the GA."""
import numpy as np
from .chromosome import Chromosome


def random_search(env, evaluator, n_evals, n_uav=3, n_wp=8, seed=0):
    rng = np.random.default_rng(seed)
    best, hist = None, []
    for _ in range(n_evals):
        c = Chromosome.random(env, n_uav, n_wp, rng)
        c.fitness = evaluator.evaluate(c)
        if best is None or c.fitness > best.fitness:
            best = c
        hist.append(best.fitness)
    return best, hist
