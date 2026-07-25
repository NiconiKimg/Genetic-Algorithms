import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from funciones import Item, KnapsackProblem, build_items_from_table, build_weight_items
from logger import Logger


def ejercicio_1():
    """Ejercicio 1: mochila con búsqueda exhaustiva."""
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

    # log via Logger
    logger = Logger()
    logger.start_run(algorithm="exhaustive", n=len(items), capacity=4200, capacity_dimension="volume")
    all_solutions = problem.all_solutions()
    best_solution = problem.best_exhaustive_solution()

    print("Ejercicio 1 - Exhaustivo")
    print("Total de soluciones generadas:", len(all_solutions))
    print("Mejor solución:", best_solution)
    print("Elementos seleccionados:", best_solution.item_labels())
    print("Resumen: valor máximo =", best_solution.total_value, ", volumen usado =", best_solution.total_volume)
    logger.end_run(
        total_value=best_solution.total_value,
        total_volume=best_solution.total_volume,
        total_weight=best_solution.total_weight,
        items_labels=best_solution.item_labels(),
        num_subsets=len(all_solutions),
    )
    print("Resultados guardados en:", logger.csv_location())


def ejercicio_2():
    """Ejercicio 2: mochila con algoritmo greedy."""
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

    logger = Logger()
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
    # exhaustive (for comparison)
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
    print("Solución greedy:", greedy_solution)
    print("Solución óptima:", optimal_solution)
    print("Coincide el valor óptimo?:", greedy_solution.total_value == optimal_solution.total_value)
    print("Resultados guardados en:", logger.csv_location())


def ejercicio_3():
    """Ejercicio 3: mochila con pesos en lugar de volumen."""
    weights = [1800, 600, 1200]
    values = [72, 36, 60]
    items = build_weight_items(weights, values)
    problem = KnapsackProblem(items, capacity=3000, capacity_dimension="weight")

    logger = Logger()
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
    print("Solución exhaustiva:", exhaustive_solution)
    print("Solución greedy:", greedy_solution)
    print("¿Greedy alcanza el valor óptimo?:", greedy_solution.total_value == exhaustive_solution.total_value)
    print("Análisis:")
    if greedy_solution.total_value == exhaustive_solution.total_value:
        print("  El algoritmo greedy encontró una solución óptima para este conjunto de datos.")
    else:
        print("  El algoritmo greedy no encontró la solución óptima en este caso.")
    print("Resultados guardados en:", logger.csv_location())


if __name__ == "__main__":
    print("Seleccione un ejercicio:")
    print("1 - Ejercicio 1")
    print("2 - Ejercicio 2")
    print("3 - Ejercicio 3")

    opcion = input("Ingrese el número del ejercicio: ")
    if opcion == "1":
        ejercicio_1()
    elif opcion == "2":
        ejercicio_2()
    elif opcion == "3":
        ejercicio_3()
    else:
        print("Opción inválida")
