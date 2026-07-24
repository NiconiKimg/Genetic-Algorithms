def generarEspacioCombinaciones(baseEelementos:int,numElementos:int)->list:
    """
    Genera el espacio de combinaciones para el problema de la mochila.
    
    :param baseEelementos: Número de elementos en la base(en este caso base 2).
    :param numElementos: Número de elementos a combinar
    """
    espacio = []
    for i in range(baseEelementos ** numElementos):
        combinacion = []
        for j in range(numElementos):
            combinacion.append((i // (baseEelementos ** j)) % baseEelementos)
        espacio.append(combinacion)

    
    return espacio


def getValorConjunto(combinaciones:list,tabla:list)->list:
    """
    Retorna un array donde esta la combinacion, su valor y su peso.

    :param combinacion: Combinación de elementos.
    """
    
    tabla_combinaciones = []

    for combinacion in combinaciones:
        volumen = 0
        valor = 0
        for i in range(len(combinacion)):
            if combinacion[i] == 1:
                volumen += tabla[i][0]
                valor += tabla[i][1]
        tabla_combinaciones.append([combinacion, volumen, valor])

    
    tabla_combinaciones.sort(key=lambda x: x[2], reverse=True)  # Ordenar por valor descendente
    
    return tabla_combinaciones


def getMejorCombinacion(combinaciones:list,volumen_max:int)->list:
    """
    Retorna la mejor combinacion de elementos, es decir, la que tiene el mayor valor sin superar el volumen maximo.

    :param combinaciones: Combinaciones de elementos.
    """

    valor_maximo = 0
    mejor_combinacion = None

    for i,combinacion in enumerate(combinaciones):
        if combinacion[1] <= volumen_max:
            if combinacion[2] > valor_maximo:
                valor_maximo = combinacion[2]
                mejor_combinacion=i
    
    return combinaciones[mejor_combinacion]
                

#Funciones para algoritmo de greedy

def generarProporciones(tabla:list)->list:
    """
    Genera las proporciones de valor por volumen para cada elemento en la tabla.

    :param tabla: Tabla de elementos con volumen y valor.
    """
    proporciones = []
    for i in range(len(tabla)):
        if tabla[i][0] != 0:  # Evitar división por cero
            proporcion = tabla[i][1] / tabla[i][0]
            proporciones.append([i, proporcion])
    
    return proporciones

def getMejorCombinacionGreedy(tabla:list,tabla_proporciones:list, volumen_max:int)->list:
    """
    Retorna la mejor combinacion de elementos utilizando el algoritmo greedy, es decir, la que tiene el mayor valor sin superar el volumen maximo.

    :param tabla: Tabla de elementos con volumen y valor.
    :param volumen_max: Volumen máximo permitido.
    :param tabla_proporciones: Tabla de proporciones de valor por volumen.
    """

    mejor_combinacion = [0] * len(tabla)  # Inicializar con ceros
    volumen_actual = 0

    for i in range(len(tabla_proporciones)):
        indice = tabla_proporciones[i][0]
        if volumen_actual + tabla[indice][0] <= volumen_max:
            mejor_combinacion[indice] = 1  # Marcar el elemento como incluido
            volumen_actual += tabla[indice][0]

    return mejor_combinacion