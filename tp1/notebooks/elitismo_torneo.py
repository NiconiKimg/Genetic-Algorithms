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

#INSTANCIAS GLOBALES
torneo = Torneo(COMPETIDORES_TORNEO)
elitismo = Elitismo(TAMAÑO_ELITE, torneo)
operadores = Operadores(PROBABILIDAD_CROSSOVER, PROBABILIDAD_MUTACION, FUNCION_OBJETIVO)

#CONSTANTES ETAPA 1
CICLOS_A = 20

#CONSTANTES ETAPA 2
CICLOS_B = 100

#CONSTANTES ETAPA 3
CICLOS_C = 200


#INSTANCIAS ETAPA 1
poblacion_a = Poblacion(TAMAÑO_POBLACION_A, FUNCION_OBJETIVO)
algoritmo_genetico_a = Algoritmo_Genetico(poblacion_a, operadores, elitismo, CICLOS_A, TAMAÑO_ELITE)

#INSTANCIAS ETAPA 2
poblacion_b = Poblacion(TAMAÑO_POBLACION_A, FUNCION_OBJETIVO)
algoritmo_genetico_b = Algoritmo_Genetico(poblacion_b, operadores, elitismo, CICLOS_B, TAMAÑO_ELITE)

#INSTANCIAS ETAPA 3
poblacion_c = Poblacion(TAMAÑO_POBLACION_A, FUNCION_OBJETIVO)
algoritmo_genetico_c = Algoritmo_Genetico(poblacion_c, operadores, elitismo, CICLOS_C, TAMAÑO_ELITE)

#EJEMPLO DE USO -> Luego se reemplazará por el logger y las clases que impriman
algoritmo_genetico_a.correr()
algoritmo_genetico_b.correr()
algoritmo_genetico_c.correr()

#MUESTRA DE RESULTADOS
print("ETAPA A")
mejor = poblacion_a.obtener_mejores(1)[0]
print(mejor.genes)
print(poblacion_a.maximo)
print(poblacion_a.minimo)
print(poblacion_a.promedio)
print(poblacion_a.desviacion)
print(algoritmo_genetico_a.tiempo_ejecucion)

print("ETAPA B")
mejor = poblacion_b.obtener_mejores(1)[0]
print(mejor.genes)
print(poblacion_b.maximo)
print(poblacion_b.minimo)
print(poblacion_b.promedio)
print(poblacion_b.desviacion)
print(algoritmo_genetico_b.tiempo_ejecucion)

print("ETAPA C")
mejor = poblacion_c.obtener_mejores(1)[0]
print(mejor.genes)
print(poblacion_c.maximo)
print(poblacion_c.minimo)
print(poblacion_c.promedio)
print(poblacion_c.desviacion)
print(algoritmo_genetico_c.tiempo_ejecucion)