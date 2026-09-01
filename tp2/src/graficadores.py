from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def graficar_tiempo_vs_n(ruta_csv: str, ruta_salida: str | None = None) -> str:
    """Genera y guarda el gráfico de tiempo de ejecución en función de n"""
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


def graficar_uso_capacidad(ruta_csv: str, ruta_salida: str | None = None) -> str:
    """Genera y guarda el gráfico comparativo del volumen medio utilizado"""
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


def _generar_heatmap_elementos_base(df: pd.DataFrame, *, por_n: bool, ruta_salida: str | Path | None = None, nombre_archivo: str) -> str:
    """Genera el heatmap a partir de un DataFrame de elementos seleccionados."""
    filas = []
    for _, reg in df.iterrows():
        etiquetas = str(reg.get("Elementos_Seleccionados", "")).split(",") if reg.get("Elementos_Seleccionados") else []
        etiquetas = [s.strip() for s in etiquetas if s.strip() and s.strip() != "ninguno"]
        fila = {"Algoritmo": reg["Algoritmo"]}
        if por_n:
            fila["N"] = int(reg["N"])
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

    if por_n:
        agrupado = df_elem.groupby(["Algoritmo", "N"])[columnas_elem].mean()
        ejes = "Algoritmo / N"
        titulo = "Heatmap de Selección de Elementos por Algoritmo y Tamaño n"
        figsize = (max(8, len(columnas_elem) * 0.4), max(5, len(agrupado) * 0.4 + 2))
    else:
        agrupado = df_elem.groupby("Algoritmo")[columnas_elem].mean()
        ejes = "Algoritmo"
        titulo = "Heatmap de Selección de Elementos por Algoritmo (global)"
        figsize = (max(8, len(columnas_elem) * 0.4), 4.5)

    if ruta_salida is not None:
        directorio_salida = Path(ruta_salida).parent
    else:
        csv_path = Path(df.attrs.get("ruta_csv", "."))
        directorio_salida = csv_path.parent / "plots"

    directorio_salida.mkdir(parents=True, exist_ok=True)
    archivo_salida = Path(ruta_salida) if ruta_salida else directorio_salida / nombre_archivo

    plt.figure(figsize=figsize)
    sns.heatmap(agrupado, cmap="viridis", annot=True, fmt=".2f", cbar_kws={"label": "Proporción de Selección"})
    plt.xlabel("Elemento ID", fontsize=10)
    plt.ylabel(ejes, fontsize=10)
    plt.title(titulo, fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=150)
    plt.close()
    return str(archivo_salida)


def graficar_heatmap_elementos_global(ruta_csv: str, ruta_salida: str | None = None) -> str:
    """Genera el mapa de calor global con la frecuencia de selección promedio de cada elemento por algoritmo."""
    df = pd.read_csv(ruta_csv)
    df.attrs["ruta_csv"] = ruta_csv
    return _generar_heatmap_elementos_base(df, por_n=False, ruta_salida=ruta_salida, nombre_archivo="heatmap_elementos_global.png")


def graficar_heatmap_elementos(ruta_csv: str, ruta_salida: str | None = None) -> str:
    """Genera el mapa de calor detallado con la frecuencia de selección de cada elemento por algoritmo y n."""
    df = pd.read_csv(ruta_csv)
    df = df[df["N"].notna()].copy()
    df["N"] = df["N"].astype(int)
    df.attrs["ruta_csv"] = ruta_csv
    return _generar_heatmap_elementos_base(df, por_n=True, ruta_salida=ruta_salida, nombre_archivo="heatmap_elementos.png")
