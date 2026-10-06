"""Población reutilizable de individuos para el algoritmo genético TSP."""

import random

from comun.modelos_tsp import EvaluadorRutas, IndividuoTSP, RutaTSP


class PoblacionTSP:
    """Administra la colección de cromosomas, su evaluación y el elitismo."""

    def __init__(self, individuos: list[IndividuoTSP]) -> None:
        """Inicializa la población con una lista no vacía de individuos."""
        if not individuos:
            raise ValueError("La población no puede estar vacía.")
        self.individuos = individuos

    @classmethod
    def aleatoria(
        cls,
        ciudades: tuple[int, ...],
        cantidad: int,
        generador: random.Random,
    ) -> "PoblacionTSP":
        """Genera una población inicial con permutaciones aleatorias de las ciudades."""
        if cantidad < 1:
            raise ValueError("La cantidad de individuos debe ser positiva.")
        individuos = [
            IndividuoTSP(tuple(generador.sample(ciudades, len(ciudades))))
            for _ in range(cantidad)
        ]
        return cls(individuos)

    def evaluar(self, evaluador: EvaluadorRutas, ciudad_inicial: int = 0) -> None:
        """Evalúa y asigna la distancia total de cada individuo en la población."""
        self.individuos = [
            individuo.evaluar(evaluador, ciudad_inicial)
            for individuo in self.individuos
        ]

    def mejor(self) -> IndividuoTSP:
        """Retorna el individuo con la menor distancia total de la población."""
        return min(
            self.individuos,
            key=lambda individuo: (
                individuo.distancia_total
                if individuo.distancia_total is not None
                else float("inf")
            ),
        )

    def mejor_ruta(
        self,
        evaluador: EvaluadorRutas,
        ciudad_inicial: int = 0,
    ) -> RutaTSP:
        """Convierte y retorna el mejor individuo como una RutaTSP cerrada."""
        return self.mejor().ruta(evaluador, ciudad_inicial)

    def conservar_elite(self, individuo: IndividuoTSP) -> None:
        """Reemplaza al peor individuo de la población por el individuo élite si este lo supera."""
        peor = max(
            range(len(self.individuos)),
            key=lambda indice: (
                self.individuos[indice].distancia_total
                if self.individuos[indice].distancia_total is not None
                else float("inf")
            ),
        )
        if (
            individuo.distancia_total is not None
            and (
                self.individuos[peor].distancia_total is None
                or individuo.distancia_total < self.individuos[peor].distancia_total
            )
        ):
            self.individuos[peor] = individuo