"""Ejercicio 1: ruta minima entre las capitales argentinas."""

from dataclasses import dataclass
from pathlib import Path
import argparse
import sys
from time import perf_counter

RAIZ_TP3 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_TP3 / "src"))

from branch_bound.branch_bound import BranchBound, ResultadoBranchBound
from comun.datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
from comun.modelos_tsp import ProblemaTSP, RutaTSP


@dataclass(frozen=True)
class InformeEjercicio:
    """Resultado presentable del ejercicio y metricas de ejecucion."""

    ruta: RutaTSP
    segundos: float
    nodos_explorados: int
    nodos_podados: int

    def texto(self, problema: ProblemaTSP) -> str:
        nombres_ruta = " -> ".join(self.ruta.nombres(problema))
        porcentaje_poda = (
            100 * self.nodos_podados / self.nodos_explorados
            if self.nodos_explorados
            else 0
        )
        return "\n".join(
            (
                "EJERCICIO 1 - PROBLEMA DEL VIAJANTE",
                "=" * 44,
                f"Ciudades: {problema.cantidad_ciudades}",
                f"Ciudad inicial: {problema.nombre_ciudad(self.ruta.recorrido[0])}",
                f"Distancia minima: {self.ruta.distancia_total} km",
                f"Tiempo de ejecucion: {self.segundos:.6f} s",
                f"Nodos explorados: {self.nodos_explorados}",
                f"Nodos podados: {self.nodos_podados} ({porcentaje_poda:.2f}%)",
                "Ruta optima:",
                nombres_ruta,
                "",
                "Justificacion teorica:",
                "Branch and Bound es exacto porque solo poda una rama cuando su cota",
                "inferior ya no puede mejorar la mejor ruta conocida.",
                f"Con {problema.cantidad_ciudades} ciudades se fijan el origen y el retorno,",
                f"por lo que la fuerza bruta tendria que revisar ({problema.cantidad_ciudades}-1)! rutas.",
                "El metodo puede resolver el problema, pero el crecimiento factorial",
                "hace que la ejecucion completa sea costosa para 24 ciudades.",
            )
        )


def crear_problema(cantidad_ciudades: int | None = None) -> ProblemaTSP:
    """Construye el problema completo o un prefijo para pruebas."""
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
    """Verifica que la ruta visite cada ciudad una sola vez y vuelva al origen."""
    recorrido_sin_cierre = ruta.recorrido[:-1]
    if ruta.recorrido[0] != ruta.recorrido[-1]:
        raise ValueError("La ruta no vuelve a la ciudad inicial.")
    if len(recorrido_sin_cierre) != problema.cantidad_ciudades:
        raise ValueError("La ruta no contiene todas las ciudades.")
    if len(set(recorrido_sin_cierre)) != problema.cantidad_ciudades:
        raise ValueError("La ruta repite alguna ciudad.")


def resolver_ejercicio(problema: ProblemaTSP) -> InformeEjercicio:
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ciudades",
        type=int,
        default=None,
        help="Cantidad de primeras ciudades para una prueba (por defecto, 24).",
    )
    argumentos = parser.parse_args()
    problema = crear_problema(argumentos.ciudades)
    informe = resolver_ejercicio(problema)
    print(informe.texto(problema))


if __name__ == "__main__":
    main()