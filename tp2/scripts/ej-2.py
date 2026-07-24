import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from funciones import *

volumen_maximo = 4200

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


#Generar las proporciones de valor/volumen
tabla_proporciones = generarProporciones(tabla)
tabla_proporciones = sorted(tabla_proporciones, key=lambda x: x[1], reverse=True)

# Arma la mejor combinacion de elementos sin superar el volumen maximo
# usando el algoritmo greedy
combinacion=getMejorCombinacionGreedy(tabla,tabla_proporciones,volumen_maximo)

# Muestra el peso y el valor de la combinacion
combinacion=getValorConjunto([combinacion])
print(combinacion)