"""Heuristica del vecino mas cercano para el Problema del Viajante."""

try:
    from .modelos_tsp import ProblemaTSP, RutaTSP
except ImportError:
    from modelos_tsp import ProblemaTSP, RutaTSP


class VecinoMasCercano:
    """Construye una ruta eligiendo siempre el vecino no visitado mas cercano."""

    def __init__(self, problema: ProblemaTSP) -> None:
        self.problema = problema

    def resolver(self, ciudad_inicial: int = 0) -> RutaTSP:
        """Resuelve desde una ciudad y regresa a ella al finalizar."""
        self._validar_ciudad(ciudad_inicial)
        recorrido = [ciudad_inicial]
        no_visitadas = set(range(self.problema.cantidad_ciudades))
        no_visitadas.remove(ciudad_inicial)
        distancia_total = 0

        while no_visitadas:
            ciudad_actual = recorrido[-1]
            siguiente = min(
                no_visitadas,
                key=lambda ciudad: (
                    self.problema.distancia(ciudad_actual, ciudad),
                    ciudad,
                ),
            )
            distancia_total += self.problema.distancia(ciudad_actual, siguiente)
            recorrido.append(siguiente)
            no_visitadas.remove(siguiente)

        distancia_total += self.problema.distancia(recorrido[-1], ciudad_inicial)
        recorrido.append(ciudad_inicial)
        return RutaTSP(tuple(recorrido), distancia_total)

    def resolver_todos_los_inicios(self) -> RutaTSP:
        """Devuelve la mejor ruta heuristica probando cada ciudad como inicio."""
        rutas = (
            self.resolver(ciudad_inicial)
            for ciudad_inicial in range(self.problema.cantidad_ciudades)
        )
        return min(rutas, key=lambda ruta: ruta.distancia_total)

    def _validar_ciudad(self, ciudad: int) -> None:
        if not 0 <= ciudad < self.problema.cantidad_ciudades:
            raise ValueError("La ciudad inicial no existe en el problema.")