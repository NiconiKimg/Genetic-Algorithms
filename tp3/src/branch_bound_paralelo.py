"""Resolucion exacta del TSP mediante Branch and Bound paralelo."""

from dataclasses import dataclass
import multiprocessing
from typing import Iterable

try:
    from .datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
    from .modelos_tsp import NodoBusqueda, ProblemaTSP, RutaTSP
except ImportError:
    from datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
    from modelos_tsp import NodoBusqueda, ProblemaTSP, RutaTSP


@dataclass(frozen=True)
class ResultadoBusqueda:
    """Resultado del solver junto con estadisticas de poda."""

    ruta: RutaTSP
    nodos_explorados: int
    nodos_podados: int


class BranchBoundParalelo:
    """Solver exacto que procesa en paralelo las ramas iniciales del TSP."""

    def __init__(
        self,
        problema: ProblemaTSP,
        ciudad_inicial: int = 0,
        cantidad_procesos: int | None = None,
    ) -> None:
        if not 0 <= ciudad_inicial < problema.cantidad_ciudades:
            raise ValueError("La ciudad inicial no existe en el problema.")
        self.problema = problema
        self.ciudad_inicial = ciudad_inicial
        self.cantidad_procesos = cantidad_procesos or multiprocessing.cpu_count()

    def resolver(self) -> ResultadoBusqueda:
        """Busca la ruta optima combinando el mejor resultado de cada rama."""
        if self.problema.cantidad_ciudades == 1:
            ruta = RutaTSP((self.ciudad_inicial, self.ciudad_inicial), 0)
            return ResultadoBusqueda(ruta, nodos_explorados=1, nodos_podados=0)

        tareas = self._crear_tareas_iniciales()
        if self.cantidad_procesos == 1 or len(tareas) == 1:
            resultados = [self._resolver_rama(tarea) for tarea in tareas]
        else:
            contexto = multiprocessing.get_context("spawn")
            with contexto.Pool(processes=self.cantidad_procesos) as pool:
                resultados = pool.map(_resolver_rama_en_proceso, tareas)

        return min(resultados, key=lambda resultado: resultado.ruta.distancia_total)

    def _crear_tareas_iniciales(self) -> list[tuple[ProblemaTSP, NodoBusqueda]]:
        no_visitadas = frozenset(
            indice
            for indice in range(self.problema.cantidad_ciudades)
            if indice != self.ciudad_inicial
        )
        tareas: list[tuple[ProblemaTSP, NodoBusqueda]] = []
        for siguiente in sorted(no_visitadas):
            nodo = NodoBusqueda(
                recorrido=(self.ciudad_inicial, siguiente),
                no_visitadas=no_visitadas - {siguiente},
                distancia_actual=self.problema.distancia(
                    self.ciudad_inicial, siguiente
                ),
            )
            tareas.append((self.problema, nodo))
        return tareas

    @staticmethod
    def _resolver_rama(
        tarea: tuple[ProblemaTSP, NodoBusqueda],
    ) -> ResultadoBusqueda:
        problema, nodo_inicial = tarea
        mejor_ruta = _ruta_vecino_mas_cercano(problema, nodo_inicial.recorrido[0])
        nodos_explorados = 0
        nodos_podados = 0
        pila = [nodo_inicial]

        while pila:
            nodo = pila.pop()
            nodos_explorados += 1
            limite = _limite_inferior(problema, nodo)
            if limite >= mejor_ruta.distancia_total:
                nodos_podados += 1
                continue

            if not nodo.no_visitadas:
                distancia_total = nodo.distancia_actual + problema.distancia(
                    nodo.recorrido[-1], nodo.recorrido[0]
                )
                if distancia_total < mejor_ruta.distancia_total:
                    mejor_ruta = RutaTSP(
                        nodo.recorrido + (nodo.recorrido[0],), distancia_total
                    )
                continue

            hijos = _expandir(nodo, problema)
            hijos.sort(key=lambda hijo: _limite_inferior(problema, hijo), reverse=True)
            pila.extend(hijos)

        return ResultadoBusqueda(mejor_ruta, nodos_explorados, nodos_podados)


def _resolver_rama_en_proceso(
    tarea: tuple[ProblemaTSP, NodoBusqueda],
) -> ResultadoBusqueda:
    return BranchBoundParalelo._resolver_rama(tarea)


def _expandir(nodo: NodoBusqueda, problema: ProblemaTSP) -> list[NodoBusqueda]:
    return [
        NodoBusqueda(
            recorrido=nodo.recorrido + (siguiente,),
            no_visitadas=nodo.no_visitadas - {siguiente},
            distancia_actual=nodo.distancia_actual
            + problema.distancia(nodo.recorrido[-1], siguiente),
        )
        for siguiente in nodo.no_visitadas
    ]


def _limite_inferior(problema: ProblemaTSP, nodo: NodoBusqueda) -> int:
    if not nodo.no_visitadas:
        return nodo.distancia_actual + problema.distancia(
            nodo.recorrido[-1], nodo.recorrido[0]
        )

    costo_mst = _costo_arbol_generador_minimo(problema, nodo.no_visitadas)
    salida = min(
        problema.distancia(nodo.recorrido[-1], ciudad)
        for ciudad in nodo.no_visitadas
    )
    retorno = min(
        problema.distancia(ciudad, nodo.recorrido[0]) for ciudad in nodo.no_visitadas
    )
    return nodo.distancia_actual + costo_mst + salida + retorno


def _costo_arbol_generador_minimo(
    problema: ProblemaTSP,
    ciudades: Iterable[int],
) -> int:
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


def _ruta_vecino_mas_cercano(problema: ProblemaTSP, ciudad_inicial: int) -> RutaTSP:
    recorrido = [ciudad_inicial]
    no_visitadas = set(range(problema.cantidad_ciudades)) - {ciudad_inicial}
    distancia_total = 0

    while no_visitadas:
        siguiente = min(
            no_visitadas,
            key=lambda ciudad: problema.distancia(recorrido[-1], ciudad),
        )
        distancia_total += problema.distancia(recorrido[-1], siguiente)
        recorrido.append(siguiente)
        no_visitadas.remove(siguiente)

    distancia_total += problema.distancia(recorrido[-1], ciudad_inicial)
    recorrido.append(ciudad_inicial)
    return RutaTSP(tuple(recorrido), distancia_total)


def crear_problema_capitales() -> ProblemaTSP:
    """Construye la instancia del enunciado con las capitales argentinas."""
    return ProblemaTSP(CAPITALES, DISTANCIAS_KM)


if __name__ == "__main__":
    solver = BranchBoundParalelo(crear_problema_capitales())
    resultado = solver.resolver()
    print(f"Distancia optima: {resultado.ruta.distancia_total} km")
    print(" -> ".join(resultado.ruta.nombres(solver.problema)))
    print(f"Nodos explorados: {resultado.nodos_explorados}")
    print(f"Nodos podados: {resultado.nodos_podados}")