"""Compara el Branch and Bound secuencial y el paralelo."""

from dataclasses import dataclass
import sys
from time import perf_counter

sys.path.insert(0, "tp3/src")

from branch_bound import BranchBound
from branch_bound_paralelo import BranchBoundParalelo
from datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
from modelos_tsp import ProblemaTSP


@dataclass(frozen=True)
class Medicion:
    ciudades: int
    algoritmo: str
    segundos: float
    distancia: int
    nodos_explorados: int
    nodos_podados: int


def crear_subproblema(cantidad_ciudades: int) -> ProblemaTSP:
    indices = range(cantidad_ciudades)
    return ProblemaTSP(
        tuple(CAPITALES[indice] for indice in indices),
        tuple(
            tuple(DISTANCIAS_KM[fila][columna] for columna in indices)
            for fila in indices
        ),
    )


def medir(algoritmo: str, problema: ProblemaTSP) -> Medicion:
    inicio = perf_counter()
    if algoritmo == "secuencial":
        resultado = BranchBound(problema).resolver()
    else:
        resultado = BranchBoundParalelo(
            problema,
            cantidad_procesos=2,
        ).resolver()
    segundos = perf_counter() - inicio
    return Medicion(
        problema.cantidad_ciudades,
        algoritmo,
        segundos,
        resultado.ruta.distancia_total,
        resultado.nodos_explorados,
        resultado.nodos_podados,
    )


def main() -> None:
    print("ciudades;algoritmo;segundos;distancia_km;nodos_explorados;nodos_podados")
    for cantidad_ciudades in (8, 10, 12):
        problema = crear_subproblema(cantidad_ciudades)
        for algoritmo in ("secuencial", "paralelo"):
            medicion = medir(algoritmo, problema)
            print(
                f"{medicion.ciudades};{medicion.algoritmo};"
                f"{medicion.segundos:.6f};{medicion.distancia};"
                f"{medicion.nodos_explorados};{medicion.nodos_podados}"
            )


if __name__ == "__main__":
    main()