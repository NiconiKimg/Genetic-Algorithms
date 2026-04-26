from poblacion import Poblacion
from individuo import Individuo
import random
import bisect

class Seleccion:
  def seleccionar(self, poblacion: Poblacion) -> list[Individuo]:
    raise NotImplementedError

class Ruleta(Seleccion):
  
  def __init__(self):
    
    self.ruleta : list[Individuo] = []

  def seleccionar(self, poblacion: Poblacion) -> list[Individuo]:
    self.armar_ruleta(poblacion)
    seleccionados = []
    for _ in range(len(poblacion.individuos)):
      seleccionados.append(self.girar_ruleta())
    return seleccionados
    
  def armar_ruleta(self, poblacion: Poblacion):
    self.ruleta = []
    acumulado = 0.0
    
    for individuo in poblacion.individuos:
      acumulado += individuo.fitness
      self.ruleta.append((acumulado,individuo))
  
    
  def girar_ruleta(self) -> Individuo:
    valor_aleatorio = random.random()
    acumulados = [x[0] for x in self.ruleta]
    index = bisect.bisect_left(acumulados, valor_aleatorio)
    index = min(index, len(self.ruleta) - 1)
    return self.ruleta[index][1]
  
  