"""Object-oriented Genetic Algorithm engine."""
import numpy as np
from .chromosome import Chromosome
from .operators import tournament_selection, crossover, mutate, diversity


class GeneticAlgorithm:
    def __init__(self, env, evaluator, n_uav=3, n_wp=8, pop_size=60, generations=100,
                 crossover_rate=0.85, mutation_rate=0.1, tournament_size=3, elite=2,
                 sigma0=6.0, patience=40, immigrant_frac=0.1, seed=0):
        self.env, self.ev = env, evaluator
        self.n_uav, self.n_wp = n_uav, n_wp
        self.pop_size, self.generations = pop_size, generations
        self.pc, self.pm, self.k, self.elite = crossover_rate, mutation_rate, tournament_size, elite
        self.sigma0, self.patience, self.immigrant_frac = sigma0, patience, immigrant_frac
        self.rng = np.random.default_rng(seed)
        self.history = dict(best=[], avg=[], diversity=[])
        self.snapshots = {}         # generation -> copy of best chromosome
        self.n_evals = 0

    def _evaluate(self, pop):
        for c in pop:
            if c.fitness is None:
                c.fitness = self.ev.evaluate(c)
                self.n_evals += 1

    def initialise(self):
        """Population initialisation: random legal chromosomes (repair applied)."""
        return [Chromosome.random(self.env, self.n_uav, self.n_wp, self.rng) for _ in range(self.pop_size)]

    def run(self, snapshot_gens=()):
        pop = self.initialise()
        self._evaluate(pop)
        best_ever, stagnant = max(pop, key=lambda c: c.fitness).copy(), 0
        for gen in range(self.generations + 1):
            fits = np.array([c.fitness for c in pop])
            best = pop[int(fits.argmax())]
            self.history['best'].append(float(fits.max()))
            self.history['avg'].append(float(fits.mean()))
            self.history['diversity'].append(diversity(pop))
            if gen in snapshot_gens:
                self.snapshots[gen] = best.copy()
            if best.fitness > best_ever.fitness + 1e-6:
                best_ever, stagnant = best.copy(), 0
            else:
                stagnant += 1
            if gen == self.generations or stagnant >= self.patience:   # termination criteria
                self.snapshots[gen] = best_ever.copy()
                break
            # --- next generation ---
            order = np.argsort(-fits)
            new = [pop[i].copy() for i in order[:self.elite]]          # elitism
            sigma = self.sigma0 * (1 - 0.8 * gen / self.generations) + 0.5  # decaying step size
            while len(new) < self.pop_size:
                p1 = tournament_selection(pop, self.k, self.rng)
                p2 = tournament_selection(pop, self.k, self.rng)
                if self.rng.random() < self.pc:
                    c1, c2 = crossover(p1, p2, self.rng)
                else:
                    c1, c2 = p1.copy(), p2.copy()
                new += [mutate(c1, self.env, self.pm, sigma, self.rng),
                        mutate(c2, self.env, self.pm, sigma, self.rng)]
            new = new[:self.pop_size]
            if stagnant >= self.patience // 3:                          # diversity injection
                n_imm = max(1, int(self.immigrant_frac * self.pop_size))
                for i in range(n_imm):
                    new[-1 - i] = Chromosome.random(self.env, self.n_uav, self.n_wp, self.rng)
            self._evaluate(new)
            pop = new
        self.best = best_ever
        return best_ever
