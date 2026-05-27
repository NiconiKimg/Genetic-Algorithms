from random import random, randint
from typing import Callable
from individuo import Individuo

class Operadores:
    """Aplica los operadores genéticos de cruzamiento y mutación sobre la población"""
    prob_crossover: float
    prob_mutacion: float
    funcion_objetivo: Callable[[int], float]

    def __init__(self, prob_crossover: float, prob_mutacion: float, funcion_objetivo: Callable[[int], float]) -> None:
        """Inicializa las probabilidades de cruzamiento, mutación y la función objetivo"""
        self.prob_crossover = prob_crossover
        self.prob_mutacion = prob_mutacion
        self.funcion_objetivo = funcion_objetivo

    def aplicar(self, poblacion : list[Individuo], cantidad_elite : int = 0) -> list[Individuo]:
        """Genera la siguiente generación cruzando y mutando individuos seleccionados"""

        n = len(poblacion)
        i = cantidad_elite

        while i < n:

            if i + 1 < n: 
                padre1 = poblacion[i]
                padre2 = poblacion[i + 1]

                hijo1, hijo2 = self.crossover(padre1, padre2)

                self.mutacion(hijo1)
                hijo1.actualizar()
                poblacion[i] = hijo1

                self.mutacion(hijo2)
                hijo2.actualizar()
                poblacion[i + 1] = hijo2

                i += 2
            else:
                ultimo = poblacion[i]
                self.mutacion(ultimo)
                ultimo.actualizar()
                poblacion[i] = ultimo
                i += 1

        return poblacion

    def crossover(self, padre1: Individuo, padre2: Individuo) -> tuple[Individuo, Individuo]:
        """Cruza dos padres en un punto aleatorio según la probabilidad dada"""

        if (random() < self.prob_crossover):
            cantidad_genes = len(padre1.genes)
            punto_corte = randint(1, cantidad_genes - 1)

            genes_hijo1 = padre1.genes[:punto_corte] + padre2.genes[punto_corte:]
            genes_hijo2 = padre2.genes[:punto_corte] + padre1.genes[punto_corte:]

        else:
            genes_hijo1 = padre1.genes[:]
            genes_hijo2 = padre2.genes[:]

        return Individuo(self.funcion_objetivo, genes_hijo1), Individuo(self.funcion_objetivo, genes_hijo2)

    # Mutación Puntual Única (Original)
    def mutacion(self, individuo: Individuo) -> None:
        """Altera aleatoriamente un gen en el cromosoma según la probabilidad dada"""
        if (random() < self.prob_mutacion):
            indice = randint(0, len(individuo.genes) - 1)
            individuo.genes[indice] = 1 if individuo.genes[indice] == 0 else 0

    # Mutación Bit a Bit
    # def mutacion(self, individuo: Individuo) -> None:
    #     """Altera aleatoriamente cada gen en el cromosoma según la probabilidad dada"""
    #     for i in range(len(individuo.genes)):
    #         if (random() < self.prob_mutacion):
    #             individuo.genes[i] = 1 if individuo.genes[i] == 0 else 0

    # Mutación por Inversión
    # def mutacion(self, individuo: Individuo) -> None:
    #     """Invierte una sección aleatoria del cromosoma según la probabilidad dada"""
    #     if (random() < self.prob_mutacion):
    #         n = len(individuo.genes)
    #         idx1 = randint(0, n - 2)
    #         idx2 = randint(idx1 + 1, n - 1)
    #         individuo.genes[idx1:idx2+1] = list(reversed(individuo.genes[idx1:idx2+1]))