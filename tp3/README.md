# TP3 - Problema del Viajante

Este trabajo implementa el Problema del Viajante (TSP) sobre las capitales de provincia de la República Argentina. La carpeta `src` contiene los datos y las clases reutilizables para resolver los distintos puntos mediante algoritmos exactos, busqueda heuristica y algoritmos geneticos.

## Modulos de `src`

### `datos_distancia_capitales.py`

Contiene los datos de la instancia del problema:

- `CAPITALES`: nombres de las 24 capitales.
- `DISTANCIAS_KM`: matriz simetrica de distancias en kilometros.
- `INDICE_CAPITALES`: diccionario que relaciona cada nombre con su indice en la matriz.
- `validar_datos()`: verifica que la matriz sea cuadrada, tenga diagonal cero y sea simetrica.

Ejemplo:

```python
from datos_distancia_capitales import CAPITALES, DISTANCIAS_KM

origen = CAPITALES[0]
destino = CAPITALES[1]
distancia = DISTANCIAS_KM[0][1]
```

### `modelos_tsp.py`

Define las clases de dominio compartidas por todos los algoritmos.

#### `ProblemaTSP`

Representa una instancia del problema.

Atributos principales:

- `ciudades`: nombres de las ciudades.
- `distancias`: matriz de distancias.

Metodos principales:

- `cantidad_ciudades`: cantidad de ciudades.
- `distancia(origen, destino)`: obtiene la distancia entre dos indices.
- `nombre_ciudad(indice)`: obtiene el nombre de una ciudad.

Esta clase debe utilizarse como entrada de los algoritmos heuristico y genetico.

#### `RutaTSP`

Representa una ruta cerrada y su costo.

Atributos:

- `recorrido`: tupla de indices de ciudades. La primera y la ultima ciudad deben coincidir.
- `distancia_total`: distancia total de la ruta en kilometros.

Metodo:

- `nombres(problema)`: convierte los indices del recorrido en nombres de ciudades.

Puede utilizarse como individuo, solucion candidata o resultado de cualquier algoritmo.

#### `NodoBusqueda`

Representa un estado parcial durante una busqueda.

Atributos:

- `recorrido`: ciudades visitadas hasta el momento.
- `no_visitadas`: conjunto de ciudades pendientes.
- `distancia_actual`: costo acumulado del recorrido parcial.

Es util para Branch and Bound y puede servir como base para otras estrategias de exploracion.

### `branch_bound.py`

Contiene el Branch and Bound secuencial.

#### `BranchBound`

Resuelve una instancia de `ProblemaTSP` de forma exacta. Utiliza una unica mejor solucion global y una cota inferior para podar ramas que no pueden mejorarla.

Uso basico:

```python
from branch_bound import BranchBound
from datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
from modelos_tsp import ProblemaTSP

problema = ProblemaTSP(CAPITALES, DISTANCIAS_KM)
resultado = BranchBound(problema).resolver()

print(resultado.ruta.distancia_total)
print(resultado.ruta.nombres(problema))
```

#### `ResultadoBranchBound`

Contiene el resultado de la busqueda:

- `ruta`: instancia de `RutaTSP` con la mejor ruta encontrada.
- `nodos_explorados`: cantidad de nodos procesados.
- `nodos_podados`: cantidad de nodos descartados mediante la cota inferior.

### `branch_bound_paralelo.py`

Contiene una version paralela de Branch and Bound. Divide el arbol en ramas iniciales y las procesa mediante procesos independientes.

#### `BranchBoundParalelo`

Recibe un `ProblemaTSP`, una ciudad inicial y opcionalmente la cantidad de procesos.

```python
from branch_bound_paralelo import BranchBoundParalelo

resultado = BranchBoundParalelo(
    problema,
    ciudad_inicial=0,
    cantidad_procesos=2,
).resolver()
```

#### `ResultadoBusqueda`

Tiene la misma informacion general que `ResultadoBranchBound`:

- `ruta`.
- `nodos_explorados`.
- `nodos_podados`.

La version secuencial suele ser mas conveniente para esta instancia debido al costo de crear procesos y a que los procesos paralelos no comparten la mejor cota global.

## Clases recomendadas para los siguientes puntos

Para una busqueda heuristica se recomienda reutilizar:

- `ProblemaTSP` para acceder a ciudades y distancias.
- `RutaTSP` para representar una solucion candidata.
- `distancia_total` de `RutaTSP` como funcion de evaluacion.

Para un algoritmo genetico se recomienda utilizar:

- `RutaTSP` como representacion de un individuo.
- `recorrido` como cromosoma o permutacion de ciudades.
- `ProblemaTSP.distancia()` para calcular el costo de cada arista.
- `ProblemaTSP` como contexto compartido por la poblacion.

`NodoBusqueda` pertenece especificamente a las estrategias de exploracion de arbol y no es necesario para representar individuos de un algoritmo genetico.

## Scripts disponibles

- `scripts/ejercicio_1.py`: ejecuta el ejercicio 1, valida la ruta y muestra el informe.
- `scripts/comparar_branch_bound.py`: compara los tiempos del Branch and Bound secuencial y paralelo en instancias reducidas.

Para ejecutar el ejercicio sobre una instancia pequeña:

```powershell
.\env\Scripts\python.exe tp3/scripts/ejercicio_1.py --ciudades 8
```

Para ejecutar el problema completo:

```powershell
.\env\Scripts\python.exe tp3/scripts/ejercicio_1.py
```
