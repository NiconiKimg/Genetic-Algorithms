from pathlib import Path
from typing import Optional

try:
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
except ImportError:
    pd = None
    sns = None
    plt = None


def _verificar_librerias() -> None:
    """Verifica la presencia de las librerías pandas, seaborn y matplotlib"""
    if pd is None or sns is None or plt is None:
        raise RuntimeError("La generación de gráficos requiere pandas, seaborn y matplotlib.")


def graficar_tiempo_vs_n(ruta_csv: str, ruta_salida: Optional[str] = None) -> str:
    """Genera y guarda el gráfico de tiempo de ejecución en función de n"""
    _verificar_librerias()
    df = pd.read_csv(ruta_csv)
    df = df[df["N"].notna()]
    df["N"] = df["N"].astype(int)

    agrupado = df.groupby(["Algoritmo", "N"])["Tiempo_Segundos"].agg(["mean", "std"]).reset_index()

    directorio_salida = Path(ruta_salida).parent if ruta_salida else Path(ruta_csv).parent / "plots"
    directorio_salida.mkdir(parents=True, exist_ok=True)
    archivo_salida = Path(ruta_salida) if ruta_salida else directorio_salida / "tiempo_vs_n.png"

    plt.figure(figsize=(8, 5))
    sns.lineplot(data=agrupado, x="N", y="mean", hue="Algoritmo", marker="o")
    plt.yscale("log")
    plt.xlabel("Número de elementos (n)", fontsize=10)
    plt.ylabel("Tiempo medio (s) [Escala Log]", fontsize=10)
    plt.title("Tiempo de Ejecución vs. Tamaño del Problema (n)", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=150)
    plt.close()
    return str(archivo_salida)


def graficar_uso_capacidad(ruta_csv: str, ruta_salida: Optional[str] = None) -> str:
    """Genera y guarda el gráfico comparativo del volumen medio utilizado"""
    _verificar_librerias()
    df = pd.read_csv(ruta_csv)
    df = df[df["Volumen_Total"].notna()]
    df["N"] = df["N"].astype(int)

    directorio_salida = Path(ruta_salida).parent if ruta_salida else Path(ruta_csv).parent / "plots"
    directorio_salida.mkdir(parents=True, exist_ok=True)
    archivo_salida = Path(ruta_salida) if ruta_salida else directorio_salida / "uso_capacidad.png"

    agrupado = df.groupby(["Algoritmo", "N"])["Volumen_Total"].mean().reset_index()
    pivote = agrupado.pivot(index="N", columns="Algoritmo", values="Volumen_Total")

    pivote.plot(kind="bar", figsize=(9, 5.5))
    plt.xlabel("Número de elementos (n)", fontsize=10)
    plt.ylabel("Volumen Medio Utilizado (cm³)", fontsize=10)
    plt.title("Uso Medio de Capacidad de la Mochila por Algoritmo", fontsize=12, fontweight="bold")
    plt.grid(True, axis="y", linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=150)
    plt.close()
    return str(archivo_salida)


def graficar_heatmap_elementos(ruta_csv: str, ruta_salida: Optional[str] = None) -> str:
    """Genera y guarda el mapa de calor con la frecuencia de selección de cada elemento"""
    _verificar_librerias()
    df = pd.read_csv(ruta_csv)

    filas = []
    for _, reg in df.iterrows():
        etiquetas = str(reg.get("Elementos_Seleccionados", "")).split(",") if reg.get("Elementos_Seleccionados") else []
        etiquetas = [s.strip() for s in etiquetas if s.strip() and s.strip() != "ninguno"]
        fila = {"Algoritmo": reg["Algoritmo"]}
        for lab in etiquetas:
            try:
                idx = int(lab)
                fila[f"elem_{idx}"] = 1
            except ValueError:
                continue
        filas.append(fila)

    if not filas:
        raise RuntimeError("No se encontraron registros de elementos en el archivo CSV para generar el heatmap.")

    df_elem = pd.DataFrame(filas).fillna(0)
    columnas_elem = sorted([c for c in df_elem.columns if c.startswith("elem_")], key=lambda x: int(x.split("_")[1]))
    agrupado = df_elem.groupby("Algoritmo")[columnas_elem].mean()

    directorio_salida = Path(ruta_salida).parent if ruta_salida else Path(ruta_csv).parent / "plots"
    directorio_salida.mkdir(parents=True, exist_ok=True)
    archivo_salida = Path(ruta_salida) if ruta_salida else directorio_salida / "heatmap_elementos.png"

    plt.figure(figsize=(max(8, len(columnas_elem) * 0.4), 4.5))
    sns.heatmap(agrupado, cmap="viridis", annot=True, fmt=".2f", cbar_kws={"label": "Proporción de Selección"})
    plt.xlabel("Elemento ID", fontsize=10)
    plt.ylabel("Algoritmo", fontsize=10)
    plt.title("Heatmap de Selección de Elementos por Algoritmo", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=150)
    plt.close()
    return str(archivo_salida)
