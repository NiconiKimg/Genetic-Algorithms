"""Algoritmo genetico para resolver el TSP con cromosomas de permutacion."""

from dataclasses import dataclass
import random
from time import perf_counter

try:
    from .configuracion_genetica import ConfiguracionGenetica
    from comun.modelos_tsp import EvaluadorRutas, IndividuoTSP, ProblemaTSP, RutaTSP
    from .operadores_geneticos import (
        CrossoverCiclico,
        MutacionIntercambio,
        SeleccionTorneo,
    )
    from .poblacion_tsp import PoblacionTSP
except ImportError:
    from configuracion_genetica import ConfiguracionGenetica
    from comun.modelos_tsp import EvaluadorRutas, IndividuoTSP, ProblemaTSP, RutaTSP
    from operadores_geneticos import CrossoverCiclico, MutacionIntercambio, SeleccionTorneo
    from poblacion_tsp import PoblacionTSP


@dataclass(frozen=True)
class RegistroGeneracion:
    """Mejor y promedio de una generacion."""

    ciclo: int
    mejor_distancia: int
    distancia_promedio: float


@dataclass(frozen=True)
class ResultadoAlgoritmoGenetico:
    """Resultado final del algoritmo genetico."""

    ruta: RutaTSP
    segundos: float
    historial: tuple[RegistroGeneracion, ...]


class AlgoritmoGeneticoTSP:
    """Orquesta poblacion, seleccion, crossover ciclico, mutacion y elitismo."""

    def __init__(
        self,
        problema: ProblemaTSP,
        configuracion: ConfiguracionGenetica | None = None,
        ciudad_inicial: int = 0,
    ) -> None:
        self.problema = problema
        self.configuracion = configuracion or ConfiguracionGenetica()
        self.ciudad_inicial = ciudad_inicial
        self.evaluador = EvaluadorRutas(problema)
        self.generador = random.Random(self.configuracion.semilla)
        self.seleccion = SeleccionTorneo(self.configuracion.tamano_torneo)
        self.crossover = CrossoverCiclico()
        self.mutacion = MutacionIntercambio()

    def resolver(self) -> ResultadoAlgoritmoGenetico:
        """Ejecuta la cantidad configurada de ciclos y devuelve la mejor ruta."""
        inicio = perf_counter()
        ciudades = tuple(
            indice
            for indice in range(self.problema.cantidad_ciudades)
            if indice != self.ciudad_inicial
        )
        poblacion = PoblacionTSP.aleatoria(
            ciudades,
            self.configuracion.cantidad_cromosomas,
            self.generador,
        )
        poblacion.evaluar(self.evaluador, self.ciudad_inicial)
        historial = [self._registrar_generacion(1, poblacion)]
        mejor_global = poblacion.mejor()

        for ciclo in range(2, self.configuracion.cantidad_ciclos + 1):
            elite = poblacion.mejor()
            nueva_poblacion: list[IndividuoTSP] = [elite]
            while len(nueva_poblacion) < self.configuracion.cantidad_cromosomas:
                padre_1 = self.seleccion.seleccionar(poblacion.individuos, self.generador)
                padre_2 = self.seleccion.seleccionar(poblacion.individuos, self.generador)
                if self.generador.random() < self.configuracion.frecuencia_crossover:
                    hijos = self.crossover.cruzar(padre_1, padre_2)
                else:
                    hijos = (IndividuoTSP(padre_1.cromosoma), IndividuoTSP(padre_2.cromosoma))
                for hijo in hijos:
                    if len(nueva_poblacion) >= self.configuracion.cantidad_cromosomas:
                        break
                    if self.generador.random() < self.configuracion.frecuencia_mutacion:
                        hijo = self.mutacion.mutar(hijo, self.generador)
                    nueva_poblacion.append(hijo)

            poblacion = PoblacionTSP(nueva_poblacion)
            poblacion.evaluar(self.evaluador, self.ciudad_inicial)
            mejor_actual = poblacion.mejor()
            if (mejor_global.distancia_total is None or mejor_actual.distancia_total < mejor_global.distancia_total):
                mejor_global = mejor_actual
            historial.append(self._registrar_generacion(ciclo, poblacion))

        return ResultadoAlgoritmoGenetico(
            ruta=mejor_global.ruta(self.evaluador, self.ciudad_inicial),
            segundos=perf_counter() - inicio,
            historial=tuple(historial),
        )

    @staticmethod
    def _registrar_generacion(ciclo: int, poblacion: PoblacionTSP) -> RegistroGeneracion:
        distancias = [
            individuo.distancia_total
            for individuo in poblacion.individuos
            if individuo.distancia_total is not None
        ]
        return RegistroGeneracion(
            ciclo=ciclo,
            mejor_distancia=min(distancias),
            distancia_promedio=sum(distancias) / len(distancias),
        )
