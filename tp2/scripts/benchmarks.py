import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.algoritmos import resolver_exhaustivo, resolver_greedy
from src.datos_mochila import CAPACIDAD_VOLUMEN_EJ1_EJ2, TABLA_VOLUMEN_EJ1_EJ2
from src.logger import Logger
from src.mochila import crear_elementos_desde_tabla


def ejecutar_benchmarks_e1_e2(
    logger: Logger,
    valores_n: list[int],
    repeticiones: int,
) -> None:
    """Ejecuta corridas comparativas variando el tamaño del problema n y repeticiones"""
    tabla_base = TABLA_VOLUMEN_EJ1_EJ2
    max_elementos = len(tabla_base)

    for n in valores_n:
        if n <= 0:
            continue
        n_usar = min(n, max_elementos)

        for _ in range(repeticiones):
            elementos = crear_elementos_desde_tabla(tabla_base[:n_usar])

            # 1. Búsqueda Exhaustiva
            logger.iniciar_ejecucion(
                algoritmo="exhaustivo",
                n=len(elementos),
                capacidad=CAPACIDAD_VOLUMEN_EJ1_EJ2,
                dimension_capacidad="volumen",
            )
            optimo, todas = resolver_exhaustivo(
                elementos=elementos,
                capacidad=CAPACIDAD_VOLUMEN_EJ1_EJ2,
                dimension="volumen",
            )
            logger.finalizar_ejecucion(
                valor_total=optimo.valor_total,
                volumen_total=optimo.volumen_total,
                peso_total=optimo.peso_total,
                etiquetas_elementos=optimo.etiquetas_elementos(),
                subconjuntos_evaluados=len(todas),
            )

            # 2. Algoritmo Greedy
            logger.iniciar_ejecucion(
                algoritmo="greedy",
                n=len(elementos),
                capacidad=CAPACIDAD_VOLUMEN_EJ1_EJ2,
                dimension_capacidad="volumen",
            )
            solucion_greedy = resolver_greedy(
                elementos=elementos,
                capacidad=CAPACIDAD_VOLUMEN_EJ1_EJ2,
                dimension="volumen",
            )
            logger.finalizar_ejecucion(
                valor_total=solucion_greedy.valor_total,
                volumen_total=solucion_greedy.volumen_total,
                peso_total=solucion_greedy.peso_total,
                etiquetas_elementos=solucion_greedy.etiquetas_elementos(),
                subconjuntos_evaluados=None,
            )


def ejecutar_benchmarks() -> str:
    """Ejecuta el conjunto de benchmarks automáticos y exporta la tabla de métricas"""
    logger = Logger()
    ejecutar_benchmarks_e1_e2(logger, valores_n=[4, 6, 8, 10], repeticiones=5)
    dir_salida = Path(__file__).resolve().parent.parent / "outputs"
    return logger.exportar_tabla(dir_salida, "benchmarks")


if __name__ == "__main__":
    ejecutar_benchmarks()
