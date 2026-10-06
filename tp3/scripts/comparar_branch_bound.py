"""Compara el desempeño entre Branch and Bound secuencial y paralelo."""

from dataclasses import dataclass
from pathlib import Path
import sys
from time import perf_counter

RAIZ_TP3 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_TP3 / "src"))

from branch_bound.branch_bound import BranchBound
from branch_bound.branch_bound_paralelo import BranchBoundParalelo
from comun.datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
from comun.modelos_tsp import ProblemaTSP


@dataclass(frozen=True)
class Medicion:
    """Métricas registradas para una corrida de prueba."""

    ciudades: int
    algoritmo: str
    segundos: float
    distancia: int
    nodos_explorados: int
    nodos_podados: int


def crear_subproblema(cantidad_ciudades: int) -> ProblemaTSP:
    """Crea una instancia acotada con las primeras N capitales."""
    indices = range(cantidad_ciudades)
    return ProblemaTSP(
        tuple(CAPITALES[indice] for indice in indices),
        tuple(
            tuple(DISTANCIAS_KM[fila][columna] for columna in indices)
            for fila in indices
        ),
    )


def medir(algoritmo: str, problema: ProblemaTSP) -> Medicion:
    """Ejecuta una variante del solver y retorna el tiempo y las podas realizadas."""
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
        ciudades=problema.cantidad_ciudades,
        algoritmo=algoritmo,
        segundos=segundos,
        distancia=resultado.ruta.distancia_total,
        nodos_explorados=resultado.nodos_explorados,
        nodos_podados=resultado.nodos_podados,
    )


def main() -> None:
    """Ejecuta la batería de pruebas comparativas en instancias reducidas."""
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