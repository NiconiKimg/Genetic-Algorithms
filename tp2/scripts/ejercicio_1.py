import sys
from pathlib import Path

# Agregar directorio tp2 al sys.path para importaciones limpias de src
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.algoritmos import resolver_exhaustivo
from src.datos_mochila import CAPACIDAD_VOLUMEN_EJ1_EJ2, TABLA_VOLUMEN_EJ1_EJ2
from src.logger import Logger
from src.mochila import crear_elementos_desde_tabla


def ejecutar_ejercicio_1() -> None:
    """Ejecuta la Búsqueda Exhaustiva sobre el conjunto de 10 elementos y 4200 cm³"""
    elementos = crear_elementos_desde_tabla(TABLA_VOLUMEN_EJ1_EJ2)
    logger = Logger()

    logger.iniciar_ejecucion(
        algoritmo="exhaustivo",
        n=len(elementos),
        capacidad=CAPACIDAD_VOLUMEN_EJ1_EJ2,
        dimension_capacidad="volumen",
    )

    mejor_solucion, tabla_subconjuntos = resolver_exhaustivo(
        elementos=elementos,
        capacidad=CAPACIDAD_VOLUMEN_EJ1_EJ2,
        dimension="volumen",
    )

    tiempo = logger.finalizar_ejecucion(
        valor_total=mejor_solucion.valor_total,
        volumen_total=mejor_solucion.volumen_total,
        peso_total=mejor_solucion.peso_total,
        etiquetas_elementos=mejor_solucion.etiquetas_elementos(),
        subconjuntos_evaluados=len(tabla_subconjuntos),
    )

    dir_salida = Path(__file__).resolve().parent.parent / "outputs"
    ruta_md = logger.exportar_tabla(dir_salida, "ejercicio_1")

    print("==================================================")
    print("EJERCICIO 1 - Búsqueda Exhaustiva (Tabla en Memoria)")
    print("==================================================")
    print(f"Total de subconjuntos generados en memoria : {len(tabla_subconjuntos)}")
    print(f"Elementos seleccionados en solución óptima  : [{mejor_solucion.etiquetas_elementos()}]")
    print(f"Valor máximo obtenido                       : ${mejor_solucion.valor_total:.2f}")
    print(f"Volumen ocupado                             : {mejor_solucion.volumen_total:.2f} cm³ (Límite: {CAPACIDAD_VOLUMEN_EJ1_EJ2:.2f} cm³)")
    print(f"Tiempo de ejecución                         : {tiempo:.6f} segundos")

    print("\n--- MUESTRA DE LA TABLA CLASIFICADA POR VALOR (TOP 5 SUBCONJUNTOS EN MEMORIA) ---")
    print(f"{'Pos.':<5} | {'Valor ($)':<10} | {'Volumen (cm³)':<14} | {'Factible':<10} | {'Elementos':<25}")
    print("-" * 75)
    for idx, sol in enumerate(tabla_subconjuntos[:5], 1):
        fact_str = "SÍ" if sol.es_factible else "NO (Excede)"
        print(f"{idx:<5} | ${sol.valor_total:<9.2f} | {sol.volumen_total:<14.2f} | {fact_str:<10} | [{sol.etiquetas_elementos()}]")

    print(f"\nTabla de reporte exportada a: {ruta_md}")
    print("==================================================\n")


if __name__ == "__main__":
    ejecutar_ejercicio_1()
