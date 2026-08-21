"""Poblacion reutilizable de individuos para el algoritmo genetico TSP."""

import random

try:
    from .modelos_tsp import EvaluadorRutas, IndividuoTSP, RutaTSP
except ImportError:
    from modelos_tsp import EvaluadorRutas, IndividuoTSP, RutaTSP


class PoblacionTSP:
    """Administra individuos, evaluacion y elitismo de una poblacion."""

    def __init__(self, individuos: list[IndividuoTSP]) -> None:
        if not individuos:
            raise ValueError("La poblacion no puede estar vacia.")
        self.individuos = individuos

    @classmethod
    def aleatoria(
        cls,
        ciudades: tuple[int, ...],
        cantidad: int,
        generador: random.Random,
    ) -> "PoblacionTSP":
        if cantidad < 1:
            raise ValueError("La cantidad de individuos debe ser positiva.")
        individuos = [
            IndividuoTSP(tuple(generador.sample(ciudades, len(ciudades))))
            for _ in range(cantidad)
        ]
        return cls(individuos)

    def evaluar(self, evaluador: EvaluadorRutas, ciudad_inicial: int = 0) -> None:
        self.individuos = [
            individuo.evaluar(evaluador, ciudad_inicial)
            for individuo in self.individuos
        ]

    def mejor(self) -> IndividuoTSP:
        return min(
            self.individuos,
            key=lambda individuo: individuo.distancia_total
            if individuo.distancia_total is not None
            else float("inf"),
        )

    def mejor_ruta(
        self,
        evaluador: EvaluadorRutas,
        ciudad_inicial: int = 0,
    ) -> RutaTSP:
        return self.mejor().ruta(evaluador, ciudad_inicial)

    def conservar_elite(self, individuo: IndividuoTSP) -> None:
        """Reemplaza el peor individuo por el elite si este es mejor."""
        peor = max(
            range(len(self.individuos)),
            key=lambda indice: self.individuos[indice].distancia_total
            if self.individuos[indice].distancia_total is not None
            else float("inf"),
        )
        if (
            individuo.distancia_total is not None
            and (
                self.individuos[peor].distancia_total is None
                or individuo.distancia_total < self.individuos[peor].distancia_total
            )
        ):
            self.individuos[peor] = individuo