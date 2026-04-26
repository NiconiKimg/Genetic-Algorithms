from individuo import Individuo

class Poblacion:
    
    def __init__(self, tamaño, funcion_objetivo):
        self.funcion_objetivo = funcion_objetivo
        self.individuos = [Individuo(funcion_objetivo) for _ in range(tamaño)]
        self.maximo = None
        self.minimo = None
        self.promedio = None
        self.desviacion = None
        
    def obtener_mejores(self, n):
        return sorted(self.individuos, key=lambda x: x.valor_funcion_objetivo, reverse=True)[:n]
    
    def pasar_generacion(self, nuevos_individuos): 
        self.individuos = nuevos_individuos
    
    def evaluar(self):
        """Evalúa la población y actualiza las estadísticas."""
        self.maximo = max(i.valor_funcion_objetivo for i in self.individuos) # del valor de la función objetivo
        self.minimo = min(i.valor_funcion_objetivo for i in self.individuos) # del valor de la función objetivo
        self.promedio = sum(i.valor_funcion_objetivo for i in self.individuos) / len(self.individuos) # del valor de la función objetivo
        
        total_valores = sum(i.valor_funcion_objetivo for i in self.individuos)
        
        promedio_fitness = sum(i.fitness(total_valores) for i in self.individuos) / len(self.individuos)
        
        self.desviacion = ((sum(((i.fitness(total_valores) - promedio_fitness) ** 2) for i in self.individuos))/len(self.individuos)) ** 0.5

        self.desviacion = ((sum(((i.valor_funcion_objetivo/total_valores) - self.promedio) ** 2 for i in self.individuos))/len(self.individuos)) ** 0.5