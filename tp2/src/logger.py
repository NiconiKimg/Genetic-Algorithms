import csv
import os
import time
import platform
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import psutil
except Exception:
    psutil = None


class Logger:
    """Logger simple para registrar métricas de ejecución en CSV.

    Campos registrados:
      algorithm, n, capacity, capacity_dimension, total_value, total_volume,
      total_weight, items_count, items_labels, time_s, num_subsets, memory_peak_mb, variant
    """

    DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "outputs" / "results.csv"

    def __init__(self, csv_path: Optional[str] = None):
        self.csv_path = Path(csv_path) if csv_path else self.DEFAULT_OUTPUT
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        self._fields = [
            "algorithm",
            "n",
            "capacity",
            "capacity_dimension",
            "total_value",
            "total_volume",
            "total_weight",
            "items_count",
            "items_labels",
            "time_s",
            "num_subsets",
            "memory_peak_mb",
            "variant",
            "platform",
        ]
        self._current: Dict[str, Any] = {}

    def _get_rss_mb(self) -> float:
        if psutil:
            try:
                p = psutil.Process()
                return p.memory_info().rss / 1024 ** 2
            except Exception:
                return 0.0
        return 0.0

    def start_run(self, algorithm: str, n: int, capacity: float, capacity_dimension: str = "volume", variant: Optional[str] = None):
        self._current = {
            "algorithm": algorithm,
            "n": n,
            "capacity": capacity,
            "capacity_dimension": capacity_dimension,
            "variant": variant or "",
            "start_time": time.perf_counter(),
            "start_mem": self._get_rss_mb(),
        }

    def end_run(self, total_value: float, total_volume: float, total_weight: float, items_labels: str, num_subsets: Optional[int] = None):
        if not self._current:
            raise RuntimeError("start_run must be called before end_run")

        end_time = time.perf_counter()
        end_mem = self._get_rss_mb()
        elapsed = end_time - self._current.get("start_time", end_time)
        mem_peak = max(self._current.get("start_mem", 0.0), end_mem)

        row = {
            "algorithm": self._current.get("algorithm", ""),
            "n": self._current.get("n", 0),
            "capacity": self._current.get("capacity", 0.0),
            "capacity_dimension": self._current.get("capacity_dimension", "volume"),
            "total_value": total_value,
            "total_volume": total_volume,
            "total_weight": total_weight,
            "items_count": len(items_labels.split(",")) if items_labels else 0,
            "items_labels": items_labels,
            "time_s": elapsed,
            "num_subsets": num_subsets if num_subsets is not None else "",
            "memory_peak_mb": round(mem_peak, 4),
            "variant": self._current.get("variant", ""),
            "platform": platform.platform(),
        }

        # Append to CSV
        write_header = not self.csv_path.exists() or self.csv_path.stat().st_size == 0
        with open(self.csv_path, "a", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self._fields)
            if write_header:
                writer.writeheader()
            # ensure all fields exist
            out_row = {k: row.get(k, "") for k in self._fields}
            writer.writerow(out_row)

        # clear current
        self._current = {}

    def csv_location(self) -> str:
        return str(self.csv_path)

    def clear(self):
        try:
            if self.csv_path.exists():
                self.csv_path.unlink()
        except Exception:
            pass
