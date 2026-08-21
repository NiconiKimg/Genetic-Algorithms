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

    def validar_permutacion(self, recorrido: tuple[int, ...]) -> None:
        """Verifica una permutacion de todas las ciudades del problema."""
        esperado = set(range(self.cantidad_ciudades))
        if set(recorrido) != esperado or len(recorrido) != self.cantidad_ciudades:
            raise ValueError("El recorrido no es una permutacion valida.")


@dataclass(frozen=True)
class RutaTSP:
    """Ruta cerrada y su distancia total."""

    recorrido: tuple[int, ...]
    distancia_total: int

    def nombres(self, problema: ProblemaTSP) -> tuple[str, ...]:
        return tuple(problema.nombre_ciudad(indice) for indice in self.recorrido)


@dataclass(frozen=True)
class EvaluadorRutas:
    """Calcula el costo de rutas y cromosomas para cualquier algoritmo."""

    problema: ProblemaTSP

    def distancia_recorrido(self, recorrido: tuple[int, ...]) -> int:
        if len(recorrido) < 2:
            raise ValueError("El recorrido debe tener al menos dos ciudades.")
        if recorrido[0] != recorrido[-1]:
            raise ValueError("El recorrido debe volver a la ciudad inicial.")
        self.problema.validar_permutacion(recorrido[:-1])
        return sum(
            self.problema.distancia(origen, destino)
            for origen, destino in zip(recorrido, recorrido[1:])
        )

    def distancia_cromosoma(
        self,
        cromosoma: tuple[int, ...],
        ciudad_inicial: int = 0,
    ) -> int:
        """Evalua una permutacion sin origen, cerrandola sobre la ciudad inicial."""
        if not 0 <= ciudad_inicial < self.problema.cantidad_ciudades:
            raise ValueError("La ciudad inicial no existe en el problema.")
        ciudades_esperadas = set(range(self.problema.cantidad_ciudades)) - {
            ciudad_inicial
        }
        if set(cromosoma) != ciudades_esperadas or len(cromosoma) != len(
            ciudades_esperadas
        ):
            raise ValueError("El cromosoma no es una permutacion valida.")
        recorrido = (ciudad_inicial,) + cromosoma + (ciudad_inicial,)
        return self.distancia_recorrido(recorrido)

    def crear_ruta(
        self,
        cromosoma: tuple[int, ...],
        ciudad_inicial: int = 0,
    ) -> RutaTSP:
        distancia = self.distancia_cromosoma(cromosoma, ciudad_inicial)
        recorrido = (ciudad_inicial,) + cromosoma + (ciudad_inicial,)
        return RutaTSP(recorrido, distancia)


@dataclass(frozen=True)
class IndividuoTSP:
    """Cromosoma TSP: permutacion de ciudades sin repetir el origen."""

    cromosoma: tuple[int, ...]
    distancia_total: int | None = None

    def evaluar(
        self,
        evaluador: EvaluadorRutas,
        ciudad_inicial: int = 0,
    ) -> "IndividuoTSP":
        distancia = evaluador.distancia_cromosoma(self.cromosoma, ciudad_inicial)
        return IndividuoTSP(self.cromosoma, distancia)

    def ruta(
        self,
        evaluador: EvaluadorRutas,
        ciudad_inicial: int = 0,
    ) -> RutaTSP:
        return evaluador.crear_ruta(self.cromosoma, ciudad_inicial)

    @property
    def fitness(self) -> float:
        if self.distancia_total is None:
            raise ValueError("El individuo debe evaluarse antes de consultar fitness.")
        return 1 / self.distancia_total


@dataclass(frozen=True)
class NodoBusqueda:
    """Estado parcial de una rama del arbol de busqueda."""

    recorrido: tuple[int, ...]
    no_visitadas: frozenset[int]
    distancia_actual: int
