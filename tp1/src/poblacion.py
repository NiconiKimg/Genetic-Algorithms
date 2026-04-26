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
        
        valores = [i.valor_funcion_objetivo for i in self.individuos]
        total_valores = sum(valores)
        
        for individuo in self.individuos:
            individuo.calcular_fitness(total_valores)
            
        promedio_fitness = sum(i.fitness for i in self.individuos) / len(self.individuos)
        
        
        self.desviacion = ((sum(((i.fitness - promedio_fitness) ** 2) for i in self.individuos))/len(self.individuos)) ** 0.5
        
        self.maximo = max(valores)
        self.minimo = min(valores)
        self.promedio = sum(valores) / len(valores)

