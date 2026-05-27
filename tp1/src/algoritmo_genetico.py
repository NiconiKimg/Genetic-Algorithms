from pathlib import Path
from typing import Any
from poblacion import Poblacion
from operadores import Operadores
from metodos import Seleccion
from time import perf_counter
from logger import Logger

class Algoritmo_Genetico:
    """Orquesta la ejecución del algoritmo genético aplicando operadores y selección"""
    poblacion: Poblacion
    operadores: Operadores
    seleccion: Seleccion
    ciclos: int
    historial: list[Any]
    tiempo_ejecucion: float
    cantidad_elite: int | float
    logger: Logger
  
    def __init__(self, poblacion: Poblacion, operadores: Operadores, metodo: Seleccion, ciclos: int, cantidad_elite: int | float = 0) -> None:
      """Inicializa los parámetros, población, operadores y logger del algoritmo"""
      self.poblacion = poblacion
      self.operadores = operadores
      self.seleccion = metodo
      self.ciclos = ciclos
      self.historial = []
      self.tiempo_ejecucion = 0.0
      self.cantidad_elite = cantidad_elite
      self.logger = Logger()
    
    def correr(self, directorio_salida: str | Path = "outputs", nombre_base: str = "corrida") -> None:
      """Ejecuta el ciclo evolutivo completo y exporta los resultados obtenidos"""
      
      tiempo_inicio = perf_counter()
      
      self.poblacion.evaluar()
      mejor_ind = self.poblacion.obtener_mejores(1)[0]
      self.logger.agregar_datos(
          self.poblacion.minimo if self.poblacion.minimo is not None else 0.0,
          self.poblacion.maximo if self.poblacion.maximo is not None else 0.0,
          self.poblacion.promedio if self.poblacion.promedio is not None else 0.0,
          self.poblacion.desviacion if self.poblacion.desviacion is not None else 0.0,
          mejor_ind
      )
      
      for _ in range(self.ciclos - 1):
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
        self.logger.agregar_datos(
            self.poblacion.minimo if self.poblacion.minimo is not None else 0.0,
            self.poblacion.maximo if self.poblacion.maximo is not None else 0.0,
            self.poblacion.promedio if self.poblacion.promedio is not None else 0.0,
            self.poblacion.desviacion if self.poblacion.desviacion is not None else 0.0,
            mejor_ind
        )
       
      tiempo_fin = perf_counter()
      self.tiempo_ejecucion = tiempo_fin - tiempo_inicio
    
      self.logger.export_datos(str(directorio_salida), nombre_base, self.poblacion)
      self.logger.export_metadata(str(directorio_salida), nombre_base, self.tiempo_ejecucion, self.poblacion.maximo if self.poblacion.maximo is not None else 0.0)