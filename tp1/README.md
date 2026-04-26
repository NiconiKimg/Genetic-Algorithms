# ENUNCIADO DEL TRABAJO PRÁCTICO N° 1

Hacer un programa que utilice un **Algoritmo Genético Canónico** para buscar un máximo de la función:

$$
f(x) = \left(\frac{x}{\text{coef}}\right)^2
$$

en el dominio $[0, 2^{30} - 1]$

donde $\text{coef} = 2^{30} - 1$

Teniendo en cuenta los siguientes datos:

- **Probabilidad de Crossover:** 0,75
- **Probabilidad de Mutación:** 0,05
- **Población Inicial:** 10 individuos
- **Ciclos del programa:** 20
- **Método de Selección:** Ruleta
- **Método de Crossover:** 1 Punto
- **Método de Mutación:** invertida

---

## Opción A

El programa debe mostrar, finalmente:

- El Cromosoma correspondiente al valor máximo
- El valor máximo, mínimo y promedio obtenido de cada población
- Calcular la desviación estándar del fitness por generación (esto muestra visualmente si la población converge —desviación baja— o si sigue diversa —desviación alta—).
- Agregar explicaciones de lo observado en las conclusiones.
- Medir el tiempo de cómputo
- Agregar una tabla con tiempo de ejecución promedio para cada variante (20, 100, 200 corridas) y cada método (ruleta, torneo, elitismo). Analizar el trade-off (situación en la que se debe sacrificar un objetivo, característica o beneficio para alcanzar otro) entre calidad de solución y costo computacional.
- Mostrar la impresión de las tablas de mínimos, promedios y máximos para 20, 100 y 200 corridas.
- Presentar las gráficas de los valores Máximos, Mínimos y Promedios de la función objetivo por cada generación luego de correr el algoritmo genético 20, 100 y 200 iteraciones (una gráfica por cada conjunto de iteraciones)
- Realizar comparaciones de las salidas corriendo el mismo programa en distintos ciclos de corridas y además realizar todos los cambios que considere oportunos en los parámetros de entrada de manera de enriquecer sus conclusiones.

---

## Opción B

Aplicar lo enunciado en la opción A pero con **método de Selección de Torneo**.

---

## Opción C

Se entiende por **elite** a un grupo pequeño que por algún motivo, característica, facultad o privilegio es superior o mejor en comparación al grueso de una población determinada; con cualidades o prerrogativas de las que la gran mayoría no disfrutan.

Un algoritmo genético, desde el punto de vista de la optimización, es un método poblacional de búsqueda dirigida basada en probabilidad. Bajo una condición bastante débil, que el algoritmo mantenga elitismo, es decir, guarde siempre al mejor elemento de la población sin hacerle ningún cambio, se puede demostrar que el algoritmo converge en probabilidad al óptimo. En otras palabras, al aumentar el número de iteraciones, la probabilidad de tener el óptimo en la población tiende a uno.

Luego el método más utilizado para mejorar la convergencia de los algoritmos genéticos es el **elitismo**.

Este método consiste básicamente para nuestro trabajo en realizar la etapa de selección de la siguiente manera:

- Se realiza un muestreo en una élite de “ere” miembros, es decir, para nuestro ejercicio se seleccionan dos cromosomas que posean el mejor fitness de entre los mejores de la población inicial y se incorporan directamente a la población siguiente, sin pasar por la población intermedia.
- El proceso se repite para cada población que se va generando hasta completar el número de veces que se ejecutará el algoritmo genético. Se solicita la ejecución de 100 iteraciones.

Para esta tercera parte del trabajo se deberá utilizar elitismo, mostrar nuevamente las salidas por pantalla y las gráficas solicitadas en la PARTE A y B pero en este caso considerando la aplicación de elitismo. Resolver el ejercicio realizando 100 iteraciones del algoritmo.

Comparar los tres métodos (ruleta, torneo, elitismo) en:

- Mejor fitness alcanzado
- Generación en la que se alcanzó
- Estabilidad (desviación entre corridas)
- Tiempo de ejecución

También deberá hacer cambio de algunos de los datos de entrada y obtener conclusiones sobre los cambios efectuado según el equipo considere oportuno.

---

## Formato para el informe final

- **Introducción teórica** (AG canónico, elitismo)
- **Descripción del problema y función objetivo**
- **Parámetros fijos y variables** (tabla)
- **Codificación y Resultados para Opción A** (ruleta)
- **Codificación y Resultados para Opción B** (torneo)
- **Codificación y Resultados para Opción C** (elitismo)
- **Experimentos adicionales** (cambio de parámetros)
- **Gráficas comparativas** (máximos, mínimos, promedios)
- **Tabla resumen de estabilidad y tiempos**
- **Conclusiones y recomendación final**
