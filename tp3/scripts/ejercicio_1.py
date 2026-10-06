"""Ejercicio 1: resolución exhaustiva / Branch and Bound del TSP."""

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from time import perf_counter

RAIZ_TP3 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_TP3 / "src"))

from branch_bound.branch_bound import BranchBound, ResultadoBranchBound
from comun.datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
from comun.modelos_tsp import ProblemaTSP, RutaTSP


@dataclass(frozen=True)
class InformeEjercicio:
    """Resultado del ejercicio y métricas de ejecución."""

    ruta: RutaTSP
    segundos: float
    nodos_explorados: int
    nodos_podados: int

    def texto(self, problema: ProblemaTSP) -> str:
        """Formatea las métricas principales y la ruta hallada."""
        nombres_ruta = " -> ".join(self.ruta.nombres(problema))
        porcentaje_poda = (
            100 * self.nodos_podados / self.nodos_explorados
            if self.nodos_explorados
            else 0
        )
        return "\n".join(
            (
                f"Ciudades: {problema.cantidad_ciudades}",
                f"Ciudad inicial: {problema.nombre_ciudad(self.ruta.recorrido[0])}",
                f"Distancia mínima: {self.ruta.distancia_total} km",
                f"Tiempo de ejecución: {self.segundos:.6f} s",
                f"Nodos explorados: {self.nodos_explorados}",
                f"Nodos podados: {self.nodos_podados} ({porcentaje_poda:.2f}%)",
                "Ruta óptima:",
                nombres_ruta,
            )
        )


def crear_problema(cantidad_ciudades: int | None = None) -> ProblemaTSP:
    """Construye el problema completo o un subconjunto de prefijo para pruebas."""
    cantidad = cantidad_ciudades or len(CAPITALES)
    if not 1 <= cantidad <= len(CAPITALES):
        raise ValueError(f"La cantidad debe estar entre 1 y {len(CAPITALES)}.")
    indices = range(cantidad)
    return ProblemaTSP(
        tuple(CAPITALES[indice] for indice in indices),
        tuple(
            tuple(DISTANCIAS_KM[fila][columna] for columna in indices)
            for fila in indices
        ),
    )


def validar_ruta(problema: ProblemaTSP, ruta: RutaTSP) -> None:
    """Verifica que la ruta visite cada ciudad exactamente una vez y retorne al origen."""
    recorrido_sin_cierre = ruta.recorrido[:-1]
    if ruta.recorrido[0] != ruta.recorrido[-1]:
        raise ValueError("La ruta no vuelve a la ciudad inicial.")
    if len(recorrido_sin_cierre) != problema.cantidad_ciudades:
        raise ValueError("La ruta no contiene todas las ciudades.")
    if len(set(recorrido_sin_cierre)) != problema.cantidad_ciudades:
        raise ValueError("La ruta repite alguna ciudad.")


def resolver_ejercicio(problema: ProblemaTSP) -> InformeEjercicio:
    """Ejecuta Branch and Bound sobre la instancia del problema y mide su rendimiento."""
    inicio = perf_counter()
    resultado: ResultadoBranchBound = BranchBound(problema).resolver()
    segundos = perf_counter() - inicio
    validar_ruta(problema, resultado.ruta)
    return InformeEjercicio(
        ruta=resultado.ruta,
        segundos=segundos,
        nodos_explorados=resultado.nodos_explorados,
        nodos_podados=resultado.nodos_podados,
    )


def main() -> None:
    """Punto de entrada principal para el Ejercicio 1."""
    parser = argparse.ArgumentParser(
        description="Ejercicio 1: Resolución exacta por Branch and Bound."
    )
    parser.add_argument(
        "--ciudades",
        type=int,
        default=10,
        help="Cantidad de ciudades a resolver con B&B (por defecto: 10 para ejecución ágil).",
    )
    argumentos = parser.parse_args()

    problema = crear_problema(argumentos.ciudades)
    informe = resolver_ejercicio(problema)
    print(informe.texto(problema))


if __name__ == "__main__":
    main()