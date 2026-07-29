from .mochila import Elemento, Mochila, SolucionMochila, evaluar_solucion


def resolver_exhaustivo(
    elementos: list[Elemento],
    capacidad: float,
    dimension: str = "volumen",
) -> tuple[SolucionMochila, list[SolucionMochila]]:
    """Evalúa los 2^n subconjuntos en memoria, los clasifica por valor decreciente y halla la solución óptima"""
    mochila = Mochila(capacidad_maxima=capacidad, dimension_capacidad=dimension)
    n = len(elementos)
    tabla_subconjuntos: list[SolucionMochila] = []

    # 1. Generar la tabla completa de 2^n subconjuntos en memoria
    for mascara in range(1 << n):
        seleccionados = [elementos[i] for i in range(n) if (mascara >> i) & 1]
        solucion = evaluar_solucion(seleccionados, mochila)
        tabla_subconjuntos.append(solucion)

    # 2. Clasificar los subconjuntos por valor de mayor a menor en memoria
    tabla_subconjuntos.sort(key=lambda s: s.valor_total, reverse=True)

    # 3. Seleccionar la primera solución de la tabla ordenada que sea factible
    mejor_solucion = SolucionMochila([], 0.0, 0.0, 0.0, es_factible=True)
    for solucion in tabla_subconjuntos:
        if solucion.es_factible:
            mejor_solucion = solucion
            break

    return mejor_solucion, tabla_subconjuntos


def resolver_greedy(
    elementos: list[Elemento],
    capacidad: float,
    dimension: str = "volumen",
) -> SolucionMochila:
    """Selecciona elementos ordenados por densidad de valor decreciente respetando la capacidad"""
    mochila = Mochila(capacidad_maxima=capacidad, dimension_capacidad=dimension)
    elementos_ordenados = sorted(
        elementos,
        key=lambda elem: elem.obtener_ratio(dimension),
        reverse=True,
    )

    seleccionados: list[Elemento] = []
    capacidad_usada = 0.0

    for elem in elementos_ordenados:
        cap_elem = elem.obtener_capacidad(dimension)
        if capacidad_usada + cap_elem <= capacidad:
            seleccionados.append(elem)
            capacidad_usada += cap_elem

    return evaluar_solucion(seleccionados, mochila)
