<div align="center">
# 🚁 UAV Strategy Engine
 
**A Genetic Algorithm that evolves flight paths, speeds and sensor schedules for a 3-drone fleet.**
 
![Python](https://img.shields.io/badge/python-3.9+-blue?logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-✓-lightgrey?logo=numpy)
![Matplotlib](https://img.shields.io/badge/matplotlib-✓-orange)
![Course](https://img.shields.io/badge/AI-Assignment%202-success)
 
<img src="results/dark/evolution_paths_dark.png" width="95%" alt="Evolved UAV paths over generations">
*Routes evolve from random zig-zags (left) to coordinated coverage of priority zones (right).*
 
</div>
---
 
## ⚡ Quick start
 
```bash
pip install -r requirements.txt
python main.py
```
 
Takes about 3 minutes. Plots are saved to `results/`.
 
## 📊 Results
 
| | GA | Random search |
|---|:---:|:---:|
| Fitness | **0.284** | −2.962 |
| Priority coverage | **77%** | 34% |
| Targets detected | **100%** | 33% |
| Constraint penalty | **0** | 2.69 |
 
*Equal budget: 5,860 fitness evaluations each.*
 
<details>
<summary><b>📈 Convergence plot</b></summary>
<img src="results/dark/convergence_dark.png" width="90%" alt="Fitness convergence">
</details>
<details>
<summary><b>🆚 GA vs random search</b></summary>
<img src="results/ga_vs_random.png" width="60%" alt="GA vs random search">
</details>
<details>
<summary><b>🎛️ Hyperparameter sensitivity</b></summary>
<img src="results/sensitivity.png" width="90%" alt="Sensitivity analysis">
Moderate selection pressure (tournament 3–4), a mutation rate that is not too high, and a larger population worked best.
 
</details>
## 🧬 How it works
 
<details>
<summary><b>Chromosome</b></summary>
3 UAVs × 8 waypoints × 5 genes = 120 genes. Per waypoint: `x`, `y`, `speed`, `sensor power` (real) and `sensor on/off` (binary).
 
</details>
<details>
<summary><b>Fitness function</b></summary>
```
F = 0.35·Coverage + 0.25·Detection − 0.15·Energy − 0.10·Time − 0.15·Hazard − Penalty
```
 
Constraints: no-fly zones and a 100-cell range limit per UAV (repair + penalty).
 
</details>
<details>
<summary><b>Operators</b></summary>
Tournament selection, per-route segment-swap or geometric-blend crossover, Gaussian / random-reset / bit-flip / waypoint-swap mutation, elitism, and random immigrants when the search stagnates.
 
</details>
## 🗂️ Project layout
 
```
main.py              run the main simulation
run_experiments.py   sensitivity study (slow)
make_dark_plots.py   black-background plots
uav_ga/
  environment.py     grid, zones, hazards, targets
  chromosome.py      encoding + repair
  fitness.py         multi-objective fitness
  operators.py       selection, crossover, mutation
  ga.py              GA engine
  baseline.py        random-search baseline
  visualize.py       plots
results/             generated figures
```
 
<details>
<summary><b>🔧 Troubleshooting</b></summary>
- `No module named matplotlib` → run `pip install -r requirements.txt` from inside the project folder.
- `No space left on device` → free disk space on your system drive, then rerun.
- Run `python run_experiments.py pop|mut|sel|rs|plot` to run the sensitivity study in parts.
</details>
---
 
<div align="center">
AI (BSCS 5) · Bahria University Lahore Campus
 
</div>
 
