from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"

if str(BASE_DIR) not in sys.path:
	sys.path.insert(0, str(BASE_DIR))

if str(SRC_DIR) not in sys.path:
	sys.path.insert(0, str(SRC_DIR))

from src.individuo import Individuo
from src.poblacion import Poblacion
from src.metodos import Elitismo, Torneo
from src.operadores import Operadores
from src.algoritmo_genetico import Algoritmo_Genetico

#CONSTANTES GLOBALES
PROBABILIDAD_CROSSOVER = 0.75
PROBABILIDAD_MUTACION = 0.05
FUNCION_OBJETIVO = lambda x: (x / (2**30 - 1)) ** 2
TAMAÑO_POBLACION_A = 10
COMPETIDORES_TORNEO = 5
TAMAÑO_ELITE = 2
DIR_SALIDA = BASE_DIR / "outputs" / "elitismo_torneo"

#INSTANCIAS GLOBALES
torneo = Torneo(COMPETIDORES_TORNEO)
elitismo = Elitismo(TAMAÑO_ELITE, torneo)
operadores = Operadores(PROBABILIDAD_CROSSOVER, PROBABILIDAD_MUTACION, FUNCION_OBJETIVO)

CICLOS = 100


#INSTANCIAS
poblacion_a = Poblacion(TAMAÑO_POBLACION_A, FUNCION_OBJETIVO)
algoritmo_genetico_a = Algoritmo_Genetico(poblacion_a, operadores, elitismo, CICLOS, TAMAÑO_ELITE)

#EJEMPLO DE USO -> Luego se reemplazará por el logger y las clases que impriman
algoritmo_genetico_a.correr(directorio_salida=DIR_SALIDA, nombre_base="elitismo_torneo_100_ciclos")

#MUESTRA DE RESULTADOS
print("RESULTADOS")
mejor = poblacion_a.obtener_mejores(1)[0]
print(mejor.genes)
print(poblacion_a.maximo)
print(poblacion_a.minimo)
print(poblacion_a.promedio)
print(poblacion_a.desviacion)
print(algoritmo_genetico_a.tiempo_ejecucion)