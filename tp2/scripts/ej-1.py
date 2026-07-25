import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import time

from funciones import KnapsackProblem, build_items_from_table
from logger import Logger

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
    logger = Logger()
    items = build_items_from_table(tabla)
    problem = KnapsackProblem(items, capacity=4200, capacity_dimension="volume")

    logger.start_run(algorithm="exhaustive", n=len(items), capacity=4200, capacity_dimension="volume")
    all_solutions = problem.all_solutions()
    best_solution = problem.best_exhaustive_solution()

    print("Ejercicio 1 - Exhaustivo")
    print("Número de subconjuntos evaluados:", len(all_solutions))
    print("Mejor subconjunto:", best_solution.item_labels())
    print("Valor total:", best_solution.total_value)
    print("Volumen ocupado:", best_solution.total_volume)

    logger.end_run(
        total_value=best_solution.total_value,
        total_volume=best_solution.total_volume,
        total_weight=best_solution.total_weight,
        items_labels=best_solution.item_labels(),
        num_subsets=len(all_solutions),
    )
    print("Resultados guardados en:", logger.csv_location())
