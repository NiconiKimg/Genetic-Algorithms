import random

class Individuo:
    
    def __init__(self, funcion_objetivo, genes=None):
        self.funcion_objetivo = funcion_objetivo
        self.genes = genes if genes is not None else self.generar()
        self.valor_funcion_objetivo = self.evaluar_funcion_objetivo(funcion_objetivo)

    def generar(self):
        return [random.randint(0, 1) for _ in range(30)]

    def decodificar(self):
        binario = ''.join(str(g) for g in self.genes)
        return int(binario, 2)
    
    def evaluar_funcion_objetivo(self, funcion_objetivo):
        x = self.decodificar()
        return funcion_objetivo(x)
    
    def fitness(self, total_funcion_poblacion : float) -> float:
        return self.valor_funcion_objetivo / total_funcion_poblacion