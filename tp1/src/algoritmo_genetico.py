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
    
    def correr(self):
      
      tiempo_inicio = perf_counter()
      
      for _ in range(self.ciclos):
        
        self.poblacion.evaluar()

        self.logger.agregar_datos(self.poblacion.minimo, self.poblacion.maximo, self.poblacion.promedio, self.poblacion.desviacion)

        seleccionados = self.seleccion.seleccionar(self.poblacion)
        
        nueva_poblacion = self.operadores.aplicar(seleccionados, self.cantidad_elite)
        
        self.poblacion.pasar_generacion(nueva_poblacion)

        
      tiempo_fin = perf_counter()
      self.tiempo_ejecucion = tiempo_fin - tiempo_inicio
    
      # aca ya exportamos los datos a csv y graficos u otros formatos
      self.logger.export_datos("corrida_algoritmo_genetico.csv")