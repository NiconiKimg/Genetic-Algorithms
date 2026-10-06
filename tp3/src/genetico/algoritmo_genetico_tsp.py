"""Algoritmo genético para resolver el TSP con cromosomas de permutación."""

from dataclasses import dataclass
import random
from time import perf_counter

from comun.modelos_tsp import EvaluadorRutas, IndividuoTSP, ProblemaTSP, RutaTSP
from genetico.configuracion_genetica import ConfiguracionGenetica
from genetico.operadores_geneticos import (
    CrossoverCiclico,
    MutacionIntercambio,
    SeleccionTorneo,
)
from genetico.poblacion_tsp import PoblacionTSP


@dataclass(frozen=True)
class RegistroGeneracion:
    """Métricas de desempeño (mejor distancia y promedio) registradas en un ciclo evolutivo."""

    ciclo: int
    mejor_distancia: int
    distancia_promedio: float


@dataclass(frozen=True)
class ResultadoAlgoritmoGenetico:
    """Resultado final del algoritmo genético con la mejor ruta y su historial evolutivo."""

    ruta: RutaTSP
    segundos: float
    historial: tuple[RegistroGeneracion, ...]


class AlgoritmoGeneticoTSP:
    """Orquesta la población, selección, crossover cíclico, mutación y elitismo para el TSP."""

    def __init__(
        self,
        problema: ProblemaTSP,
        configuracion: ConfiguracionGenetica | None = None,
        ciudad_inicial: int = 0,
    ) -> None:
        """Inicializa el algoritmo genético con el problema y los hiperparámetros dados."""
        self.problema = problema
        self.configuracion = configuracion or ConfiguracionGenetica()
        self.ciudad_inicial = ciudad_inicial
        self.evaluador = EvaluadorRutas(problema)
        self.generador = random.Random(self.configuracion.semilla)
        self.seleccion = SeleccionTorneo(self.configuracion.tamano_torneo)
        self.crossover = CrossoverCiclico()
        self.mutacion = MutacionIntercambio()

    def resolver(self) -> ResultadoAlgoritmoGenetico:
        """Ejecuta el ciclo evolutivo completo y retorna la mejor ruta hallada junto al historial."""
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
                    hijos = (
                        IndividuoTSP(padre_1.cromosoma),
                        IndividuoTSP(padre_2.cromosoma),
                    )
                for hijo in hijos:
                    if len(nueva_poblacion) >= self.configuracion.cantidad_cromosomas:
                        break
                    if self.generador.random() < self.configuracion.frecuencia_mutacion:
                        hijo = self.mutacion.mutar(hijo, self.generador)
                    nueva_poblacion.append(hijo)

            poblacion = PoblacionTSP(nueva_poblacion)
            poblacion.evaluar(self.evaluador, self.ciudad_inicial)
            mejor_actual = poblacion.mejor()
            if (
                mejor_global.distancia_total is None
                or (
                    mejor_actual.distancia_total is not None
                    and mejor_actual.distancia_total < mejor_global.distancia_total
                )
            ):
                mejor_global = mejor_actual
            historial.append(self._registrar_generacion(ciclo, poblacion))

        return ResultadoAlgoritmoGenetico(
            ruta=mejor_global.ruta(self.evaluador, self.ciudad_inicial),
            segundos=perf_counter() - inicio,
            historial=tuple(historial),
        )

    @staticmethod
    def _registrar_generacion(
        ciclo: int,
        poblacion: PoblacionTSP,
    ) -> RegistroGeneracion:
        """Calcula el mejor y promedio de aptitud de la población en la generación actual."""
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
