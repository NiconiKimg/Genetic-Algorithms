import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from Plotters import plot_runtime_vs_n, plot_capacity_usage, plot_items_heatmap

csv_path = Path(__file__).resolve().parent / "outputs" / "results.csv"
print("CSV:", csv_path)

try:
    print("Generating runtime_vs_n...")
    p1 = plot_runtime_vs_n(str(csv_path))
    print("Saved:", p1)
except Exception as e:
    print("runtime plot failed:", e)

try:
    print("Generating capacity_usage...")
    p2 = plot_capacity_usage(str(csv_path))
    print("Saved:", p2)
except Exception as e:
    print("capacity plot failed:", e)

try:
    print("Generating items_heatmap...")
    p3 = plot_items_heatmap(str(csv_path))
    print("Saved:", p3)
except Exception as e:
    print("heatmap failed:", e)
