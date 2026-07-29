import csv
import time
from pathlib import Path
from typing import Any, Optional


class Logger:
    """Registra y exporta las estadísticas de ejecución exclusivamente a un archivo CSV"""

    campos: list[str]
    registros: list[dict[str, Any]]

    def __init__(self) -> None:
        """Inicializa las estructuras para almacenar las métricas de la corrida"""
        self.campos = [
            "Algoritmo",
            "N",
            "Capacidad",
            "Dimension",
            "Valor_Total",
            "Volumen_Total",
            "Peso_Total",
            "Cantidad_Elementos",
            "Elementos_Seleccionados",
            "Tiempo_Segundos",
            "Subconjuntos_Evaluados",
        ]
        self.registros = []
        self._ejecucion_actual: dict[str, Any] = {}

    def iniciar_ejecucion(
        self,
        algoritmo: str,
        n: int,
        capacidad: float,
        dimension_capacidad: str = "volumen",
    ) -> None:
        """Registra el inicio de una corrida midiendo el tiempo inicial"""
        self._ejecucion_actual = {
            "algoritmo": algoritmo,
            "n": n,
            "capacidad": capacidad,
            "dimension_capacidad": dimension_capacidad,
            "tiempo_inicio": time.perf_counter(),
        }

    def finalizar_ejecucion(
        self,
        valor_total: float,
        volumen_total: float,
        peso_total: float,
        etiquetas_elementos: str,
        subconjuntos_evaluados: Optional[int] = None,
    ) -> float:
        """Calcula el tiempo transcurrido y almacena el registro en memoria"""
        if not self._ejecucion_actual:
            raise RuntimeError("Debe llamarse a iniciar_ejecucion antes de finalizar_ejecucion")

        tiempo_fin = time.perf_counter()
        elapsed = tiempo_fin - self._ejecucion_actual.get("tiempo_inicio", tiempo_fin)

        cantidad = (
            len(etiquetas_elementos.split(","))
            if etiquetas_elementos and etiquetas_elementos != "ninguno"
            else 0
        )

        registro = {
            "Algoritmo": self._ejecucion_actual.get("algoritmo", ""),
            "N": self._ejecucion_actual.get("n", 0),
            "Capacidad": self._ejecucion_actual.get("capacidad", 0.0),
            "Dimension": self._ejecucion_actual.get("dimension_capacidad", "volumen"),
            "Valor_Total": valor_total,
            "Volumen_Total": volumen_total,
            "Peso_Total": peso_total,
            "Cantidad_Elementos": cantidad,
            "Elementos_Seleccionados": etiquetas_elementos,
            "Tiempo_Segundos": round(elapsed, 6),
            "Subconjuntos_Evaluados": subconjuntos_evaluados if subconjuntos_evaluados is not None else "-",
        }

        self.registros.append(registro)
        self._ejecucion_actual = {}
        return elapsed

    def exportar_tabla(
        self,
        directorio_salida: str | Path,
        nombre_base: str,
    ) -> str:
        """Exporta las estadísticas acumuladas a un único archivo CSV"""
        directorio = Path(directorio_salida)
        directorio.mkdir(parents=True, exist_ok=True)

        ruta_csv = directorio / f"{nombre_base}.csv"

        with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=self.campos)
            escritor.writeheader()
            for reg in self.registros:
                escritor.writerow(reg)

        return str(ruta_csv)

    def limpiar(self) -> None:
        """Limpia el historial de registros en memoria"""
        self.registros = []
        self._ejecucion_actual = {}
