"""Modelos y datos compartidos por los algoritmos del TP3."""

from .datos_distancia_capitales import (
    CAPITALES,
    DISTANCIAS_KM,
    INDICE_CAPITALES,
    validar_datos,
)
from .modelos_tsp import (
    EvaluadorRutas,
    IndividuoTSP,
    NodoBusqueda,
    ProblemaTSP,
    RutaTSP,
)

__all__ = [
    "CAPITALES",
    "DISTANCIAS_KM",
    "EvaluadorRutas",
    "INDICE_CAPITALES",
    "IndividuoTSP",
    "NodoBusqueda",
    "ProblemaTSP",
    "RutaTSP",
    "validar_datos",
]