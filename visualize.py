"""Plot helpers: convergence curves, UAV paths with coverage heatmaps, comparison charts."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

COLORS = ['tab:red', 'tab:blue', 'tab:green', 'tab:purple', 'tab:orange']


def plot_convergence(history, path):
    g = np.arange(len(history['best']))
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(g, history['best'], label='Best fitness', lw=2)
    ax[0].plot(g, history['avg'], label='Average fitness', lw=2)
    ax[0].set(xlabel='Generation', ylabel='Fitness', title='Fitness convergence'); ax[0].legend(); ax[0].grid(alpha=.3)
    ax[1].plot(g, history['diversity'], color='tab:green', lw=2)
    ax[1].set(xlabel='Generation', ylabel='Mean coordinate std-dev (cells)', title='Population diversity'); ax[1].grid(alpha=.3)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def draw_solution(ax, env, evaluator, chrom, title):
    fit, d = evaluator.evaluate(chrom, return_details=True)
    s = env.size
    ax.imshow(env.priority, origin='lower', cmap='YlOrBr', alpha=0.45, extent=(0, s, 0, s))
    ax.imshow(np.ma.masked_where(env.hazard < 0.15, env.hazard), origin='lower', cmap='Reds',
              alpha=0.45, extent=(0, s, 0, s), vmin=0, vmax=1.2)
    cov = np.ma.masked_where(~d['covered'], d['covered'].astype(float))      # coverage heatmap overlay
    ax.imshow(cov, origin='lower', cmap='Blues', alpha=0.35, extent=(0, s, 0, s), vmin=0, vmax=1.5)
    for (x0, y0, x1, y1) in env.no_fly_rects:
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc='black', alpha=0.6, hatch='//'))
    ax.scatter(env.targets[:, 0], env.targets[:, 1], marker='*', c='gold', edgecolors='k', s=70, zorder=5)
    for u in range(chrom.bits.shape[0]):
        pts = np.vstack([env.base, chrom.real[u, :, 0:2]])
        ax.plot(pts[:, 0], pts[:, 1], '-o', color=COLORS[u % 5], lw=1.8, ms=3.5, label=f'UAV {u+1}')
    ax.scatter(*env.base, marker='s', c='k', s=60, zorder=6)
    ax.set(xlim=(0, s), ylim=(0, s), title=f"{title}\nfit={fit:.3f}  cov={d['coverage']:.2f}  det={d['detection']:.2f}")
    ax.set_aspect('equal'); ax.tick_params(labelsize=7)


def plot_evolution(env, evaluator, snapshots, path):
    gens = sorted(snapshots)
    pick = [gens[0], gens[len(gens) // 3], gens[2 * len(gens) // 3], gens[-1]] if len(gens) >= 4 else gens
    fig, axes = plt.subplots(1, len(pick), figsize=(4.4 * len(pick), 4.8))
    for ax, g in zip(np.atleast_1d(axes), pick):
        draw_solution(ax, env, evaluator, snapshots[g], f'Generation {g}')
    np.atleast_1d(axes)[0].legend(fontsize=7, loc='upper right')
    fig.tight_layout(); fig.savefig(path, dpi=140); plt.close(fig)


def plot_coverage_heatmap(env, evaluator, chrom, path):
    fig, ax = plt.subplots(figsize=(5.5, 5.2))
    draw_solution(ax, env, evaluator, chrom, 'Final evolved solution')
    ax.legend(fontsize=7, loc='upper right')
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def plot_sensitivity(results, path):
    """results: {'Population size': {label: [final fitness per seed]}, ...}"""
    fig, axes = plt.subplots(1, len(results), figsize=(4.2 * len(results), 3.8))
    for ax, (name, groups) in zip(np.atleast_1d(axes), results.items()):
        labels = list(groups)
        ax.boxplot([groups[l] for l in labels], labels=labels)
        ax.set(title=name, ylabel='Best fitness'); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def plot_ga_vs_random(ga_hist, rs_hist, ga_evals, path):
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(np.linspace(0, ga_evals, len(ga_hist['best'])), ga_hist['best'], lw=2, label='Genetic Algorithm (best)')
    ax.plot(np.arange(1, len(rs_hist) + 1), rs_hist, lw=2, label='Random search (best so far)')
    ax.set(xlabel='Fitness evaluations', ylabel='Best fitness', title='GA vs random search (equal budget)')
    ax.legend(); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)
