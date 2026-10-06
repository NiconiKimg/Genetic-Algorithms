"""Operadores genéticos válidos para cromosomas basados en permutaciones."""

import random

from comun.modelos_tsp import IndividuoTSP


class SeleccionTorneo:
    """Selecciona el individuo de mejor aptitud entre candidatos elegidos al azar."""

    def __init__(self, tamano_torneo: int = 3) -> None:
        """Inicializa el operador con el tamaño de muestra del torneo."""
        if tamano_torneo < 2:
            raise ValueError("El torneo debe tener al menos dos participantes.")
        self.tamano_torneo = tamano_torneo

    def seleccionar(
        self,
        poblacion: list[IndividuoTSP],
        generador: random.Random,
    ) -> IndividuoTSP:
        """Extrae participantes al azar y retorna el de menor distancia total."""
        if len(poblacion) < self.tamano_torneo:
            raise ValueError("La población es menor que el tamaño del torneo.")
        candidatos = generador.sample(poblacion, self.tamano_torneo)
        return min(
            candidatos,
            key=lambda individuo: (
                individuo.distancia_total
                if individuo.distancia_total is not None
                else float("inf")
            ),
        )


class CrossoverCiclico:
    """Implementa Cycle Crossover (CX) preservando el orden relativo de permutaciones."""

    def cruzar(
        self,
        padre_1: IndividuoTSP,
        padre_2: IndividuoTSP,
    ) -> tuple[IndividuoTSP, IndividuoTSP]:
        """Genera dos descendientes válidos mediante ciclos de correspondencia de genes."""
        self._validar_padres(padre_1, padre_2)
        genes_1 = padre_1.cromosoma
        genes_2 = padre_2.cromosoma
        hijo_1: list[int | None] = [None] * len(genes_1)
        hijo_2: list[int | None] = [None] * len(genes_1)
        posiciones = {gen: posicion for posicion, gen in enumerate(genes_1)}
        ciclo = 0
        inicio = 0

        while inicio < len(genes_1):
            if hijo_1[inicio] is not None:
                inicio += 1
                continue
            posicion = inicio
            indices_ciclo: list[int] = []
            while posicion not in indices_ciclo:
                indices_ciclo.append(posicion)
                posicion = posiciones[genes_2[posicion]]
            for indice in indices_ciclo:
                if ciclo % 2 == 0:
                    hijo_1[indice] = genes_1[indice]
                    hijo_2[indice] = genes_2[indice]
                else:
                    hijo_1[indice] = genes_2[indice]
                    hijo_2[indice] = genes_1[indice]
            ciclo += 1

        hijo_1_tupla = tuple(g for g in hijo_1 if g is not None)
        hijo_2_tupla = tuple(g for g in hijo_2 if g is not None)
        return IndividuoTSP(hijo_1_tupla), IndividuoTSP(hijo_2_tupla)

    @staticmethod
    def _validar_padres(
        padre_1: IndividuoTSP,
        padre_2: IndividuoTSP,
    ) -> None:
        """Verifica que ambos progenitores posean la misma longitud y conjunto de genes."""
        if len(padre_1.cromosoma) != len(padre_2.cromosoma):
            raise ValueError("Los padres deben tener igual longitud.")
        if set(padre_1.cromosoma) != set(padre_2.cromosoma):
            raise ValueError("Los padres deben contener los mismos genes.")


class MutacionIntercambio:
    """Aplica mutación por intercambio de dos posiciones aleatorias en el cromosoma."""

    def mutar(
        self,
        individuo: IndividuoTSP,
        generador: random.Random,
    ) -> IndividuoTSP:
        """Intercambia dos genes conservando la validez de la permutación."""
        if len(individuo.cromosoma) < 2:
            return individuo
        posiciones = generador.sample(range(len(individuo.cromosoma)), 2)
        genes = list(individuo.cromosoma)
        genes[posiciones[0]], genes[posiciones[1]] = (
            genes[posiciones[1]],
            genes[posiciones[0]],
        )
        return IndividuoTSP(tuple(genes))