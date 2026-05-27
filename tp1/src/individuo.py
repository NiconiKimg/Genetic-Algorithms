import random
from typing import Callable, Optional

class Individuo:
    """Representa a un individuo en la población con su genotipo y aptitud"""
    funcion_objetivo: Callable[[int], float]
    genes: list[int]
    valor_funcion_objetivo: float
    fitness: Optional[float]
    
    def __init__(self, funcion_objetivo: Callable[[int], float], genes: Optional[list[int]] = None) -> None:
        """Inicializa un individuo con genes aleatorios o provistos y evalúa su función objetivo"""
        self.funcion_objetivo = funcion_objetivo
        self.genes = genes if genes is not None else self.generar()
        self.valor_funcion_objetivo = self.evaluar_funcion_objetivo(funcion_objetivo)
        self.fitness = None

    def generar(self) -> list[int]:
        """Genera un cromosoma aleatorio de 30 bits representados como lista de enteros"""
        return [random.randint(0, 1) for _ in range(30)]

    def decodificar(self) -> int:
        """Convierte la representación binaria del cromosoma en su correspondiente valor entero"""
        binario = ''.join(str(g) for g in self.genes)
        return int(binario, 2)
    
    def evaluar_funcion_objetivo(self, funcion_objetivo: Callable[[int], float]) -> float:
        """Calcula el valor de la función objetivo para el individuo decodificado"""
        x = self.decodificar()
        return funcion_objetivo(x)
    
    def calcular_fitness(self, total_funcion_poblacion : float) -> None:
        """Calcula la aptitud relativa (fitness) en base al total de la población"""
        self.fitness = self.valor_funcion_objetivo / total_funcion_poblacion
        
    def actualizar(self) -> None:
        """Recalcula y actualiza el valor de la función objetivo"""
        self.valor_funcion_objetivo = self.evaluar_funcion_objetivo(self.funcion_objetivo)
        