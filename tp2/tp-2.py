import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from funciones import Item, KnapsackProblem, build_items_from_table, build_weight_items
import time


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

    t0 = time.perf_counter()
    all_solutions = problem.all_solutions()
    best_solution = problem.best_exhaustive_solution()
    print("Ejercicio 1 - Exhaustivo")
    print("Total de soluciones generadas:", len(all_solutions))
    print("Mejor solución:", best_solution)
    print("Elementos seleccionados:", best_solution.item_labels())
    print("Resumen: valor máximo =", best_solution.total_value, ", volumen usado =", best_solution.total_volume)

    t1 = time.perf_counter()
    print(f"Tiempo de ejecución Ejercicio 1: {t1 - t0:.6f} s")


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

    t0 = time.perf_counter()
    greedy_solution = problem.greedy_solution()
    t1 = time.perf_counter()

    t2 = time.perf_counter()
    optimal_solution = problem.best_exhaustive_solution()
    t3 = time.perf_counter()

    print("Ejercicio 2 - Greedy")
    print("Solución greedy:", greedy_solution)
    print("Solución óptima:", optimal_solution)
    print("Coincide el valor óptimo?:", greedy_solution.total_value == optimal_solution.total_value)
    print(f"Tiempo greedy: {t1 - t0:.6f} s; Tiempo exhaustivo: {t3 - t2:.6f} s")


def ejercicio_3():
    """Ejercicio 3: mochila con pesos en lugar de volumen."""
    weights = [1800, 600, 1200]
    values = [72, 36, 60]
    items = build_weight_items(weights, values)
    problem = KnapsackProblem(items, capacity=3000, capacity_dimension="weight")

    t0 = time.perf_counter()
    exhaustive_solution = problem.best_exhaustive_solution()
    t1 = time.perf_counter()

    t2 = time.perf_counter()
    greedy_solution = problem.greedy_solution()
    t3 = time.perf_counter()

    print("Ejercicio 3 - Peso")
    print("Solución exhaustiva:", exhaustive_solution)
    print("Solución greedy:", greedy_solution)
    print("¿Greedy alcanza el valor óptimo?:", greedy_solution.total_value == exhaustive_solution.total_value)
    print("Análisis:")
    if greedy_solution.total_value == exhaustive_solution.total_value:
        print("  El algoritmo greedy encontró una solución óptima para este conjunto de datos.")
    else:
        print("  El algoritmo greedy no encontró la solución óptima en este caso.")
    print(f"Tiempo exhaustivo: {t1 - t0:.6f} s; Tiempo greedy: {t3 - t2:.6f} s")


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
