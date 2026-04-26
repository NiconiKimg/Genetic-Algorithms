from individuo import Individuo
from poblacion import Poblacion
from operadores import Operadores
from metodo_ruleta import Ruleta


funcion_objetivo = lambda x: (x/((2 ** 30) - 1)) ** 2

poblacion = Poblacion(20, funcion_objetivo)
operadores = Operadores(prob_crossover=0.7, prob_mutacion=0.01, funcion_objetivo=funcion_objetivo)
ruleta = Ruleta()
cantidad_generaciones = 100000

# Aca el for para las generaciones
for generacion in range(cantidad_generaciones):
    poblacion.evaluar()

    ruleta.armar_ruleta(poblacion)

    nueva_poblacion = []
    for i in range(len(poblacion.individuos)):
        seleccionado = ruleta.girar_ruleta()
        nueva_poblacion.append(seleccionado)

    for i in range(0, len(nueva_poblacion), 2):
        padre1 = nueva_poblacion[i]
        padre2 = nueva_poblacion[i + 1]
        
        hijo1, hijo2 = operadores.crossover(padre1, padre2)
        
        operadores.mutacion(hijo1)
        operadores.mutacion(hijo2)
        
        nueva_poblacion[i] = hijo1
        nueva_poblacion[i + 1] = hijo2
        
    poblacion.pasar_generacion(nueva_poblacion)

mejores = poblacion.obtener_mejores(5)
print("Mejores individuos:")
for i, individuo in enumerate(mejores, 1):
    print(f"{i}. Valor función objetivo: {individuo.valor_funcion_objetivo}, Genes: {individuo.genes}")
    
