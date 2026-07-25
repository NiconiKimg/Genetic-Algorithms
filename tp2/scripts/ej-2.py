import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from funciones import KnapsackProblem, build_items_from_table
from logger import Logger
import time


if __name__ == "__main__":
    tabla = [
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
    items = build_items_from_table(tabla)
    logger = Logger()
    items = build_items_from_table(tabla)
    problem = KnapsackProblem(items, capacity=4200, capacity_dimension="volume")

    # greedy
    logger.start_run(algorithm="greedy", n=len(items), capacity=4200, capacity_dimension="volume")
    greedy_solution = problem.greedy_solution()
    logger.end_run(
        total_value=greedy_solution.total_value,
        total_volume=greedy_solution.total_volume,
        total_weight=greedy_solution.total_weight,
        items_labels=greedy_solution.item_labels(),
        num_subsets=None,
    )

    # exhaustive for comparison
    logger.start_run(algorithm="exhaustive", n=len(items), capacity=4200, capacity_dimension="volume")
    optimal_solution = problem.best_exhaustive_solution()
    logger.end_run(
        total_value=optimal_solution.total_value,
        total_volume=optimal_solution.total_volume,
        total_weight=optimal_solution.total_weight,
        items_labels=optimal_solution.item_labels(),
        num_subsets=len(problem.all_solutions()),
    )

    print("Ejercicio 2 - Greedy")
    print("Solución greedy:", greedy_solution.item_labels())
    print("Valor greedy:", greedy_solution.total_value)
    print("Volumen greedy:", greedy_solution.total_volume)
    print("Solución óptima:", optimal_solution.item_labels())
    print("Valor óptimo:", optimal_solution.total_value)
    print("Coinciden los valores?:", greedy_solution.total_value == optimal_solution.total_value)
    print("Resultados guardados en:", logger.csv_location())
