import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from funciones import KnapsackProblem, build_items_from_table

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
    problem = KnapsackProblem(items, capacity=4200, capacity_dimension="volume")

    greedy_solution = problem.greedy_solution()
    exhaustive_solution = problem.best_exhaustive_solution()

    print("Ejercicio 2 - Greedy")
    print("Solución greedy:", greedy_solution.item_labels())
    print("Valor greedy:", greedy_solution.total_value)
    print("Volumen greedy:", greedy_solution.total_volume)
    print("Solución óptima:", exhaustive_solution.item_labels())
    print("Valor óptimo:", exhaustive_solution.total_value)
    print("Coinciden los valores?:", greedy_solution.total_value == exhaustive_solution.total_value)
