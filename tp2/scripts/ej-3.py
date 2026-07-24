import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from funciones import KnapsackProblem, build_weight_items

if __name__ == "__main__":
    weights = [1800, 600, 1200]
    values = [72, 36, 60]
    items = build_weight_items(weights, values)
    problem = KnapsackProblem(items, capacity=3000, capacity_dimension="weight")

    exhaustive_solution = problem.best_exhaustive_solution()
    greedy_solution = problem.greedy_solution()

    print("Ejercicio 3 - Peso")
    print("Solución exhaustiva:", exhaustive_solution.item_labels())
    print("Valor exhaustivo:", exhaustive_solution.total_value)
    print("Peso exhaustivo:", exhaustive_solution.total_weight)
    print("")
    print("Solución greedy:", greedy_solution.item_labels())
    print("Valor greedy:", greedy_solution.total_value)
    print("Peso greedy:", greedy_solution.total_weight)
    print("¿Greedy alcanza el óptimo?:", greedy_solution.total_value == exhaustive_solution.total_value)
    if greedy_solution.total_value == exhaustive_solution.total_value:
        print("El greedy encontró la solución óptima para este conjunto de datos.")
    else:
        print("El greedy no encontró la solución óptima en este caso, por lo tanto es subóptimo.")
