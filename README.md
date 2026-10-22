<div align="center">

<img src="assets/banner.svg" alt="Genetic Algorithms Banner" width="100%">

<br><br>

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![GUI and Visualization](https://img.shields.io/badge/GUI-Tkinter%20%7C%20MapView-0284c7?style=for-the-badge)](https://github.com/TomSchimansky/TkinterMapView)
[![License: MIT](https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge)](LICENSE)

<p align="center">
  <b>Implementation, empirical benchmarking, and interactive visualizers for population-based metaheuristics and combinatorial optimization problems.</b>
</p>

[Academic Context](#academic-context) •
[Practical Assignments](#practical-assignments) •
[GUIs and Visualization](#guis-and-visualization) •
[Installation and Setup](#installation-and-setup) •
[Project Structure](#project-structure) •
[Team Members](#team-members)

<br>

---

</div>

## Academic Context

This repository contains practical assignments, experimental benchmarks, and interactive tools developed for the **Genetic Algorithms** (*Algoritmos Genéticos*) course at the **National Technological University - Rosario Regional Faculty** (Universidad Tecnológica Nacional - Facultad Regional Rosario, **UTN FRRo**), within the **Information Systems Engineering** degree program.

The primary objective of the course is the rigorous study and application of bio-inspired metaheuristics, evolutionary computation, and classical optimization heuristics. Special emphasis is placed on solving complex continuous and discrete $NP$-hard optimization problems where brute-force search is computationally intractable due to exponential state-space explosion.

---

## Practical Assignments

The table below outlines each assignment, its optimization domain, implemented algorithms, and dedicated documentation:

| Assignment | Problem Domain | Implemented Methods | Key Features | Documentation |
|:---:|:---|:---|:---|:---:|
| **TP 1** | **Function Optimization** ($f(x) = (x / \text{coef})^2$) | Roulette Wheel, Tournament Selection, Elitism | Binary encoding (30-bit), 1-point crossover, bit-inversion mutation, statistical convergence metrics | [English](tp1/README.md) · [Español](tp1/README.es.md) |
| **TP 2** | **0/1 Knapsack Problem** | Exhaustive Search ($O(2^n)$), Greedy Algorithm ($O(n \log n)$) | Volume and weight constraints, execution time benchmarks, interactive Tkinter desktop GUI | [English](tp2/README.md) · [Español](tp2/README.es.md) |
| **TP 3** | **Traveling Salesperson Problem (TSP)** (23 Argentine Capitals) | Exhaustive Search, Nearest Neighbor Heuristic, Genetic Algorithm (CX), Branch & Bound | Permutation encoding, Cycle Crossover, real geographic coordinates on interactive Argentina map | [English](tp3/README.md) · [Español](tp3/README.es.md) |

---

### TP 1: Canonical Genetic Algorithm

Maximization of the continuous objective function:

$$f(x) = \left(\frac{x}{\text{coef}}\right)^2 \quad \text{within the domain } [0, 2^{30} - 1], \quad \text{where } \text{coef} = 2^{30} - 1$$

* **Chromosome Representation:** 30-bit binary strings.
* **Genetic Operators:**
  * **Selection:** Fitness-proportionate Roulette Wheel, Deterministic/Tournament selection, and **Elitism** (preserving the top performing individuals across generations).
  * **Crossover:** Single-point crossover with probability $P_c = 0.75$.
  * **Mutation:** Bit-flip inversion with probability $P_m = 0.05$.
* **Analysis:** Statistical tracking across 20, 100, and 200 iterations: maximum, minimum, average fitness, standard deviation per generation, and phenotypic population diversity (Hamming distance).

```bash
# Run TP1 experiments
python tp1/scripts/experimento.py
```

---

### TP 2: Knapsack Problem (0/1 Knapsack)

Selection of optimal item subsets under capacity limits (volume in $\text{cm}^3$ and weight in grams) to maximize total value without exceeding container thresholds.

* **Exhaustive Search:** Exact evaluation of all $2^n$ combinations to establish guaranteed ground-truth optima.
* **Greedy Algorithm:** Value-to-cost heuristic ranking ($O(n \log n)$) for near-instant solutions.
* **Empirical Trade-off Analysis:** Performance comparison between solution optimality and runtime scalability as $n$ scales.
* **Interactive GUI:** Dedicated desktop interface allowing custom element entries, capacity adjustments, and live algorithm comparisons.

```bash
# Launch the TP2 GUI application
python tp2/scripts/gui.py
```

---

### TP 3: Traveling Salesperson Problem (TSP Argentina)

Finding the minimum distance tour that visits all **23 provincial capitals of Argentina** exactly once and returns to the starting capital.

* **Search Space Complexity:** For $N = 23$ cities, the symmetric search space size is:

$$\frac{(N - 1)!}{2} = \frac{22!}{2} \approx 5.62 \times 10^{20} \text{ possible tours}$$

* **Methods Implemented:**
  1. **Exhaustive Method:** Theoretical factorial complexity analysis confirming computational intractability.
  2. **Nearest Neighbor Heuristic:** Constructive greedy traversal from a selected capital or across all possible starting points.
  3. **Permutation-based Genetic Algorithm:** Integer-encoded chromosomes representing capital indices, **Cycle Crossover (CX)** to guarantee valid permutation offspring without duplicate cities, and swap mutation.
  4. **Branch and Bound:** Tree search with lower-bound distance pruning.
* **Cartographic Visualization:** Live route plotting using real latitude and longitude coordinates over an interactive map of Argentina.

```bash
# Launch the TP3 Argentina Map interactive GUI
python tp3/scripts/gui.py

# Alternatively, run console scripts:
python tp3/scripts/ejercicio_2a.py          # Nearest neighbor from single capital
python tp3/scripts/ejercicio_2b.py          # Best global nearest neighbor tour
python tp3/scripts/ejercicio_2c.py          # Genetic algorithm solution
python tp3/scripts/comparar_branch_bound.py # Branch & Bound benchmark comparison
```

---

## GUIs and Visualization

The project includes graphical interfaces and visual analytics modules:

* **Argentina Map Route Visualizer (`tp3`):** Built with `tkintermapview`, rendering actual geospatial routes computed by both the Genetic Algorithm and the Nearest Neighbor heuristic, displaying total kilometer length, visited nodes, and interactive map panning/zooming.
* **Knapsack Interactive Workbench (`tp2`):** Allows users to configure knapsack volumes and weights, edit item tables, and inspect capacity utilization charts.
* **Statistical Plotting Engine (`outputs/`):** Generates automated matplotlib plots for fitness curves (maximum, average, minimum), Hamming diversity, and computational time scaling.

---

## Installation and Setup

Follow these steps to set up the development environment locally:

### 1. Clone the repository
```bash
git clone https://github.com/NiconiKimg/Genetic-Algorithms.git
cd Genetic-Algorithms
```

### 2. Create and activate a virtual environment

* **Windows (PowerShell):**
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

* **Linux / macOS:**
```bash
python3 -m venv env
source env/bin/activate
```

> [!TIP]
> **PowerShell Execution Policy Notice:**
> If script activation is blocked on Windows PowerShell, run the following command in your terminal session:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

### 3. Install required dependencies
```bash
pip install -r requeriments.txt
```

---

## Project Structure

```plaintext
Genetic-Algorithms/
├── assets/
│   └── banner.svg                # Full-width vector animated header banner
├── tp1/                          # TP1: Canonical Genetic Algorithm
│   ├── outputs/                  # Convergence curves, diversity plots, stats tables
│   ├── scripts/                  # Executable experiment scripts (roulette, tournament, elitism)
│   ├── src/                      # Core modules: individual, population, operators, logger
│   └── README.md                 # Detailed TP1 specifications
├── tp2/                          # TP2: 0/1 Knapsack Problem
│   ├── outputs/                  # Benchmarks and runtime execution charts
│   ├── scripts/                  # gui.py, benchmarks.py, run_plots.py
│   ├── src/                      # Exhaustive and greedy algorithms, Tkinter GUI
│   └── README.md                 # Detailed TP2 specifications
├── tp3/                          # TP3: Traveling Salesperson Problem (TSP Argentina)
│   ├── scripts/                  # gui.py, exercises 1, 2a, 2b, 2c, branch and bound
│   ├── src/                      # Genetic algorithm, heuristics, Argentina map visualizer
│   └── README.md                 # Detailed TP3 specifications
├── LICENSE                       # MIT open source license
├── requeriments.txt              # Project dependencies (NumPy, Matplotlib, TkinterMapView)
└── README.md                     # Main repository documentation
```

---

## Team Members

Developed by students of **Information Systems Engineering** at **UTN Facultad Regional Rosario**:

<div align="center">

| Avatar | Full Name | GitHub Profile |
| :---: | :--- | :---: |
| <img src="https://github.com/carlex74.png" width="55" height="55" alt="Carlos Gugliermino" style="border-radius: 50%;"> | **Carlos Ricardo Gugliermino Zuñiga** | [![GitHub carlex74](https://img.shields.io/badge/carlex74-181717?style=flat-square&logo=github)](https://github.com/carlex74) |
| <img src="https://github.com/NiconiKImg.png" width="55" height="55" alt="Nicolás Pedemonte" style="border-radius: 50%;"> | **Nicolás Pedemonte** | [![GitHub NiconiKImg](https://img.shields.io/badge/NiconiKImg-181717?style=flat-square&logo=github)](https://github.com/NiconiKImg) |
| <img src="https://github.com/LucaTvl.png" width="55" height="55" alt="Luca Trincavelli" style="border-radius: 50%;"> | **Luca Trincavelli** | [![GitHub LucaTvl](https://img.shields.io/badge/LucaTvl-181717?style=flat-square&logo=github)](https://github.com/LucaTvl) |
| <img src="https://github.com/Frasquito3.png" width="55" height="55" alt="Franco Zariaga" style="border-radius: 50%;"> | **Franco Zariaga** | [![GitHub Frasquito3](https://img.shields.io/badge/Frasquito3-181717?style=flat-square&logo=github)](https://github.com/Frasquito3) |

</div>

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).
