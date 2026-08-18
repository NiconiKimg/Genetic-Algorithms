import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.graficadores import graficar_heatmap_elementos, graficar_tiempo_vs_n, graficar_uso_capacidad


def generar_todas_las_graficas(ruta_csv_especifica: str | None = None) -> None:
    """Genera los tres gráficos PNG desde un CSV de benchmarks en outputs/plots/"""
    dir_outputs = Path(__file__).resolve().parent.parent / "outputs"
    ruta_csv = str(
        Path(ruta_csv_especifica) if ruta_csv_especifica else dir_outputs / "benchmarks.csv"
    )

    graficar_tiempo_vs_n(ruta_csv)
    graficar_uso_capacidad(ruta_csv)
    graficar_heatmap_elementos(ruta_csv)


if __name__ == "__main__":
    generar_todas_las_graficas()
