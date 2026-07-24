import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from funciones import *


def ejercicio_1():
    """Ejercicio 1: mochila con combinación de elementos."""
    tabla = [
        [150, 20],
        [325, 40],
        [600, 50],
        [805, 36],
        [430, 25],
        [1200, 64],
        [770, 54],
        [60, 18],
        [930, 46],
        [353, 28],
    ]
    volumen_maximo = 4200

    espacio = generarEspacioCombinaciones(2, 10)
    espacio_valor = getValorConjunto(espacio, tabla)
    mejor_combinacion = getMejorCombinacion(espacio_valor, volumen_maximo)

    print("Ejercicio 1")
    print(mejor_combinacion)


def ejercicio_2():
    """Ejercicio 2: solución greedy para la mochila."""
    tabla = [
        [150, 20],
        [325, 40],
        [600, 50],
        [805, 36],
        [430, 25],
        [1200, 64],
        [770, 54],
        [60, 18],
        [930, 46],
        [353, 28],
    ]
    volumen_maximo = 4200

    tabla_proporciones = generarProporciones(tabla)
    tabla_proporciones = sorted(tabla_proporciones, key=lambda x: x[1], reverse=True)

    combinacion = getMejorCombinacionGreedy(tabla, tabla_proporciones, volumen_maximo)
    combinacion = getValorConjunto([combinacion], tabla)

    print("Ejercicio 2")
    print(combinacion)


def ejercicio_3():
    """Ejercicio 3: fuerza bruta o heurístico según la opción elegida."""
    tabla = [
        [1800, 72],
        [600, 36],
        [1200, 60],
    ]
    peso_maximo = 3000

    op = int(input("Ingrese el método de búsqueda a usar (1: Fuerza Bruta, 2: Heurístico): "))

    if op == 1:
        espacio = generarEspacioCombinaciones(2, len(tabla))
        combinaciones = getValorConjunto(espacio, tabla)
        mejor_combinacion = getMejorCombinacion(combinaciones, peso_maximo)

        print("Mejor combinación (Fuerza Bruta):", mejor_combinacion)

    elif op == 2:
        tabla_proporciones = generarProporciones(tabla)
        tabla_proporciones = sorted(tabla_proporciones, key=lambda x: x[1], reverse=True)

        combinacion = getMejorCombinacionGreedy(tabla, tabla_proporciones, peso_maximo)
        combinacion = getValorConjunto([combinacion], tabla)

        print("Mejor combinación (Heurístico):", combinacion)

    else:
        print("Opción inválida")


if __name__ == "__main__":
    print("Seleccione un ejercicio:")
    print("1 - Ejercicio 1")
    print("2 - Ejercicio 2")
    print("3 - Ejercicio 3")

    opcion = input("Ingrese el número del ejercicio: ")

    if opcion == "1":
        ejercicio_1()
    elif opcion == "2":
        ejercicio_2()
    elif opcion == "3":
        ejercicio_3()
    else:
        print("Opción inválida")
