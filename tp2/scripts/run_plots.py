import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.graficadores import graficar_heatmap_elementos, graficar_tiempo_vs_n, graficar_uso_capacidad


def generar_todas_las_graficas(ruta_csv_especifica: str | None = None) -> None:
    """Lee un archivo de datos o convierte la tabla para generar los gráficos PNG en outputs/plots/"""
    dir_outputs = Path(__file__).resolve().parent.parent / "outputs"

    # Si se requiere gráfico desde datos, busca archivos .md o .csv
    ruta_csv = Path(ruta_csv_especifica) if ruta_csv_especifica else dir_outputs / "benchmarks_stats.csv"

    if not ruta_csv.exists():
        candidatos = list(dir_outputs.glob("*.csv"))
        if candidatos:
            ruta_csv = candidatos[0]

    if not ruta_csv.exists():
        print(f"Nota: Para generar gráficos PNG con seaborn/matplotlib, asegúrese de contar con datos de corridas.")
        return

    print(f"Generando gráficos a partir de: {ruta_csv}")

    try:
        p1 = graficar_tiempo_vs_n(str(ruta_csv))
        print(f"  [OK] Gráfico de tiempo guardado en: {p1}")
    except Exception as e:
        print(f"  [ERR] Fallo al generar gráfico de tiempo: {e}")

    try:
        p2 = graficar_uso_capacidad(str(ruta_csv))
        print(f"  [OK] Gráfico de capacidad guardado en: {p2}")
    except Exception as e:
        print(f"  [ERR] Fallo al generar gráfico de capacidad: {e}")

    try:
        p3 = graficar_heatmap_elementos(str(ruta_csv))
        print(f"  [OK] Heatmap de elementos guardado en: {p3}")
    except Exception as e:
        print(f"  [ERR] Fallo al generar heatmap: {e}")


if __name__ == "__main__":
    generar_todas_las_graficas()
