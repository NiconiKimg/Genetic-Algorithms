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
    index = self.buscar_indice_ganador(acumulados, valor_aleatorio)
    return self.ruleta[index][1]
  
  def buscar_indice_ganador(self, acumulados: list[float], valor_aleatorio: float) -> int:
    index = 0
    while index < len(acumulados) and acumulados[index] < valor_aleatorio:
      index += 1
    return min(index, len(acumulados) - 1)
  
class Torneo(Seleccion):

  def __init__(self, k: int):
    self.k = k

  def seleccionar(self, poblacion: Poblacion) -> list[Individuo]:
    seleccionados = []
    for _ in range(len(poblacion.individuos)):
      seleccionados.append(self.realizar_torneo(poblacion))
    return seleccionados

  def realizar_torneo(self, poblacion: Poblacion) -> Individuo:
    competidores = self.tomar_competidores(poblacion.individuos)
    return max(competidores, key=lambda ind: ind.fitness)

  def tomar_competidores(self, poblacion: list[Individuo]) -> list[Individuo]:
    competidores = []
    for _ in range(self.k):
      index = random.randint(0, len(poblacion) - 1)
      competidores.append(poblacion[index])
    return competidores

class Elitismo(Seleccion):

  def __init__(self, k: int, metodo: Seleccion):
    self.k = k
    self.metodo = metodo
    
  def seleccionar(self, poblacion: Poblacion) -> list[Individuo]:
    elite = sorted(poblacion.individuos, key=lambda ind: ind.fitness, reverse=True)[:self.k]

    for e in elite:
      poblacion.individuos.remove(e)

    seleccionados = self.metodo.seleccionar(poblacion)
    
    temp = elite + seleccionados

    return elite + seleccionados