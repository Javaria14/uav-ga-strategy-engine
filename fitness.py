"""Multi-objective fitness (weighted sum of normalised objectives) with penalty-based constraints."""
import numpy as np

DEFAULT_WEIGHTS = dict(coverage=0.35, detection=0.25, energy=0.15, time=0.10, hazard=0.15)


class FitnessEvaluator:
    def __init__(self, env, weights=None, max_range=100.0, penalty=2.0, step=1.5):
        self.env = env
        self.w = dict(DEFAULT_WEIGHTS if weights is None else weights)
        self.max_range = max_range      # hard constraint: max path length per UAV
        self.penalty = penalty          # penalty strength for constraint violations
        self.step = step                # sampling distance along each leg
        self.total_priority = env.priority.sum()
        # normalisation references (so every objective lies roughly in [0, 1])
        self.E_ref = 3 * max_range * 1.0 * 1.3
        self.T_ref = max_range / 0.5 * 0.5
        self.H_ref = 3 * max_range * 0.25

    def evaluate(self, chrom, return_details=False):
        env, r, bits = self.env, chrom.real, chrom.bits
        n_uav, n_wp = bits.shape
        on_pts, on_rad = [], []
        energy = hazard = nofly_len = 0.0
        times, range_excess = [], 0.0
        for u in range(n_uav):
            pos = env.base
            dist_u = time_u = 0.0
            for k in range(n_wp):
                nxt = r[u, k, 0:2]
                s, p = r[u, k, 2], r[u, k, 3]
                d = float(np.hypot(*(nxt - pos)))
                n = max(2, int(np.ceil(d / self.step)) + 1)
                t = np.linspace(0, 1, n)[:, None]
                pts = pos + t * (nxt - pos)
                seg = d / (n - 1)
                t_leg = d / s
                dist_u += d
                time_u += t_leg
                energy += d * (0.5 + 0.5 * s ** 2) + bits[u, k] * p * t_leg * 0.5
                ix = np.clip(pts[:, 0].astype(int), 0, env.size - 1)
                iy = np.clip(pts[:, 1].astype(int), 0, env.size - 1)
                hazard += env.hazard[iy, ix].sum() * seg
                nofly_len += env.no_fly[iy, ix].sum() * seg
                if bits[u, k]:
                    on_pts.append(pts)
                    on_rad.append(np.full(n, (2 + 4 * p) * (1.2 - 0.2 * s)))  # sensing radius
                pos = nxt
            times.append(time_u)
            range_excess += max(0.0, dist_u - self.max_range)

        covered = np.zeros(env.size * env.size, dtype=bool)
        detected = 0.0
        if on_pts:
            P, R = np.vstack(on_pts), np.concatenate(on_rad)
            d2 = ((env.cells[None, :, :] - P[:, None, :]) ** 2).sum(-1)
            covered = (d2 <= (R ** 2)[:, None]).any(0)
            dt = ((env.targets[None, :, :] - P[:, None, :]) ** 2).sum(-1)
            detected = ((dt <= (R ** 2)[:, None]).any(0)).mean()
        coverage = env.priority.ravel()[covered].sum() / self.total_priority

        E, T, H = energy / self.E_ref, max(times) / self.T_ref, hazard / self.H_ref
        pen = self.penalty * (range_excess / self.max_range + nofly_len / self.max_range)
        w = self.w
        fit = (w['coverage'] * coverage + w['detection'] * detected
               - w['energy'] * E - w['time'] * T - w['hazard'] * H - pen)
        if not return_details:
            return fit
        return fit, dict(coverage=coverage, detection=detected, energy=E, time=T, hazard=H,
                         penalty=pen, covered=covered.reshape(env.size, env.size))
