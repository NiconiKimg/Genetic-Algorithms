"""Resolución exacta del TSP mediante Branch and Bound paralelo."""

import multiprocessing

try:
    from .branch_bound import (
        ResultadoBranchBound,
        crear_problema_capitales,
        expandir_nodo,
        limite_inferior,
    )
except ImportError:
    from branch_bound.branch_bound import (
        ResultadoBranchBound,
        crear_problema_capitales,
        expandir_nodo,
        limite_inferior,
    )

from comun.modelos_tsp import NodoBusqueda, ProblemaTSP, RutaTSP
from heuristica.heuristica_vecino import VecinoMasCercano


def _resolver_rama_en_proceso(
    tarea: tuple[ProblemaTSP, NodoBusqueda],
) -> ResultadoBranchBound:
    """Función de nivel superior ejecutable por cada proceso del pool."""
    return BranchBoundParalelo._resolver_rama(tarea)


class BranchBoundParalelo:
    """Solver exacto que distribuye las ramas iniciales del árbol en procesos paralelos."""

    def __init__(
        self,
        problema: ProblemaTSP,
        ciudad_inicial: int = 0,
        cantidad_procesos: int | None = None,
    ) -> None:
        """Inicializa el solver paralelo configurando la cantidad de procesos."""
        if not 0 <= ciudad_inicial < problema.cantidad_ciudades:
            raise ValueError("La ciudad inicial no existe en el problema.")
        self.problema = problema
        self.ciudad_inicial = ciudad_inicial
        self.cantidad_procesos = cantidad_procesos or multiprocessing.cpu_count()

    def resolver(self) -> ResultadoBranchBound:
        """Busca la ruta óptima combinando el mejor resultado obtenido en cada subárbol."""
        if self.problema.cantidad_ciudades == 1:
            ruta = RutaTSP((self.ciudad_inicial, self.ciudad_inicial), 0)
            return ResultadoBranchBound(ruta, nodos_explorados=1, nodos_podados=0)

        tareas = self._crear_tareas_iniciales()
        if self.cantidad_procesos == 1 or len(tareas) == 1:
            resultados = [self._resolver_rama(tarea) for tarea in tareas]
        else:
            contexto = multiprocessing.get_context("spawn")
            with contexto.Pool(processes=self.cantidad_procesos) as pool:
                resultados = pool.map(_resolver_rama_en_proceso, tareas)

        # Combinar métricas globales
        mejor = min(resultados, key=lambda r: r.ruta.distancia_total)
        total_explorados = sum(r.nodos_explorados for r in resultados)
        total_podados = sum(r.nodos_podados for r in resultados)

        return ResultadoBranchBound(
            ruta=mejor.ruta,
            nodos_explorados=total_explorados,
            nodos_podados=total_podados,
        )

    def _crear_tareas_iniciales(self) -> list[tuple[ProblemaTSP, NodoBusqueda]]:
        """Genera los nodos de nivel 1 asignando cada ciudad no visitada como segundo paso."""
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
    ) -> ResultadoBranchBound:
        """Explora una rama del árbol de búsqueda en un proceso independiente."""
        problema, nodo_inicial = tarea
        mejor_ruta = VecinoMasCercano(problema).resolver(nodo_inicial.recorrido[0])
        nodos_explorados = 0
        nodos_podados = 0
        pila = [nodo_inicial]

        while pila:
            nodo = pila.pop()
            nodos_explorados += 1
            limite = limite_inferior(problema, nodo)
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

            hijos = expandir_nodo(nodo, problema)
            hijos.sort(key=lambda hijo: limite_inferior(problema, hijo), reverse=True)
            pila.extend(hijos)

        return ResultadoBranchBound(
            ruta=mejor_ruta,
            nodos_explorados=nodos_explorados,
            nodos_podados=nodos_podados,
        )


if __name__ == "__main__":
    solver = BranchBoundParalelo(crear_problema_capitales())
    resultado = solver.resolver()
    print(f"Distancia óptima: {resultado.ruta.distancia_total} km")
    print(" -> ".join(resultado.ruta.nombres(solver.problema)))
    print(f"Nodos explorados: {resultado.nodos_explorados}")
    print(f"Nodos podados: {resultado.nodos_podados}")