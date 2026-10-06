"""Ejercicio 2.a: heurística del vecino más cercano desde una capital de partida."""

import argparse
from pathlib import Path
import sys
from time import perf_counter

RAIZ_TP3 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_TP3 / "src"))

from comun.datos_distancia_capitales import CAPITALES, DISTANCIAS_KM, INDICE_CAPITALES
from comun.modelos_tsp import ProblemaTSP
from heuristica.heuristica_vecino import VecinoMasCercano


def resolver_2a(capital_inicial: str) -> None:
    """Ejecuta la heurística desde la capital indicada e imprime el resultado."""
    if capital_inicial not in INDICE_CAPITALES:
        raise ValueError(f"Capital no reconocida: '{capital_inicial}'.")

    indice_inicial = INDICE_CAPITALES[capital_inicial]
    problema = ProblemaTSP(CAPITALES, DISTANCIAS_KM)

    inicio = perf_counter()
    ruta = VecinoMasCercano(problema).resolver(indice_inicial)
    segundos = perf_counter() - inicio
    nombres = ruta.nombres(problema)

    print(f"Ciudad de partida: {capital_inicial}")
    print(f"Distancia total: {ruta.distancia_total} km")
    print(f"Tiempo de ejecución: {segundos:.6f} s")
    print("Ruta:")
    print(" -> ".join(nombres))


def main() -> None:
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Ejercicio 2.a: Heurística del vecino más cercano desde una capital."
    )
    parser.add_argument(
        "--ciudad",
        type=str,
        default=None,
        help="Nombre exacto de la capital de partida (por defecto: Ciudad de Buenos Aires).",
    )
    argumentos = parser.parse_args()

    ciudad = argumentos.ciudad or "Ciudad de Buenos Aires"
    resolver_2a(ciudad)


if __name__ == "__main__":
    main()
