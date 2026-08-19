"""Clases reutilizables para representar instancias y soluciones del TSP."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProblemaTSP:
    """Una instancia simetrica del problema del viajante."""

    ciudades: tuple[str, ...]
    distancias: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        cantidad_ciudades = len(self.ciudades)
        if cantidad_ciudades == 0:
            raise ValueError("El problema debe tener al menos una ciudad.")
        if len(self.distancias) != cantidad_ciudades:
            raise ValueError("Debe existir una fila por ciudad.")
        if any(len(fila) != cantidad_ciudades for fila in self.distancias):
            raise ValueError("La matriz de distancias debe ser cuadrada.")

    @property
    def cantidad_ciudades(self) -> int:
        return len(self.ciudades)

    def distancia(self, origen: int, destino: int) -> int:
        return self.distancias[origen][destino]

    def nombre_ciudad(self, indice: int) -> str:
        return self.ciudades[indice]


@dataclass(frozen=True)
class RutaTSP:
    """Ruta cerrada y su distancia total."""

    recorrido: tuple[int, ...]
    distancia_total: int

    def nombres(self, problema: ProblemaTSP) -> tuple[str, ...]:
        return tuple(problema.nombre_ciudad(indice) for indice in self.recorrido)


@dataclass(frozen=True)
class NodoBusqueda:
    """Estado parcial de una rama del arbol de busqueda."""

    recorrido: tuple[int, ...]
    no_visitadas: frozenset[int]
    distancia_actual: int
