"""Funciones de graficado para TP2: runtime, uso de capacidad e items heatmap.

Requiere: pandas, matplotlib, seaborn (se importan bajo try/except para mensajes claros).
"""
from pathlib import Path
from typing import Optional

try:
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
except Exception:
    pd = None
    sns = None
    plt = None


def _ensure_libs():
    if pd is None or sns is None or plt is None:
        raise RuntimeError("Plotting requires pandas, seaborn and matplotlib. Install them in your environment.")


def plot_runtime_vs_n(csv_path: str, out_path: Optional[str] = None):
    _ensure_libs()
    df = pd.read_csv(csv_path)
    df = df[df["n"].notna()]
    df["n"] = df["n"].astype(int)

    agg = df.groupby(["algorithm", "n"])["time_s"].agg(["mean", "std"]).reset_index()

    out_dir = Path(csv_path).parent / "plots"
    out_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    sns.lineplot(data=agg, x="n", y="mean", hue="algorithm", marker="o")
    # optional fill for first algorithm only (visual aid)
    try:
        first_alg = agg.algorithm.unique()[0]
        subset = agg[agg.algorithm == first_alg]
        plt.fill_between(subset.n,
                         subset["mean"] - subset["std"],
                         subset["mean"] + subset["std"],
                         alpha=0.15)
    except Exception:
        pass
    plt.yscale('log')
    plt.xlabel("Número de elementos (n)")
    plt.ylabel("Tiempo medio (s) [log scale]")
    plt.title("Runtime vs n")
    out_file = out_dir / "runtime_vs_n.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=150)
    plt.close()
    return str(out_file)


def plot_capacity_usage(csv_path: str, out_path: Optional[str] = None):
    _ensure_libs()
    df = pd.read_csv(csv_path)
    # select only runs with numeric total_volume
    df = df[df["total_volume"].notna()]
    df["n"] = df["n"].astype(int)

    out_dir = Path(csv_path).parent / "plots"
    out_dir.mkdir(parents=True, exist_ok=True)

    # stacked bar: for each run, show used capacity vs remaining
    df_plot = df.copy()
    df_plot["used"] = df_plot["total_volume"].fillna(0)
    df_plot["remaining"] = df_plot["capacity"] - df_plot["used"]

    # limit to one run per algorithm/n for clarity (mean)
    agg = df_plot.groupby(["algorithm", "n"]).agg({"used":"mean", "remaining":"mean"}).reset_index()

    pivot = agg.pivot(index="n", columns="algorithm", values="used")

    pivot.plot(kind='bar', figsize=(10,6))
    plt.xlabel("n")
    plt.ylabel("Volumen usado (media)")
    plt.title("Uso de capacidad por algoritmo (media)")
    out_file = out_dir / "capacity_usage.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=150)
    plt.close()
    return str(out_file)


def plot_items_heatmap(csv_path: str, out_path: Optional[str] = None, max_items: int = 30):
    _ensure_libs()
    df = pd.read_csv(csv_path)
    # parse items_labels into columns
    rows = []
    for _, r in df.iterrows():
        labels = str(r.get('items_labels', '')).split(',') if r.get('items_labels') else []
        labels = [s.strip() for s in labels if s.strip()]
        row = {'algorithm': r['algorithm'], 'n': int(r['n']) if pd.notna(r['n']) else 0}
        for lab in labels:
            try:
                idx = int(lab)
            except Exception:
                continue
            row[f'item_{idx}'] = 1
        rows.append(row)

    if not rows:
        raise RuntimeError("No hay datos de items en CSV para generar heatmap")

    df_items = pd.DataFrame(rows).fillna(0)
    item_cols = [c for c in df_items.columns if c.startswith('item_')]
    # aggregate by algorithm
    agg = df_items.groupby('algorithm')[item_cols].mean()

    out_dir = Path(csv_path).parent / "plots"
    out_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(max(8, len(item_cols)*0.3), 4))
    sns.heatmap(agg, cmap='viridis', cbar_kws={'label':'Proporción de ejecuciones que seleccionan el item'})
    plt.xlabel('Item')
    plt.ylabel('Algorithm')
    plt.title('Heatmap de selección de items por algoritmo')
    out_file = out_dir / "items_heatmap.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=150)
    plt.close()
    return str(out_file)
