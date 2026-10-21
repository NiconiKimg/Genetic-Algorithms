"""Resolución exacta del TSP mediante Branch and Bound paralelo."""

import ctypes
import multiprocessing
from multiprocessing.sharedctypes import Synchronized

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

_cota_compartida_global: Synchronized | None = None


def _inicializar_trabajador(cota: Synchronized) -> None:
    """Configura la cota compartida en el espacio de memoria del proceso trabajador."""
    global _cota_compartida_global
    _cota_compartida_global = cota


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

        mejor_heuristica = VecinoMasCercano(self.problema).resolver(self.ciudad_inicial)
        tareas = self._crear_tareas_iniciales()
        if not tareas:
            return ResultadoBranchBound(mejor_heuristica, nodos_explorados=1, nodos_podados=0)

        contexto = multiprocessing.get_context("spawn")
        cota_compartida = contexto.Value(ctypes.c_int, mejor_heuristica.distancia_total)

        if self.cantidad_procesos == 1 or len(tareas) == 1:
            _inicializar_trabajador(cota_compartida)
            resultados = [self._resolver_rama(tarea) for tarea in tareas]
        else:
            with contexto.Pool(
                processes=self.cantidad_procesos,
                initializer=_inicializar_trabajador,
                initargs=(cota_compartida,),
            ) as pool:
                resultados = pool.map(_resolver_rama_en_proceso, tareas)

        # Combinar métricas globales
        candidatos = [r for r in resultados if r.ruta.distancia_total < float("inf")]
        mejor = (
            min(candidatos, key=lambda r: r.ruta.distancia_total)
            if candidatos
            else ResultadoBranchBound(mejor_heuristica, 0, 0)
        )
        total_explorados = sum(r.nodos_explorados for r in resultados)
        total_podados = sum(r.nodos_podados for r in resultados)

        return ResultadoBranchBound(
            ruta=mejor.ruta,
            nodos_explorados=total_explorados,
            nodos_podados=total_podados,
        )

    def _crear_tareas_iniciales(self) -> list[tuple[ProblemaTSP, NodoBusqueda]]:
        """Genera los nodos de nivel 1 ordenados ascendentemente por su límite inferior."""
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
        tareas.sort(key=lambda t: limite_inferior(t[0], t[1]))
        return tareas

    @staticmethod
    def _resolver_rama(
        tarea: tuple[ProblemaTSP, NodoBusqueda],
    ) -> ResultadoBranchBound:
        """Explora una rama del árbol de búsqueda sincronizando la cota con el pool."""
        global _cota_compartida_global
        problema, nodo_inicial = tarea
        mejor_distancia = (
            _cota_compartida_global.value
            if _cota_compartida_global is not None
            else float("inf")
        )
        mejor_ruta: RutaTSP | None = None
        nodos_explorados = 0
        nodos_podados = 0
        pila = [nodo_inicial]

        while pila:
            nodo = pila.pop()
            nodos_explorados += 1
            cota_actual = (
                _cota_compartida_global.value
                if _cota_compartida_global is not None
                else mejor_distancia
            )
            limite = limite_inferior(problema, nodo)
            if limite >= cota_actual:
                nodos_podados += 1
                continue

            if not nodo.no_visitadas:
                distancia_total = nodo.distancia_actual + problema.distancia(
                    nodo.recorrido[-1], nodo.recorrido[0]
                )
                if _cota_compartida_global is not None and distancia_total < _cota_compartida_global.value:
                    with _cota_compartida_global.get_lock():
                        if distancia_total < _cota_compartida_global.value:
                            _cota_compartida_global.value = distancia_total
                if distancia_total <= mejor_distancia:
                    mejor_distancia = distancia_total
                    mejor_ruta = RutaTSP(
                        nodo.recorrido + (nodo.recorrido[0],), distancia_total
                    )
                continue

            hijos = expandir_nodo(nodo, problema)
            hijos.sort(key=lambda hijo: limite_inferior(problema, hijo), reverse=True)
            pila.extend(hijos)

        ruta_retorno = mejor_ruta if mejor_ruta is not None else RutaTSP((), float("inf"))
        return ResultadoBranchBound(
            ruta=ruta_retorno,
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