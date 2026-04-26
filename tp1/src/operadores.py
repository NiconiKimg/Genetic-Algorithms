from random import random, randint
from individuo import Individuo

class Operadores:

    def __init__(self, prob_crossover, prob_mutacion, funcion_objetivo):
        self.prob_crossover = prob_crossover
        self.prob_mutacion = prob_mutacion
        self.funcion_objetivo = funcion_objetivo

    def aplicar(self, poblacion : list[Individuo]) -> list[Individuo]:
        for i in range(0, len(poblacion), 2):
            padre1 = poblacion[i]
            padre2 = poblacion[i + 1]

            hijo1, hijo2 = self.crossover(padre1, padre2)

            self.mutacion(hijo1)
            hijo1.actualizar()
            poblacion[i] = hijo1
            
            self.mutacion(hijo2)
            hijo2.actualizar()
            poblacion[i + 1] = hijo2
            
        return poblacion

    def crossover(self, padre1, padre2):  

        if (random() < self.prob_crossover):
            cantidad_genes = len(padre1.genes)
            punto_corte = randint(1, cantidad_genes - 1)

            genes_hijo1 = padre1.genes[:punto_corte] + padre2.genes[punto_corte:]
            genes_hijo2 = padre2.genes[:punto_corte] + padre1.genes[punto_corte:]
          
        else:
            genes_hijo1 = padre1.genes[:]
            genes_hijo2 = padre2.genes[:]
        
        return Individuo(self.funcion_objetivo, genes_hijo1), Individuo(self.funcion_objetivo, genes_hijo2)

    def mutacion(self, individuo):
        
        for i in range(len(individuo.genes)):
            if (random() < self.prob_mutacion):
                individuo.genes[i] = 1 if individuo.genes[i] == 0 else 0