import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from funciones import *

# 1 Columna: Volumen en cm3, 2 Columna: Valor en $.
tabla = [
    [150,20],
    [325,40],
    [600,50],
    [805,36],
    [430,25],
    [1200,64],
    [770,54],
    [60,18],
    [930,46],
    [353,28]
        ]
volumen_maximo=4200

espacio=generarEspacioCombinaciones(2, 10)

# Combinaciones, Sumatoria de Volumen, Sumatoria de Valor
espacio_valor=getValorConjunto(espacio,tabla)

# Obtener la mejor combinacion de elementos sin superar el volumen maximo
mejor_combinacion=getMejorCombinacion(espacio_valor, volumen_maximo)

print(mejor_combinacion)