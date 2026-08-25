"""Resolucion secuencial del TSP mediante Branch and Bound."""

from dataclasses import dataclass

try:
    from .branch_bound_paralelo import (
        _costo_arbol_generador_minimo,
        _limite_inferior,
        _ruta_vecino_mas_cercano,
        crear_problema_capitales,
    )
    from comun.modelos_tsp import NodoBusqueda, ProblemaTSP, RutaTSP
except ImportError:
    from branch_bound_paralelo import (
        _costo_arbol_generador_minimo,
        _limite_inferior,
        _ruta_vecino_mas_cercano,
        crear_problema_capitales,
    )
    from comun.modelos_tsp import NodoBusqueda, ProblemaTSP, RutaTSP


@dataclass(frozen=True)
class ResultadoBranchBound:
    """Resultado del algoritmo y sus estadisticas de busqueda."""

    ruta: RutaTSP
    nodos_explorados: int
    nodos_podados: int


class BranchBound:
    """Solver exacto secuencial con una unica mejor solucion global."""

    def __init__(self, problema: ProblemaTSP, ciudad_inicial: int = 0) -> None:
        if not 0 <= ciudad_inicial < problema.cantidad_ciudades:
            raise ValueError("La ciudad inicial no existe en el problema.")
        self.problema = problema
        self.ciudad_inicial = ciudad_inicial

    def resolver(self) -> ResultadoBranchBound:
        """Explora el arbol completo aplicando la cota inferior en cada nodo."""
        mejor_ruta = _ruta_vecino_mas_cercano(self.problema, self.ciudad_inicial)
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

            if _limite_inferior(self.problema, nodo) >= mejor_ruta.distancia_total:
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

            hijos = [
                NodoBusqueda(
                    recorrido=nodo.recorrido + (siguiente,),
                    no_visitadas=nodo.no_visitadas - {siguiente},
                    distancia_actual=nodo.distancia_actual
                    + self.problema.distancia(nodo.recorrido[-1], siguiente),
                )
                for siguiente in nodo.no_visitadas
            ]
            hijos.sort(
                key=lambda hijo: _limite_inferior(self.problema, hijo),
                reverse=True,
            )
            pila.extend(hijos)

        return ResultadoBranchBound(
            mejor_ruta,
            nodos_explorados=nodos_explorados,
            nodos_podados=nodos_podados,
        )


if __name__ == "__main__":
    solver = BranchBound(crear_problema_capitales())
    resultado = solver.resolver()
    print(f"Distancia optima: {resultado.ruta.distancia_total} km")
    print(" -> ".join(resultado.ruta.nombres(solver.problema)))
    print(f"Nodos explorados: {resultado.nodos_explorados}")
    print(f"Nodos podados: {resultado.nodos_podados}")