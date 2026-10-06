"""Parámetros configurables para los experimentos del algoritmo genético."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfiguracionGenetica:
    """Configuración de hiperparámetros con los valores indicados en la consigna."""

    cantidad_cromosomas: int = 50
    cantidad_ciclos: int = 200
    frecuencia_crossover: float = 0.90
    frecuencia_mutacion: float = 0.10
    tamano_torneo: int = 3
    semilla: int | None = None

    def __post_init__(self) -> None:
        """Valida que los parámetros se encuentren dentro de los rangos válidos."""
        if self.cantidad_cromosomas < 2:
            raise ValueError("La población debe tener al menos dos cromosomas.")
        if self.cantidad_ciclos < 1:
            raise ValueError("La cantidad de ciclos debe ser positiva.")
        if not 0 <= self.frecuencia_crossover <= 1:
            raise ValueError("La frecuencia de crossover debe estar entre 0 y 1.")
        if not 0 <= self.frecuencia_mutacion <= 1:
            raise ValueError("La frecuencia de mutación debe estar entre 0 y 1.")
        if self.tamano_torneo < 2:
            raise ValueError("El torneo debe tener al menos dos participantes.")