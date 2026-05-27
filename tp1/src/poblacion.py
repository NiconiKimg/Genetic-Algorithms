from typing import Callable, Optional
from individuo import Individuo

class Poblacion:
    """Gestiona el conjunto de individuos que participan en el proceso evolutivo"""
    funcion_objetivo: Callable[[int], float]
    individuos: list[Individuo]
    maximo: Optional[float]
    minimo: Optional[float]
    promedio: Optional[float]
    desviacion: Optional[float]
    
    def __init__(self, tamaño: int, funcion_objetivo: Callable[[int], float]) -> None:
        """Inicializa una población de un tamaño determinado con la función objetivo provista"""
        self.funcion_objetivo = funcion_objetivo
        self.individuos = [Individuo(funcion_objetivo) for _ in range(tamaño)]
        self.maximo = None
        self.minimo = None
        self.promedio = None
        self.desviacion = None
        
    def obtener_mejores(self, n: int) -> list[Individuo]:
        """Retorna los n individuos con el mayor valor en la función objetivo"""
        return sorted(self.individuos, key=lambda x: x.valor_funcion_objetivo, reverse=True)[:n]
    
    def pasar_generacion(self, nuevos_individuos: list[Individuo]) -> None: 
        """Reemplaza los individuos de la población actual por una nueva generación"""
        self.individuos = nuevos_individuos
    
    def evaluar(self) -> None:
        """Calcula el fitness, promedio, mínimo, máximo y la desviación estándar de la población"""
        
        valores = [i.valor_funcion_objetivo for i in self.individuos]
        total_valores = sum(valores)
        
        for individuo in self.individuos:
            individuo.calcular_fitness(total_valores)
            
        promedio_fitness = sum(i.fitness for i in self.individuos if i.fitness is not None) / len(self.individuos)
        
        
        self.desviacion = ((sum(((i.fitness - promedio_fitness) ** 2) for i in self.individuos if i.fitness is not None))/len(self.individuos)) ** 0.5
        
        self.maximo = max(valores)
        self.minimo = min(valores)
        self.promedio = sum(valores) / len(valores)