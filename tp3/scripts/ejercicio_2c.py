"""Ejercicio 2.c: resolver el TSP mediante algoritmo genético."""

from pathlib import Path
import sys

RAIZ_TP3 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_TP3 / "src"))

from comun.datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
from comun.modelos_tsp import ProblemaTSP
from genetico.algoritmo_genetico_tsp import AlgoritmoGeneticoTSP
from genetico.configuracion_genetica import ConfiguracionGenetica


def main() -> None:
    """Ejecuta el algoritmo genético sobre las 24 capitales argentinas."""
    problema = ProblemaTSP(CAPITALES, DISTANCIAS_KM)
    configuracion = ConfiguracionGenetica(
        cantidad_cromosomas=50,
        cantidad_ciclos=200,
        frecuencia_crossover=0.90,
        frecuencia_mutacion=0.10,
        tamano_torneo=3,
    )
    resultado = AlgoritmoGeneticoTSP(problema, configuracion).resolver()
    nombres = resultado.ruta.nombres(problema)

    print(f"Población: {configuracion.cantidad_cromosomas}")
    print(f"Ciclos: {configuracion.cantidad_ciclos}")
    print(f"Crossover cíclico: {configuracion.frecuencia_crossover:.0%}")
    print(f"Mutación: {configuracion.frecuencia_mutacion:.0%}")
    print(f"Distancia encontrada: {resultado.ruta.distancia_total} km")
    print(f"Tiempo de ejecución: {resultado.segundos:.6f} s")
    print("Ruta:")
    print(" -> ".join(nombres))


if __name__ == "__main__":
    main()