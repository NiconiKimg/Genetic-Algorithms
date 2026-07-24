import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from funciones import *

# 1 Columna: Peso, 2 Columna: Valor en $.
tabla = [
        [1800,72],
        [600,36],
        [1200,60]
        ]

peso_maximo = 3000

op=int(input("Ingrese el metodo de busqueda a usar (1: Fuerza Bruta, 2: Heuristico): "))


if op == 1:
    
    espacio= generarEspacioCombinaciones(2, len(tabla))

    combinaciones = getValorConjunto(espacio, tabla)

    mejor_combinacion = getMejorCombinacion(combinaciones, peso_maximo)

    print("Mejor combinacion (Fuerza Bruta):", mejor_combinacion)


elif op == 2:
    tabla_proporciones = generarProporciones(tabla)
    tabla_proporciones = sorted(tabla_proporciones, key=lambda x: x[1], reverse=True)

    print(tabla_proporciones)
    combinacion = getMejorCombinacionGreedy(tabla, tabla_proporciones, peso_maximo)

    combinacion = getValorConjunto([combinacion], tabla)

    print("Mejor combinacion (Heuristico):", combinacion)