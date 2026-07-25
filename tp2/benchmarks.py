"""Benchmark runner for TP2.

Runs exercises and logs results to CSV via `Logger` in `src/logger.py`.

Usage examples:
  python tp2/benchmarks.py --mode e1e2 --k 10 --shuffle --start-seed 0
  python tp2/benchmarks.py --mode e3 --k 5
"""
import sys
from pathlib import Path
import argparse
import random

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from logger import Logger
from funciones import build_items_from_table, build_weight_items, KnapsackProblem


VOLUME_TABLE = [
    [150, 20],
    [325, 40],
    [600, 50],
    [805, 36],
    [430, 25],
    [1200, 64],
    [770, 54],
    [60, 18],
    [930, 46],
    [353, 28],
]


def run_e1e2(logger: Logger, n_values: list, k: int, shuffle: bool, start_seed: int):
    """Run exercises 1 (exhaustive) and 2 (greedy) for each n in n_values, k repetitions each."""
    table_base = VOLUME_TABLE
    max_items = len(table_base)
    for n in n_values:
        if n <= 0:
            continue
        if n > max_items:
            print(f"Requested n={n} larger than available items ({max_items}); capping to {max_items}.")
            n_use = max_items
        else:
            n_use = n

        for i in range(k):
            seed = start_seed + i
            tbl = [row[:] for row in table_base[:n_use]]
            if shuffle:
                rnd = random.Random(seed)
                rnd.shuffle(tbl)

            items = build_items_from_table(tbl)
            problem = KnapsackProblem(items, capacity=4200, capacity_dimension="volume")

            # Exhaustive
            variant = f"seed={seed},run={i},n={n_use}"
            logger.start_run(algorithm="exhaustive", n=len(items), capacity=4200, capacity_dimension="volume", variant=variant)
            best = problem.best_exhaustive_solution()
            logger.end_run(total_value=best.total_value, total_volume=best.total_volume, total_weight=best.total_weight, items_labels=best.item_labels(), num_subsets=(1 << len(items)))

            # Greedy
            logger.start_run(algorithm="greedy", n=len(items), capacity=4200, capacity_dimension="volume", variant=variant)
            greedy = problem.greedy_solution()
            logger.end_run(total_value=greedy.total_value, total_volume=greedy.total_volume, total_weight=greedy.total_weight, items_labels=greedy.item_labels(), num_subsets=None)


def run_e3(logger: Logger, n_values: list, k: int, shuffle: bool, start_seed: int):
    """Run exercise 3 (weights) k times: both exhaustive and greedy. n_values ignored beyond available items."""
    weights = [1800, 600, 1200]
    values = [72, 36, 60]
    max_items = len(weights)
    for n in n_values:
        n_use = min(n, max_items) if n > 0 else max_items
        for i in range(k):
            seed = start_seed + i
            # for weight problem we can optionally shuffle (keeps pairings)
            w = weights[:n_use]
            v = values[:n_use]
            if shuffle:
                rnd = random.Random(seed)
                perm = list(range(len(w)))
                rnd.shuffle(perm)
                w = [w[j] for j in perm]
                v = [v[j] for j in perm]

            items = build_weight_items(w, v)
            problem = KnapsackProblem(items, capacity=3000, capacity_dimension="weight")

            variant = f"seed={seed},run={i},n={n_use}"
            logger.start_run(algorithm="exhaustive", n=len(items), capacity=3000, capacity_dimension="weight", variant=variant)
            best = problem.best_exhaustive_solution()
            logger.end_run(total_value=best.total_value, total_volume=best.total_volume, total_weight=best.total_weight, items_labels=best.item_labels(), num_subsets=(1 << len(items)))

            logger.start_run(algorithm="greedy", n=len(items), capacity=3000, capacity_dimension="weight", variant=variant)
            greedy = problem.greedy_solution()
            logger.end_run(total_value=greedy.total_value, total_volume=greedy.total_volume, total_weight=greedy.total_weight, items_labels=greedy.item_labels(), num_subsets=None)


def main():
    # Interactive inputs with defaults
    print("Benchmark runner (interactive). Press Enter to accept defaults in brackets.")
    mode = input("Mode (e1e2 - exercises 1 and 2, e3 - exercise 3) [e1e2]: ").strip() or "e1e2"
    while mode not in ("e1e2", "e3"):
        mode = input("Invalid mode. Enter 'e1e2' or 'e3': ").strip()

    nvals_raw = input("n values (comma list or range start-end[:step]) [10]: ").strip()

    def parse_n_values(s: str):
        if not s:
            return [10]
        s = s.strip()
        parts = [p.strip() for p in s.split(',') if p.strip()]
        vals = []
        for p in parts:
            if '-' in p:
                # range or range:step
                if ':' in p:
                    range_part, step_part = p.split(':', 1)
                    try:
                        step = int(step_part)
                    except Exception:
                        step = 1
                else:
                    range_part = p
                    step = 1
                try:
                    start_s, end_s = range_part.split('-', 1)
                    start = int(start_s)
                    end = int(end_s)
                    vals.extend(list(range(start, end + 1, step)))
                except Exception:
                    continue
            else:
                try:
                    vals.append(int(p))
                except Exception:
                    continue
        # unique and sorted
        return sorted(list(dict.fromkeys(vals))) if vals else [10]

    try:
        n_values = parse_n_values(nvals_raw)
    except Exception:
        n_values = [10]

    k_raw = input("Repetitions per configuration k [5]: ").strip()
    try:
        k = int(k_raw) if k_raw else 5
    except ValueError:
        k = 5

    shuffle_raw = input("Shuffle items each run? (y/N) [N]: ").strip().lower()
    shuffle = True if shuffle_raw in ("y", "yes") else False

    seed_raw = input("Start seed [0]: ").strip()
    try:
        start_seed = int(seed_raw) if seed_raw else 0
    except ValueError:
        start_seed = 0

    csv_path = input("CSV output path (leave blank for default 'tp2/outputs/results.csv'): ").strip() or None

    logger = Logger(csv_path=csv_path) if csv_path else Logger()
    logger.clear()

    if mode == "e1e2":
        run_e1e2(logger, n_values=n_values, k=k, shuffle=shuffle, start_seed=start_seed)
    else:
        run_e3(logger, n_values=n_values, k=k, shuffle=shuffle, start_seed=start_seed)

    print("Benchmark finished. CSV:", logger.csv_location())


if __name__ == "__main__":
    main()
