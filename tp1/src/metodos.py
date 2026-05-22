from poblacion import Poblacion
from individuo import Individuo
import random

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

  def __init__(self, k):
    self.k = k

  def seleccionar(self, poblacion: Poblacion) -> list[Individuo]:
    n_poblacion = len(poblacion.individuos)
    if isinstance(self.k, float) and 0.0 < self.k <= 1.0:
      k_real = max(2, round(self.k * n_poblacion))
    else:
      k_real = int(self.k)

    seleccionados = []
    for _ in range(n_poblacion):
      seleccionados.append(self.realizar_torneo(poblacion, k_real))
    return seleccionados

  def realizar_torneo(self, poblacion: Poblacion, k_real: int) -> Individuo:
    competidores = self.tomar_competidores(poblacion.individuos, k_real)
    return max(competidores, key=lambda ind: ind.fitness)

  def tomar_competidores(self, poblacion: list[Individuo], k_real: int) -> list[Individuo]:
    competidores = []
    for _ in range(k_real):
      index = random.randint(0, len(poblacion) - 1)
      competidores.append(poblacion[index])
    return competidores

class Elitismo(Seleccion):

  def __init__(self, k, metodo: Seleccion):
    self.k = k
    self.metodo = metodo
    
  def seleccionar(self, poblacion: Poblacion) -> list[Individuo]:
    n_poblacion = len(poblacion.individuos)
    if isinstance(self.k, float) and 0.0 < self.k <= 1.0:
      k_real = max(1, round(self.k * n_poblacion))
    else:
      k_real = int(self.k)

    elite = sorted(poblacion.individuos, key=lambda ind: ind.fitness, reverse=True)[:k_real]

    resto = [individuo for individuo in poblacion.individuos if individuo not in elite]

    poblacion_temporal = Poblacion(0, poblacion.funcion_objetivo)
    poblacion_temporal.individuos = resto
    
    seleccionados = self.metodo.seleccionar(poblacion_temporal)

    return elite + seleccionados