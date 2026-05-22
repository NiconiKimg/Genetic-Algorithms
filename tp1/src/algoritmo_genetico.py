from poblacion import Poblacion
from operadores import Operadores
from metodos import Seleccion
from time import perf_counter
from logger import Logger

class Algoritmo_Genetico:
  
    def __init__(self, poblacion: Poblacion, operadores: Operadores, metodo: Seleccion, ciclos: int, cantidad_elite: int = 0):
      self.poblacion = poblacion
      self.operadores = operadores
      self.seleccion = metodo
      self.ciclos = ciclos
      self.historial = []
      self.tiempo_ejecucion = 0.0
      self.cantidad_elite = cantidad_elite
      self.logger = Logger()
    
    def correr(self, directorio_salida="outputs", nombre_base="corrida"):
      
      tiempo_inicio = perf_counter()
      
      for _ in range(self.ciclos):
        
        self.poblacion.evaluar()

        mejor_ind = self.poblacion.obtener_mejores(1)[0]
        self.logger.agregar_datos(self.poblacion.minimo, self.poblacion.maximo, self.poblacion.promedio, self.poblacion.desviacion, mejor_ind)

        seleccionados = self.seleccion.seleccionar(self.poblacion)
        
        n_poblacion = len(self.poblacion.individuos)
        if isinstance(self.cantidad_elite, float) and 0.0 < self.cantidad_elite <= 1.0:
            elite_real = max(1, round(self.cantidad_elite * n_poblacion))
        else:
            elite_real = int(self.cantidad_elite)
            
        nueva_poblacion = self.operadores.aplicar(seleccionados, elite_real)
        
        self.poblacion.pasar_generacion(nueva_poblacion)

      self.poblacion.evaluar()
      mejor_ind = self.poblacion.obtener_mejores(1)[0]
      self.logger.agregar_datos(self.poblacion.minimo, self.poblacion.maximo, self.poblacion.promedio, self.poblacion.desviacion, mejor_ind)

       
      tiempo_fin = perf_counter()
      self.tiempo_ejecucion = tiempo_fin - tiempo_inicio
    
      self.logger.export_datos(directorio_salida, nombre_base)
      self.logger.export_metadata(directorio_salida, nombre_base, self.tiempo_ejecucion, self.poblacion.maximo)