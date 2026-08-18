from dataclasses import dataclass


@dataclass
class Elemento:
    """Representa un objeto individual susceptible de ser cargado en la mochila"""
    id: int
    volumen: float = 0.0
    peso: float = 0.0
    valor: float = 0.0

    def obtener_capacidad(self, dimension: str = "volumen") -> float:
        """Retorna el volumen o el peso según la dimensión solicitada"""
        return self.peso if dimension == "peso" else self.volumen

    def obtener_ratio(self, dimension: str = "volumen") -> float:
        """Calcula la densidad de valor por unidad de capacidad (valor / capacidad)"""
        cap = self.obtener_capacidad(dimension)
        return self.valor / cap if cap > 0 else 0.0

    def __repr__(self) -> str:
        return f"Elemento(id={self.id}, volumen={self.volumen}, peso={self.peso}, valor={self.valor})"


@dataclass
class SolucionMochila:
    """Representa el resultado de la selección de elementos cargados en la mochila"""
    elementos: list[Elemento]
    volumen_total: float
    peso_total: float
    valor_total: float
    es_factible: bool = True

    def ids_elementos(self) -> list[int]:
        """Retorna la lista de identificadores de los elementos seleccionados"""
        return [elem.id for elem in self.elementos]

    def etiquetas_elementos(self) -> str:
        """Retorna los IDs de los elementos como cadena separada por comas"""
        return ", ".join(str(elem.id) for elem in self.elementos) if self.elementos else "ninguno"

    def __repr__(self) -> str:
        factible_str = "Factible" if self.es_factible else "No factible"
        return (
            f"SolucionMochila(elementos={self.ids_elementos()}, "
            f"volumen_total={self.volumen_total}, peso_total={self.peso_total}, "
            f"valor_total={self.valor_total}, estado={factible_str})"
        )


@dataclass
class Mochila:
    """Define las restricciones de capacidad física de la mochila"""
    capacidad_maxima: float
    dimension_capacidad: str = "volumen"


def evaluar_solucion(elementos: list[Elemento], mochila: Mochila) -> SolucionMochila:
    """Evalúa la suma de volumen, peso, valor y factibilidad de una lista de elementos"""
    volumen_total = 0.0
    peso_total = 0.0
    valor_total = 0.0
    for elem in elementos:
        volumen_total += elem.volumen
        peso_total += elem.peso
        valor_total += elem.valor

    if mochila.dimension_capacidad == "peso":
        factible = peso_total <= mochila.capacidad_maxima
    else:
        factible = volumen_total <= mochila.capacidad_maxima

    return SolucionMochila(
        elementos=elementos,
        volumen_total=volumen_total,
        peso_total=peso_total,
        valor_total=valor_total,
        es_factible=factible,
    )


def crear_elementos_desde_tabla(tabla: list[list[float]], inicio_id: int = 1) -> list[Elemento]:
    """Crea una lista de objetos Elemento a partir de una matriz [volumen, valor]"""
    return [Elemento(id=i + inicio_id, volumen=fila[0], valor=fila[1]) for i, fila in enumerate(tabla)]


def crear_elementos_por_peso(pesos: list[float], valores: list[float], inicio_id: int = 1) -> list[Elemento]:
    """Crea una lista de objetos Elemento a partir de listas de pesos y valores"""
    return [Elemento(id=i + inicio_id, peso=pesos[i], valor=valores[i]) for i in range(len(pesos))]
