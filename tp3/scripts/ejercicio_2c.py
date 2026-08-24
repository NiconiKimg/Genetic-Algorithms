"""Ejercicio 2.c: resolver el TSP mediante algoritmo genetico."""

from pathlib import Path
import sys

RAIZ_TP3 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_TP3 / "src"))

from algoritmo_genetico_tsp import AlgoritmoGeneticoTSP
from configuracion_genetica import ConfiguracionGenetica
from datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
from modelos_tsp import ProblemaTSP


def main() -> None:
    problema = ProblemaTSP(CAPITALES, DISTANCIAS_KM)
    configuracion = ConfiguracionGenetica(
        cantidad_cromosomas=50,
        cantidad_ciclos=200,
        frecuencia_crossover=0.90,
        frecuencia_mutacion=0.10,
        semilla=42,
    )
    resultado = AlgoritmoGeneticoTSP(problema, configuracion).resolver()
    print("EJERCICIO 2.c - ALGORITMO GENETICO")
    print(f"Poblacion: {configuracion.cantidad_cromosomas}")
    print(f"Ciclos: {configuracion.cantidad_ciclos}")
    print(f"Crossover ciclico: {configuracion.frecuencia_crossover:.0%}")
    print(f"Mutacion por intercambio: {configuracion.frecuencia_mutacion:.0%}")
    print(f"Distancia encontrada: {resultado.ruta.distancia_total} km")
    print(f"Tiempo de ejecucion: {resultado.segundos:.6f} s")
    print(" -> ".join(resultado.ruta.nombres(problema)))


if __name__ == "__main__":
    main()