from poblacion import Poblacion
from individuo import Individuo
import random

class Ruleta():
  
  def __init__(self):
    
    self.ruleta : list[Individuo] = []
    self.total_fitness : float = 0.0

  def calcular_frecuencia(self, individuo : Individuo, total_valores : float) -> float:
      return individuo.fitness(total_valores) / self.total_fitness
    
  def armar_ruleta(self, poblacion: Poblacion):
    
    total_valores = sum(i.valor_funcion_objetivo for i in poblacion.individuos)
    
    self.total_fitness = sum(ind.fitness(total_valores) for ind in poblacion.individuos)
    
    for individuo in poblacion.individuos:
      frecuencia = self.calcular_frecuencia(individuo, total_valores)
      cantidad = int(frecuencia * 100) 
      self.ruleta.extend([individuo] * cantidad)
    
  def girar_ruleta(self) -> Individuo:
    indice = random.randint(0, len(self.ruleta) - 1)
    return self.ruleta[indice]