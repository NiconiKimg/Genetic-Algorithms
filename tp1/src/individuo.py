import random
from typing import Callable, Optional

class Individuo:
    funcion_objetivo: Callable[[int], float]
    genes: list[int]
    valor_funcion_objetivo: float
    fitness: Optional[float]
    
    def __init__(self, funcion_objetivo: Callable[[int], float], genes: Optional[list[int]] = None) -> None:
        self.funcion_objetivo = funcion_objetivo
        self.genes = genes if genes is not None else self.generar()
        self.valor_funcion_objetivo = self.evaluar_funcion_objetivo(funcion_objetivo)
        self.fitness = None

    def generar(self) -> list[int]:
        return [random.randint(0, 1) for _ in range(30)]

    def decodificar(self) -> int:
        binario = ''.join(str(g) for g in self.genes)
        return int(binario, 2)
    
    def evaluar_funcion_objetivo(self, funcion_objetivo: Callable[[int], float]) -> float:
        x = self.decodificar()
        return funcion_objetivo(x)
    
    def calcular_fitness(self, total_funcion_poblacion : float) -> None:
        self.fitness = self.valor_funcion_objetivo / total_funcion_poblacion
        
    def actualizar(self) -> None:
        self.valor_funcion_objetivo = self.evaluar_funcion_objetivo(self.funcion_objetivo)
        