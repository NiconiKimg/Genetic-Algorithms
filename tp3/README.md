# TP3 - Problema del Viajante

Este trabajo implementa el Problema del Viajante (TSP) sobre las capitales de provincia de la República Argentina. La carpeta `src` contiene los datos y las clases reutilizables para resolver los distintos puntos mediante algoritmos exactos, busqueda heuristica y algoritmos geneticos.

## Modulos de `src`

Los componentes estan organizados por responsabilidad:

```text
src/
├── comun/          modelos y datos compartidos
├── branch_bound/   algoritmos exactos
├── heuristica/     vecino mas cercano
├── genetico/       algoritmo genetico y operadores
├── visualizacion/  coordenadas y mapa
└── gui_app.py      interfaz Tkinter
```

### `comun/datos_distancia_capitales.py`

Contiene los datos de la instancia del problema:

- `CAPITALES`: nombres de las 24 capitales.
- `DISTANCIAS_KM`: matriz simetrica de distancias en kilometros.
- `INDICE_CAPITALES`: diccionario que relaciona cada nombre con su indice en la matriz.
- `validar_datos()`: verifica que la matriz sea cuadrada, tenga diagonal cero y sea simetrica.

Ejemplo:

```python
from comun.datos_distancia_capitales import CAPITALES, DISTANCIAS_KM

origen = CAPITALES[0]
destino = CAPITALES[1]
distancia = DISTANCIAS_KM[0][1]
```

### `comun/modelos_tsp.py`

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

#### `EvaluadorRutas`

Centraliza el calculo de distancias. Permite evaluar una ruta cerrada o un cromosoma genetico. El cromosoma no contiene la ciudad inicial: para el problema completo contiene las ciudades `1` a `23`, mientras que la ciudad `0` se agrega como origen y retorno al construir la ruta.

Metodos principales:

- `distancia_recorrido(recorrido)`: calcula una ruta cerrada valida.
- `distancia_cromosoma(cromosoma, ciudad_inicial)`: evalua una permutacion genetica.
- `crear_ruta(cromosoma, ciudad_inicial)`: convierte un cromosoma en `RutaTSP`.

#### `IndividuoTSP`

Representa un cromosoma como una tupla inmutable y opcionalmente guarda su distancia total. `evaluar()` devuelve el individuo evaluado, `ruta()` lo convierte en una ruta cerrada y `fitness` devuelve `1 / distancia_total`.

### `branch_bound/branch_bound.py`

Contiene el Branch and Bound secuencial.

#### `BranchBound`

Resuelve una instancia de `ProblemaTSP` de forma exacta. Utiliza una unica mejor solucion global y una cota inferior para podar ramas que no pueden mejorarla.

Uso basico:

```python
from branch_bound.branch_bound import BranchBound
from comun.datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
from comun.modelos_tsp import ProblemaTSP

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

### `branch_bound/branch_bound_paralelo.py`

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

### `genetico/configuracion_genetica.py`

Contiene `ConfiguracionGenetica`, una clase con los parametros del algoritmo genetico. Sus valores por defecto siguen las recomendaciones del enunciado:

- `cantidad_cromosomas = 50`.
- `cantidad_ciclos = 200`.
- `frecuencia_crossover = 0.90`.
- `frecuencia_mutacion = 0.10`.
- `tamano_torneo = 3`.

Las frecuencias y la semilla aleatoria pueden modificarse para comparar experimentos.

### `genetico/poblacion_tsp.py`

Contiene `PoblacionTSP`, responsable de generar, evaluar y administrar individuos.

- `aleatoria(ciudades, cantidad, generador)`: crea la poblacion inicial.
- `evaluar(evaluador, ciudad_inicial)`: calcula la distancia de cada individuo.
- `mejor()`: devuelve el individuo con menor distancia.
- `mejor_ruta(evaluador, ciudad_inicial)`: devuelve el mejor individuo como `RutaTSP`.
- `conservar_elite(individuo)`: conserva una solucion elite reemplazando al peor individuo.

### `genetico/operadores_geneticos.py`

Contiene operadores que conservan la validez de las permutaciones.

#### `SeleccionTorneo`

Elige aleatoriamente varios candidatos y devuelve el de menor distancia. Es una estrategia de seleccion reutilizable para formar parejas de padres.

#### `CrossoverCiclico`

Implementa el crossover ciclico (Cycle Crossover, CX) recomendado por el enunciado. Recibe dos `IndividuoTSP` y devuelve dos hijos que contienen exactamente los mismos genes, sin repetidos ni faltantes.

#### `MutacionIntercambio`

Intercambia dos posiciones del cromosoma. Al operar sobre una permutacion, mantiene siempre una ruta valida.

### `heuristica/heuristica_vecino.py`

Contiene `VecinoMasCercano`, que implementa la heuristica solicitada: desde la ciudad actual visita la ciudad no visitada mas cercana y, despues de visitar todas, regresa a la ciudad inicial.

```python
from heuristica.heuristica_vecino import VecinoMasCercano

heuristica = VecinoMasCercano(problema)
ruta = heuristica.resolver(ciudad_inicial=0)
mejor_de_todos = heuristica.resolver_todos_los_inicios()
```

`resolver()` corresponde al punto 2.a, porque permite elegir la ciudad de partida. `resolver_todos_los_inicios()` resulta util para el punto 2.b, porque ejecuta la heuristica desde cada capital y devuelve la mejor ruta heuristica encontrada.

### `genetico/algoritmo_genetico_tsp.py`

Contiene `AlgoritmoGeneticoTSP`, que sigue la segmentacion utilizada en TP1: el orquestador coordina la poblacion, la seleccion, el crossover, la mutacion y el elitismo.

La configuracion por defecto se encuentra en `ConfiguracionGenetica`:

- 50 cromosomas por poblacion.
- 200 ciclos evolutivos.
- Crossover ciclico (`CrossoverCiclico`).
- Mutacion por intercambio (`MutacionIntercambio`).
- Seleccion por torneo (`SeleccionTorneo`).

El algoritmo devuelve `ResultadoAlgoritmoGenetico`, que contiene la mejor `RutaTSP`, el tiempo de ejecucion y el historial de cada generacion. Como es un metodo aproximado, no garantiza alcanzar el optimo; sus resultados deben compararse con Branch and Bound y la heuristica del vecino mas cercano.

Ejemplo:

```python
from genetico.algoritmo_genetico_tsp import AlgoritmoGeneticoTSP
from genetico.configuracion_genetica import ConfiguracionGenetica

configuracion = ConfiguracionGenetica(semilla=42)
resultado = AlgoritmoGeneticoTSP(problema, configuracion).resolver()
```

### `visualizacion/` y `gui_app.py`

`visualizacion/` contiene las coordenadas de las capitales y el contorno de respaldo. `gui_app.py` contiene la interfaz Tkinter y utiliza `TkinterMapView` para mostrar OpenStreetMap.

## Scripts disponibles

- `scripts/ejercicio_1.py`: ejecuta el ejercicio 1, valida la ruta y muestra el informe.
- `scripts/comparar_branch_bound.py`: compara los tiempos del Branch and Bound secuencial y paralelo en instancias reducidas.
- `scripts/ejercicio_2c.py`: ejecuta el algoritmo genetico sobre las 24 capitales.

La interfaz utiliza `TkinterMapView` para mostrar OpenStreetMap en la pestaña 2.a. Requiere conexion a Internet para descargar las teselas del mapa. El visor permite zoom y desplazamiento con el mouse, y la ruta heuristica se dibuja sobre las capitales.

Para ejecutar el ejercicio sobre una instancia pequeña:

```powershell
.\env\Scripts\python.exe tp3/scripts/ejercicio_1.py --ciudades 8
```

Para ejecutar el problema completo:

```powershell
.\env\Scripts\python.exe tp3/scripts/ejercicio_1.py
```

Para iniciar la interfaz grafica:

```powershell
.\env\Scripts\python.exe tp3/src/gui_app.py
```
