import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import time

from funciones import KnapsackProblem, build_weight_items
from logger import Logger

if __name__ == "__main__":
    weights = [1800, 600, 1200]
    values = [72, 36, 60]
    logger = Logger()
    items = build_weight_items(weights, values)
    problem = KnapsackProblem(items, capacity=3000, capacity_dimension="weight")

    # exhaustive
    logger.start_run(algorithm="exhaustive", n=len(items), capacity=3000, capacity_dimension="weight")
    exhaustive_solution = problem.best_exhaustive_solution()
    logger.end_run(
        total_value=exhaustive_solution.total_value,
        total_volume=exhaustive_solution.total_volume,
        total_weight=exhaustive_solution.total_weight,
        items_labels=exhaustive_solution.item_labels(),
        num_subsets=len(problem.all_solutions()),
    )

    # greedy
    logger.start_run(algorithm="greedy", n=len(items), capacity=3000, capacity_dimension="weight")
    greedy_solution = problem.greedy_solution()
    logger.end_run(
        total_value=greedy_solution.total_value,
        total_volume=greedy_solution.total_volume,
        total_weight=greedy_solution.total_weight,
        items_labels=greedy_solution.item_labels(),
        num_subsets=None,
    )

    print("Ejercicio 3 - Peso")
    print("Solución exhaustiva:", exhaustive_solution.item_labels())
    print("Valor total exhaustivo:", exhaustive_solution.total_value)
    print("Peso usado exhaustivo:", exhaustive_solution.total_weight)
    print("")
    print("Solución greedy:", greedy_solution.item_labels())
    print("Valor total greedy:", greedy_solution.total_value)
    print("Peso usado greedy:", greedy_solution.total_weight)
    print("")
    print("¿Greedy alcanza el óptimo?:", greedy_solution.total_value == exhaustive_solution.total_value)
    if greedy_solution.total_value == exhaustive_solution.total_value:
        print("El greedy encontró la solución óptima para este conjunto de datos.")
    else:
        print("El greedy no encontró la solución óptima en este caso, por lo tanto es subóptimo.")
    print("Resultados guardados en:", logger.csv_location())
