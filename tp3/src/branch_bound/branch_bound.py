"""Resolución secuencial del TSP mediante Branch and Bound."""

from dataclasses import dataclass
from typing import Iterable

from comun.datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
from comun.modelos_tsp import NodoBusqueda, ProblemaTSP, RutaTSP
from heuristica.heuristica_vecino import VecinoMasCercano


@dataclass(frozen=True)
class ResultadoBranchBound:
    """Resultado del algoritmo Branch and Bound junto a sus métricas de búsqueda."""

    ruta: RutaTSP
    nodos_explorados: int
    nodos_podados: int


def costo_arbol_generador_minimo(
    problema: ProblemaTSP,
    ciudades: Iterable[int],
) -> int:
    """Calcula el costo del Árbol Generador Mínimo (MST) sobre un conjunto de ciudades mediante Prim."""
    pendientes = set(ciudades)
    if len(pendientes) < 2:
        return 0

    incluidos = {pendientes.pop()}
    costo_total = 0
    while pendientes:
        distancia, ciudad = min(
            (
                (problema.distancia(incluida, candidata), candidata)
                for incluida in incluidos
                for candidata in pendientes
            ),
            key=lambda elemento: elemento[0],
        )
        incluidos.add(ciudad)
        pendientes.remove(ciudad)
        costo_total += distancia
    return costo_total


def limite_inferior(problema: ProblemaTSP, nodo: NodoBusqueda) -> int:
    """Calcula la cota inferior admisible para el nodo parcial usando MST + aristas de conexión."""
    if not nodo.no_visitadas:
        return nodo.distancia_actual + problema.distancia(
            nodo.recorrido[-1], nodo.recorrido[0]
        )

    costo_mst = costo_arbol_generador_minimo(problema, nodo.no_visitadas)
    salida = min(
        problema.distancia(nodo.recorrido[-1], ciudad)
        for ciudad in nodo.no_visitadas
    )
    retorno = min(
        problema.distancia(ciudad, nodo.recorrido[0])
        for ciudad in nodo.no_visitadas
    )
    return nodo.distancia_actual + costo_mst + salida + retorno


def expandir_nodo(nodo: NodoBusqueda, problema: ProblemaTSP) -> list[NodoBusqueda]:
    """Genera los nodos sucesores a partir de las ciudades no visitadas."""
    return [
        NodoBusqueda(
            recorrido=nodo.recorrido + (siguiente,),
            no_visitadas=nodo.no_visitadas - {siguiente},
            distancia_actual=nodo.distancia_actual
            + problema.distancia(nodo.recorrido[-1], siguiente),
        )
        for siguiente in nodo.no_visitadas
    ]


def crear_problema_capitales() -> ProblemaTSP:
    """Construye la instancia del enunciado con las 24 capitales argentinas."""
    return ProblemaTSP(CAPITALES, DISTANCIAS_KM)


class BranchBound:
    """Solver exacto secuencial con poda por cota inferior y cota superior voraz inicial."""

    def __init__(self, problema: ProblemaTSP, ciudad_inicial: int = 0) -> None:
        """Inicializa el solver con la instancia del problema y la ciudad de partida."""
        if not 0 <= ciudad_inicial < problema.cantidad_ciudades:
            raise ValueError("La ciudad inicial no existe en el problema.")
        self.problema = problema
        self.ciudad_inicial = ciudad_inicial

    def resolver(self) -> ResultadoBranchBound:
        """Explora el espacio de búsqueda podando ramas cuya cota no mejore la mejor ruta conocida."""
        mejor_ruta = VecinoMasCercano(self.problema).resolver(self.ciudad_inicial)
        nodo_inicial = NodoBusqueda(
            recorrido=(self.ciudad_inicial,),
            no_visitadas=frozenset(
                indice
                for indice in range(self.problema.cantidad_ciudades)
                if indice != self.ciudad_inicial
            ),
            distancia_actual=0,
        )
        pila = [nodo_inicial]
        nodos_explorados = 0
        nodos_podados = 0

        while pila:
            nodo = pila.pop()
            nodos_explorados += 1

            if limite_inferior(self.problema, nodo) >= mejor_ruta.distancia_total:
                nodos_podados += 1
                continue

            if not nodo.no_visitadas:
                distancia_total = nodo.distancia_actual + self.problema.distancia(
                    nodo.recorrido[-1], self.ciudad_inicial
                )
                if distancia_total < mejor_ruta.distancia_total:
                    mejor_ruta = RutaTSP(
                        nodo.recorrido + (self.ciudad_inicial,), distancia_total
                    )
                continue

            hijos = expandir_nodo(nodo, self.problema)
            hijos.sort(
                key=lambda hijo: limite_inferior(self.problema, hijo),
                reverse=True,
            )
            pila.extend(hijos)

        return ResultadoBranchBound(
            ruta=mejor_ruta,
            nodos_explorados=nodos_explorados,
            nodos_podados=nodos_podados,
        )


if __name__ == "__main__":
    solver = BranchBound(crear_problema_capitales())
    resultado = solver.resolver()
    print(f"Distancia óptima: {resultado.ruta.distancia_total} km")