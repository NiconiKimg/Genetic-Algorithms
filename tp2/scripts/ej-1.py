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

    all_solutions = problem.all_solutions()
    best_solution = problem.best_exhaustive_solution()

    print("Ejercicio 1 - Exhaustivo")
    print("Número de subconjuntos evaluados:", len(all_solutions))
    print("Mejor subconjunto:", best_solution.item_labels())
    print("Valor total:", best_solution.total_value)
    print("Volumen usado:", best_solution.total_volume)
