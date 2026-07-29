import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.algoritmos import resolver_greedy
from src.datos_mochila import CAPACIDAD_VOLUMEN_EJ1_EJ2, TABLA_VOLUMEN_EJ1_EJ2
from src.logger import Logger
from src.mochila import crear_elementos_desde_tabla


def ejecutar_ejercicio_2() -> None:
    """Ejecuta el Algoritmo Goloso (Greedy) sobre la mochila de 4200 cm³"""
    elementos = crear_elementos_desde_tabla(TABLA_VOLUMEN_EJ1_EJ2)
    logger = Logger()

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
    tiempo_greedy = logger.finalizar_ejecucion(
        valor_total=solucion_greedy.valor_total,
        volumen_total=solucion_greedy.volumen_total,
        peso_total=solucion_greedy.peso_total,
        etiquetas_elementos=solucion_greedy.etiquetas_elementos(),
        subconjuntos_evaluados=None,
    )

    dir_salida = Path(__file__).resolve().parent.parent / "outputs"
    ruta_csv = logger.exportar_tabla(dir_salida, "ejercicio_2")

    print("==================================================")
    print("EJERCICIO 2 - Algoritmo Goloso (Greedy)")
    print("==================================================")
    print(f"Elementos seleccionados por Greedy : [{solucion_greedy.etiquetas_elementos()}]")
    print(f"Valor obtenido                     : ${solucion_greedy.valor_total:.2f}")
    print(f"Volumen ocupado                    : {solucion_greedy.volumen_total:.2f} cm³ (Límite: {CAPACIDAD_VOLUMEN_EJ1_EJ2:.2f} cm³)")
    print(f"Tiempo de ejecución                : {tiempo_greedy:.6f} segundos")
    print(f"\nTabla de reporte exportada a: {ruta_csv}")
    print("==================================================\n")


if __name__ == "__main__":
    ejecutar_ejercicio_2()
