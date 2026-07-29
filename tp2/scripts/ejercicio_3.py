import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.algoritmos import resolver_exhaustivo, resolver_greedy
from src.datos_mochila import CAPACIDAD_PESO_EJ3, PESOS_EJ3, VALORES_EJ3
from src.logger import Logger
from src.mochila import crear_elementos_por_peso


def ejecutar_ejercicio_3() -> None:
    """Ejecuta ambos algoritmos sobre el problema de peso (3000 grs) y analiza la suboptimidad del Greedy"""
    elementos = crear_elementos_por_peso(PESOS_EJ3, VALORES_EJ3)
    logger = Logger()

    # 1. Búsqueda Exhaustiva
    logger.iniciar_ejecucion(
        algoritmo="exhaustivo",
        n=len(elementos),
        capacidad=CAPACIDAD_PESO_EJ3,
        dimension_capacidad="peso",
    )
    solucion_exhaustiva, todas = resolver_exhaustivo(
        elementos=elementos,
        capacidad=CAPACIDAD_PESO_EJ3,
        dimension="peso",
    )
    tiempo_exhaustivo = logger.finalizar_ejecucion(
        valor_total=solucion_exhaustiva.valor_total,
        volumen_total=solucion_exhaustiva.volumen_total,
        peso_total=solucion_exhaustiva.peso_total,
        etiquetas_elementos=solucion_exhaustiva.etiquetas_elementos(),
        subconjuntos_evaluados=len(todas),
    )

    # 2. Algoritmo Greedy
    logger.iniciar_ejecucion(
        algoritmo="greedy",
        n=len(elementos),
        capacidad=CAPACIDAD_PESO_EJ3,
        dimension_capacidad="peso",
    )
    solucion_greedy = resolver_greedy(
        elementos=elementos,
        capacidad=CAPACIDAD_PESO_EJ3,
        dimension="peso",
    )
    tiempo_greedy = logger.finalizar_ejecucion(
        valor_total=solucion_greedy.valor_total,
        volumen_total=solucion_greedy.volumen_total,
        peso_total=solucion_greedy.peso_total,
        etiquetas_elementos=solucion_greedy.etiquetas_elementos(),
        subconjuntos_evaluados=None,
    )

    dir_salida = Path(__file__).resolve().parent.parent / "outputs"
    ruta_md = logger.exportar_tabla(dir_salida, "ejercicio_3")

    es_optimo = solucion_greedy.valor_total == solucion_exhaustiva.valor_total

    print("==================================================")
    print("EJERCICIO 3 - Mochila con Pesos (Límite: 3000 grs)")
    print("==================================================")
    print("Solución Exhaustiva (Óptima):")
    print(f"  - Elementos seleccionados : [{solucion_exhaustiva.etiquetas_elementos()}]")
    print(f"  - Valor total             : ${solucion_exhaustiva.valor_total:.2f}")
    print(f"  - Peso total              : {solucion_exhaustiva.peso_total:.2f} grs")
    print(f"  - Tiempo                  : {tiempo_exhaustivo:.6f} segundos")
    print("--------------------------------------------------")
    print("Solución Golosa (Greedy):")
    print(f"  - Elementos seleccionados : [{solucion_greedy.etiquetas_elementos()}]")
    print(f"  - Valor total             : ${solucion_greedy.valor_total:.2f}")
    print(f"  - Peso total              : {solucion_greedy.peso_total:.2f} grs")
    print(f"  - Tiempo                  : {tiempo_greedy:.6f} segundos")
    print("--------------------------------------------------")
    print(f"¿Greedy alcanza el óptimo?: {'SÍ' if es_optimo else 'NO'}")
    print("\nANÁLISIS Y CONCLUSIONES:")
    if es_optimo:
        print("  El algoritmo Greedy encontró la solución óptima para este caso.")
    else:
        diferencia = solucion_exhaustiva.valor_total - solucion_greedy.valor_total
        porcentaje = (solucion_greedy.valor_total / solucion_exhaustiva.valor_total) * 100
        print(f"  El algoritmo Greedy NO alcanzó la solución óptima.")
        print(f"  - Pérdida de valor        : ${diferencia:.2f} ({100 - porcentaje:.2f}% de pérdida)")
        print(f"  - Eficiencia del Greedy   : {porcentaje:.2f}% respecto al óptimo global.")
        print("  - Explicación técnica     : El Greedy ordena por densidad ($/grs) e incluye primero el Elemento 2")
        print("    (600grs, $36 -> ratio 0.06 $/gr) y luego el Elemento 3 (1200grs, $60 -> ratio 0.05 $/gr), dejando")
        print("    solo 1200grs disponibles y sin poder incluir el Elemento 1 (1800grs, $72 -> ratio 0.04 $/gr).")
        print("    El Óptimo Exhaustivo combina los Elementos 1 y 3 utilizando exactamente los 3000grs para alcanzar $132.")

    print(f"\nTabla de reporte exportada a: {ruta_md}")
    print("==================================================\n")


if __name__ == "__main__":
    ejecutar_ejercicio_3()
