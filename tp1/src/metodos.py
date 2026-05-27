from poblacion import Poblacion
from individuo import Individuo
import random

class Seleccion:
  """Interfaz base para definir métodos de selección en el algoritmo"""
  def seleccionar(self, poblacion: Poblacion) -> list[Individuo]:
    """Selecciona individuos aptos de la población y los retorna en una lista"""
    raise NotImplementedError

class Ruleta(Seleccion):
  """Método de selección proporcional al fitness de cada individuo"""
  ruleta: list[tuple[float, Individuo]]
  
  def __init__(self) -> None:
    """Inicializa la ruleta para selección proporcional"""
    self.ruleta = []

  def seleccionar(self, poblacion: Poblacion) -> list[Individuo]:
    """Selecciona individuos girando la ruleta proporcional"""
    self.armar_ruleta(poblacion)
    seleccionados = []
    for _ in range(len(poblacion.individuos)):
      seleccionados.append(self.girar_ruleta())
    return seleccionados
    
  def armar_ruleta(self, poblacion: Poblacion) -> None:
    """Construye la ruleta de probabilidades acumuladas a partir del fitness"""
    self.ruleta = []
    acumulado = 0.0
    
    for individuo in poblacion.individuos:
      if individuo.fitness is not None:
        acumulado += individuo.fitness
      self.ruleta.append((acumulado,individuo))
    
  def girar_ruleta(self) -> Individuo:
    """Obtiene un individuo al azar usando la distribución de la ruleta"""
    valor_aleatorio = random.random()
    acumulados = [x[0] for x in self.ruleta]
    index = self.buscar_indice_ganador(acumulados, valor_aleatorio)
    return self.ruleta[index][1]
  
  def buscar_indice_ganador(self, acumulados: list[float], valor_aleatorio: float) -> int:
    """Busca la posición del individuo ganador usando búsqueda secuencial"""
    index = 0
    while index < len(acumulados) and acumulados[index] < valor_aleatorio:
      index += 1
    return min(index, len(acumulados) - 1)
  
class Torneo(Seleccion):
  """Método de selección basado en torneos aleatorios de tamaño K"""
  k: int | float

  def __init__(self, k: int | float) -> None:
    """Inicializa el tamaño del torneo K"""
    self.k = k

  def seleccionar(self, poblacion: Poblacion) -> list[Individuo]:
    """Realiza múltiples torneos y selecciona a los ganadores"""
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
    """Lleva a cabo un torneo entre competidores aleatorios y retorna al mejor"""
    competidores = self.tomar_competidores(poblacion.individuos, k_real)
    return max(competidores, key=lambda ind: ind.fitness if ind.fitness is not None else -1.0)

  def tomar_competidores(self, poblacion: list[Individuo], k_real: int) -> list[Individuo]:
    """Selecciona una muestra aleatoria de competidores de la población"""
    competidores = []
    for _ in range(k_real):
      index = random.randint(0, len(poblacion) - 1)
      competidores.append(poblacion[index])
    return competidores

class Elitismo(Seleccion):
  """Método de selección que preserva a los mejores individuos intactos"""
  k: int | float
  metodo: Seleccion

  def __init__(self, k: int | float, metodo: Seleccion) -> None:
    """Inicializa la cantidad de élite K y el método de selección secundario"""
    self.k = k
    self.metodo = metodo
    
  def seleccionar(self, poblacion: Poblacion) -> list[Individuo]:
    """Combina los mejores individuos con el resultado de la selección del resto"""
    n_poblacion = len(poblacion.individuos)
    if isinstance(self.k, float) and 0.0 < self.k <= 1.0:
      k_real = max(1, round(self.k * n_poblacion))
    else:
      k_real = int(self.k)

    elite = sorted(poblacion.individuos, key=lambda ind: ind.fitness if ind.fitness is not None else -1.0, reverse=True)[:k_real]

    resto = [individuo for individuo in poblacion.individuos if individuo not in elite]

    poblacion_temporal = Poblacion(0, poblacion.funcion_objetivo)
    poblacion_temporal.individuos = resto
    
    seleccionados = self.metodo.seleccionar(poblacion_temporal)

    return elite + seleccionados