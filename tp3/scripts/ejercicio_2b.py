"""Ejercicio 2.b: recorrido mínimo por vecino más cercano evaluando todas las capitales de origen."""

from pathlib import Path
import sys
from time import perf_counter

RAIZ_TP3 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_TP3 / "src"))

from comun.datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
from comun.modelos_tsp import ProblemaTSP
from heuristica.heuristica_vecino import VecinoMasCercano


def resolver_2b() -> None:
    """Evalúa la heurística partiendo de cada una de las 24 capitales y halla el recorrido mínimo."""
    problema = ProblemaTSP(CAPITALES, DISTANCIAS_KM)
    heuristica = VecinoMasCercano(problema)

    inicio = perf_counter()
    mejor_capital = CAPITALES[0]
    mejor_distancia = float("inf")
    mejor_recorrido: list[str] = []

    for indice, capital in enumerate(CAPITALES):
        ruta = heuristica.resolver(indice)
        if ruta.distancia_total < mejor_distancia:
            mejor_distancia = ruta.distancia_total
            mejor_capital = capital
            mejor_recorrido = list(ruta.nombres(problema))

    segundos = perf_counter() - inicio

    print(f"Mejor ciudad de partida: {mejor_capital}")
    print(f"Distancia mínima: {mejor_distancia} km")
    print(f"Tiempo de ejecución: {segundos:.6f} s")
    print("Ruta óptima:")
    print(" -> ".join(mejor_recorrido))


def main() -> None:
    """Ejecuta el análisis del ejercicio 2.b."""
    resolver_2b()


if __name__ == "__main__":
    main()
