"""Interfaz Tkinter para ejecutar el ejercicio 1 del TP3."""

from dataclasses import dataclass
import queue
from pathlib import Path
import sys
import threading
from time import perf_counter
import tkinter as tk
from tkinter import messagebox, ttk
from tkintermapview import TkinterMapView

RAIZ_TP3 = Path(__file__).resolve().parents[1]
if str(RAIZ_TP3 / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ_TP3 / "src"))

from branch_bound.branch_bound import BranchBound
from branch_bound.branch_bound_paralelo import BranchBoundParalelo
from genetico.algoritmo_genetico_tsp import AlgoritmoGeneticoTSP
from genetico.configuracion_genetica import ConfiguracionGenetica
from heuristica.heuristica_vecino import VecinoMasCercano
from comun.datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
from comun.modelos_tsp import ProblemaTSP, RutaTSP
from visualizacion.coordenadas_capitales import COORDENADAS_CAPITALES


@dataclass(frozen=True)
class ResultadoGUI:
    """Datos listos para mostrar en la interfaz."""

    algoritmo: str
    cantidad_ciudades: int
    ruta: RutaTSP
    segundos: float
    nodos_explorados: int
    nodos_podados: int


@dataclass(frozen=True)
class ResultadoHeuristicoGUI:
    """Datos de la ruta heurística para la pestaña 2.a."""

    ciudad_inicial: int
    ruta: RutaTSP
    segundos: float


@dataclass(frozen=True)
class ResultadoHeuristicoTodosGUI:
    """Datos de la mejor ruta heurística evaluando todos los inicios para la pestaña 2.b."""

    mejor_ciudad_inicial: int
    ruta: RutaTSP
    segundos: float
    ranking: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class ResultadoGeneticoGUI:
    """Datos del algoritmo genetico para la pestaña 2.c."""

    ciudad_inicial: int
    ruta: RutaTSP
    segundos: float
    cantidad_cromosomas: int
    cantidad_ciclos: int
    frecuencia_crossover: float
    frecuencia_mutacion: float


def crear_problema(cantidad_ciudades: int) -> ProblemaTSP:
    """Crea una instancia usando las primeras ciudades seleccionadas."""
    indices = range(cantidad_ciudades)
    return ProblemaTSP(
        tuple(CAPITALES[indice] for indice in indices),
        tuple(
            tuple(DISTANCIAS_KM[fila][columna] for columna in indices)
            for fila in indices
        ),
    )


def ejecutar_algoritmo(
    algoritmo: str,
    cantidad_ciudades: int,
    cantidad_procesos: int,
) -> ResultadoGUI:
    """Ejecuta el solver seleccionado sin depender de la interfaz."""
    problema = crear_problema(cantidad_ciudades)
    inicio = perf_counter()
    if algoritmo == "Branch and Bound secuencial":
        resultado = BranchBound(problema).resolver()
    else:
        resultado = BranchBoundParalelo(
            problema,
            cantidad_procesos=cantidad_procesos,
        ).resolver()
    segundos = perf_counter() - inicio
    return ResultadoGUI(
        algoritmo=algoritmo,
        cantidad_ciudades=cantidad_ciudades,
        ruta=resultado.ruta,
        segundos=segundos,
        nodos_explorados=resultado.nodos_explorados,
        nodos_podados=resultado.nodos_podados,
    )


def ejecutar_heuristica(ciudad_inicial: int) -> ResultadoHeuristicoGUI:
    """Ejecuta vecino mas cercano desde la capital elegida."""
    problema = crear_problema(len(CAPITALES))
    inicio = perf_counter()
    ruta = VecinoMasCercano(problema).resolver(ciudad_inicial)
    return ResultadoHeuristicoGUI(
        ciudad_inicial=ciudad_inicial,
        ruta=ruta,
        segundos=perf_counter() - inicio,
    )


def ejecutar_heuristica_todos() -> ResultadoHeuristicoTodosGUI:
    """Ejecuta la heurística desde cada una de las 24 capitales y halla el mejor recorrido."""
    problema = crear_problema(len(CAPITALES))
    inicio = perf_counter()
    heuristica = VecinoMasCercano(problema)
    resultados: list[tuple[int, str, int, RutaTSP]] = []
    for idx, capital in enumerate(CAPITALES):
        ruta = heuristica.resolver(idx)
        resultados.append((idx, capital, ruta.distancia_total, ruta))
    resultados.sort(key=lambda item: item[2])
    mejor_idx, mejor_capital, mejor_dist, mejor_ruta = resultados[0]
    segundos = perf_counter() - inicio
    return ResultadoHeuristicoTodosGUI(
        mejor_ciudad_inicial=mejor_idx,
        ruta=mejor_ruta,
        segundos=segundos,
        ranking=tuple((cap, dist) for _, cap, dist, _ in resultados),
    )


def ejecutar_genetico(
    ciudad_inicial: int,
    cantidad_cromosomas: int,
    cantidad_ciclos: int,
    frecuencia_crossover: float,
    frecuencia_mutacion: float,
) -> ResultadoGeneticoGUI:
    """Ejecuta el algoritmo genético con los parámetros seleccionados."""
    problema = crear_problema(len(CAPITALES))
    configuracion = ConfiguracionGenetica(
        cantidad_cromosomas=cantidad_cromosomas,
        cantidad_ciclos=cantidad_ciclos,
        frecuencia_crossover=frecuencia_crossover,
        frecuencia_mutacion=frecuencia_mutacion,
    )
    inicio = perf_counter()
    resultado = AlgoritmoGeneticoTSP(
        problema,
        configuracion,
        ciudad_inicial=ciudad_inicial,
    ).resolver()
    return ResultadoGeneticoGUI(
        ciudad_inicial=ciudad_inicial,
        ruta=resultado.ruta,
        segundos=perf_counter() - inicio,
        cantidad_cromosomas=cantidad_cromosomas,
        cantidad_ciclos=cantidad_ciclos,
        frecuencia_crossover=frecuencia_crossover,
        frecuencia_mutacion=frecuencia_mutacion,
    )


class AplicacionTSP:
    """Ventana principal y navegación de la aplicación del TP3."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("TP3 - Problema del Viajante")
        self.root.geometry("820x620")
        self.root.minsize(700, 500)
        self.resultados: queue.Queue[tuple[str, object]] = queue.Queue()
        self.zoom_2a = 1.0
        self._crear_variables()
        self._crear_estilos()
        self._crear_interfaz()

    def _crear_variables(self) -> None:
        self.cantidad_ciudades = tk.IntVar(value=10)
        self.algoritmo = tk.StringVar(value="Branch and Bound secuencial")
        self.cantidad_procesos = tk.IntVar(value=2)
        self.ciudad_inicial_heuristica = tk.StringVar(value=CAPITALES[0])
        self.ciudad_inicial_genetico = tk.StringVar(value=CAPITALES[0])
        self.cantidad_cromosomas = tk.IntVar(value=50)
        self.cantidad_ciclos = tk.IntVar(value=200)
        self.frecuencia_crossover = tk.DoubleVar(value=0.90)
        self.frecuencia_mutacion = tk.DoubleVar(value=0.10)
        self.estado = tk.StringVar(value="Listo para ejecutar el ejercicio 1.")

    def _crear_estilos(self) -> None:
        estilo = ttk.Style()
        try:
            estilo.theme_use("vista")
        except tk.TclError:
            pass
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 18, "bold"))
        estilo.configure("Subtitulo.TLabel", font=("Segoe UI", 11))
        estilo.configure("Resultado.TLabel", font=("Consolas", 10))

    def _crear_interfaz(self) -> None:
        contenedor = ttk.Frame(self.root, padding=20)
        contenedor.pack(fill="both", expand=True)

        encabezado = ttk.Frame(contenedor)
        encabezado.pack(fill="x", pady=(0, 18))
        ttk.Label(
            encabezado,
            text="Problema del Viajante",
            style="Titulo.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            encabezado,
            text="Resolución exacta de rutas entre capitales argentinas",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        self.pestanas = ttk.Notebook(contenedor)
        self.pestanas.pack(fill="both", expand=True)
        self.pestana_inicio = ttk.Frame(self.pestanas, padding=24)
        self.pestana_ejercicio_1 = ttk.Frame(self.pestanas, padding=20)
        self.pestana_ejercicio_2a = ttk.Frame(self.pestanas, padding=20)
        self.pestana_ejercicio_2b = ttk.Frame(self.pestanas, padding=20)
        self.pestana_ejercicio_2c = ttk.Frame(self.pestanas, padding=20)
        self.pestanas.add(self.pestana_inicio, text="Inicio")
        self.pestanas.add(self.pestana_ejercicio_1, text="Ejercicio 1")
        self.pestanas.add(self.pestana_ejercicio_2a, text="Ejercicio 2.a")
        self.pestanas.add(self.pestana_ejercicio_2b, text="Ejercicio 2.b")
        self.pestanas.add(self.pestana_ejercicio_2c, text="Ejercicio 2.c")
        self._crear_inicio()
        self._crear_ejercicio_1()
        self._crear_ejercicio_2a()
        self._crear_ejercicio_2b()
        self._crear_ejercicio_2c()

        ttk.Label(contenedor, textvariable=self.estado).pack(anchor="w", pady=(12, 0))

    def _crear_inicio(self) -> None:
        marco = ttk.Frame(self.pestana_inicio)
        marco.pack(expand=True)
        ttk.Label(
            marco,
            text="Ejercicios disponibles",
            style="Titulo.TLabel",
        ).pack(pady=(30, 10))
        ttk.Label(
            marco,
            text="Seleccione un ejercicio para comenzar.",
            style="Subtitulo.TLabel",
        ).pack(pady=(0, 24))
        ttk.Button(
            marco,
            text="Ejercicio 1 - Branch and Bound",
            command=self.mostrar_ejercicio_1,
        ).pack(ipadx=18, ipady=8)
        ttk.Button(
            marco,
            text="Ejercicio 2.a - Vecino más cercano",
            command=self.mostrar_ejercicio_2a,
        ).pack(ipadx=18, ipady=8, pady=(10, 0))
        ttk.Button(
            marco,
            text="Ejercicio 2.b - Mejor origen heurístico",
            command=self.mostrar_ejercicio_2b,
        ).pack(ipadx=18, ipady=8, pady=(10, 0))
        ttk.Button(
            marco,
            text="Ejercicio 2.c - Algoritmo genético",
            command=self.mostrar_ejercicio_2c,
        ).pack(ipadx=18, ipady=8, pady=(10, 0))

    def _crear_ejercicio_1(self) -> None:
        self.pestana_ejercicio_1.columnconfigure(1, weight=1)
        self.pestana_ejercicio_1.rowconfigure(5, weight=1)

        ttk.Label(
            self.pestana_ejercicio_1,
            text="Resolver ejercicio 1",
            style="Titulo.TLabel",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 18))

        ttk.Label(
            self.pestana_ejercicio_1,
            text="Cantidad de ciudades:",
        ).grid(row=1, column=0, sticky="w", pady=6)
        ciudades = ttk.Spinbox(
            self.pestana_ejercicio_1,
            from_=1,
            to=len(CAPITALES),
            textvariable=self.cantidad_ciudades,
            width=8,
        )
        ciudades.grid(row=1, column=1, sticky="w", padx=(12, 0), pady=6)

        ttk.Label(
            self.pestana_ejercicio_1,
            text="Algoritmo:",
        ).grid(row=2, column=0, sticky="w", pady=6)
        algoritmos = ttk.Combobox(
            self.pestana_ejercicio_1,
            textvariable=self.algoritmo,
            values=(
                "Branch and Bound secuencial",
                "Branch and Bound paralelo",
            ),
            state="readonly",
            width=32,
        )
        algoritmos.grid(row=2, column=1, sticky="w", padx=(12, 0), pady=6)

        ttk.Label(
            self.pestana_ejercicio_1,
            text="Procesos (paralelo):",
        ).grid(row=3, column=0, sticky="w", pady=6)
        procesos = ttk.Spinbox(
            self.pestana_ejercicio_1,
            from_=1,
            to=16,
            textvariable=self.cantidad_procesos,
            width=8,
        )
        procesos.grid(row=3, column=1, sticky="w", padx=(12, 0), pady=6)

        self.boton_resolver = ttk.Button(
            self.pestana_ejercicio_1,
            text="Resolver",
            command=self.resolver_ejercicio_1,
        )
        self.boton_resolver.grid(row=1, column=2, rowspan=3, padx=(24, 0), ipadx=18, ipady=8)

        self.progreso_1 = ttk.Progressbar(self.pestana_ejercicio_1, mode="indeterminate")

        self.salida = tk.Text(
            self.pestana_ejercicio_1,
            height=18,
            wrap="word",
            state="disabled",
            font=("Consolas", 10),
        )
        self.salida.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(16, 0))

    def mostrar_ejercicio_1(self) -> None:
        self.pestanas.select(self.pestana_ejercicio_1)

    def mostrar_ejercicio_2a(self) -> None:
        self.pestanas.select(self.pestana_ejercicio_2a)

    def mostrar_ejercicio_2b(self) -> None:
        self.pestanas.select(self.pestana_ejercicio_2b)

    def mostrar_ejercicio_2c(self) -> None:
        self.pestanas.select(self.pestana_ejercicio_2c)

    def _crear_ejercicio_2a(self) -> None:
        self.pestana_ejercicio_2a.columnconfigure(0, weight=0, minsize=330)
        self.pestana_ejercicio_2a.columnconfigure(1, weight=1)
        self.pestana_ejercicio_2a.rowconfigure(0, weight=1)

        panel_izquierdo = tk.Frame(
            self.pestana_ejercicio_2a,
            borderwidth=1,
            relief="solid",
            background="#f7f9f8",
        )
        panel_izquierdo.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        panel_izquierdo.grid_columnconfigure(0, weight=1)
        panel_izquierdo.grid_rowconfigure(6, weight=1)

        ttk.Label(
            panel_izquierdo,
            text="Ejercicio 2.a",
            style="Titulo.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(20, 4))
        ttk.Label(
            panel_izquierdo,
            text="Vecino más cercano",
            style="Subtitulo.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 18))
        ttk.Label(
            panel_izquierdo,
            text="Ciudad de partida:",
        ).grid(row=2, column=0, sticky="w", padx=18, pady=(0, 6))
        ttk.Combobox(
            panel_izquierdo,
            textvariable=self.ciudad_inicial_heuristica,
            values=CAPITALES,
            state="readonly",
        ).grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 12))
        self.boton_resolver_2a = ttk.Button(
            panel_izquierdo,
            text="Resolver heurística",
            command=self.resolver_ejercicio_2a,
        )
        self.boton_resolver_2a.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 10))

        self.progreso_2a = ttk.Progressbar(panel_izquierdo, mode="indeterminate")

        self.salida_2a = tk.Text(
            panel_izquierdo,
            width=36,
            wrap="word",
            state="disabled",
            borderwidth=0,
            background="#f7f9f8",
            font=("Consolas", 9),
        )
        self.salida_2a.grid(row=6, column=0, sticky="nsew", padx=18, pady=(0, 18))

        visor = ttk.Frame(self.pestana_ejercicio_2a)
        visor.grid(row=0, column=1, sticky="nsew")
        visor.columnconfigure(0, weight=1)
        visor.rowconfigure(0, weight=1)
        self.mapa_2a = TkinterMapView(
            visor,
            corner_radius=0,
        )
        self.mapa_2a.grid(row=0, column=0, sticky="nsew")
        self.mapa_2a.bind("<MouseWheel>", self._actualizar_marcadores_despues_zoom)
        controles_mapa = ttk.Frame(visor)
        controles_mapa.grid(row=1, column=0, sticky="e", pady=(8, 0))
        ttk.Button(
            controles_mapa,
            text="-",
            width=3,
            command=self._alejar_mapa,
        ).pack(side="left", padx=2)
        ttk.Button(
            controles_mapa,
            text="100%",
            command=self._centrar_mapa,
        ).pack(side="left", padx=2)
        ttk.Button(
            controles_mapa,
            text="+",
            width=3,
            command=self._acercar_mapa,
        ).pack(side="left", padx=2)
        ttk.Button(
            controles_mapa,
            text="Guardar imagen",
            command=self._guardar_mapa,
        ).pack(side="left", padx=(10, 2))
        self._dibujar_mapa_base()

    def _crear_ejercicio_2b(self) -> None:
        self.pestana_ejercicio_2b.columnconfigure(0, weight=0, minsize=350)
        self.pestana_ejercicio_2b.columnconfigure(1, weight=1)
        self.pestana_ejercicio_2b.rowconfigure(0, weight=1)

        panel = tk.Frame(
            self.pestana_ejercicio_2b,
            borderwidth=1,
            relief="solid",
            background="#f7f9f8",
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(5, weight=1)

        ttk.Label(
            panel,
            text="Ejercicio 2.b",
            style="Titulo.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(20, 4))
        ttk.Label(
            panel,
            text="Recorrido mínimo (todos los orígenes)",
            style="Subtitulo.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 12))
        ttk.Label(
            panel,
            text="Evalúa la heurística partiendo desde cada una\nde las 24 capitales para hallar la mejor ruta.",
            wraplength=310,
        ).grid(row=2, column=0, sticky="w", padx=18, pady=(0, 14))

        self.boton_resolver_2b = ttk.Button(
            panel,
            text="Evaluar todas las capitales",
            command=self.resolver_ejercicio_2b,
        )
        self.boton_resolver_2b.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 10))

        self.progreso_2b = ttk.Progressbar(panel, mode="indeterminate")

        self.salida_2b = tk.Text(
            panel,
            width=38,
            wrap="word",
            state="disabled",
            borderwidth=0,
            background="#f7f9f8",
            font=("Consolas", 9),
        )
        self.salida_2b.grid(row=5, column=0, sticky="nsew", padx=18, pady=(0, 18))

        visor = ttk.Frame(self.pestana_ejercicio_2b)
        visor.grid(row=0, column=1, sticky="nsew")
        visor.columnconfigure(0, weight=1)
        visor.rowconfigure(0, weight=1)
        self.mapa_2b = TkinterMapView(visor, corner_radius=0)
        self.mapa_2b.grid(row=0, column=0, sticky="nsew")
        self.mapa_2b.set_position(-35.5, -64.5)
        self.mapa_2b.set_zoom(4)
        self._agregar_marcadores_en(self.mapa_2b)

    def _crear_ejercicio_2c(self) -> None:
        self.pestana_ejercicio_2c.columnconfigure(0, weight=0, minsize=350)
        self.pestana_ejercicio_2c.columnconfigure(1, weight=1)
        self.pestana_ejercicio_2c.rowconfigure(0, weight=1)

        panel = tk.Frame(
            self.pestana_ejercicio_2c,
            borderwidth=1,
            relief="solid",
            background="#f7f9f8",
        )
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 18))

        # Encabezado fijo
        encabezado = ttk.Frame(panel)
        encabezado.pack(fill="x", padx=18, pady=(16, 10))
        ttk.Label(encabezado, text="Ejercicio 2.c", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(encabezado, text="Algoritmo genético", style="Subtitulo.TLabel").pack(anchor="w", pady=(2, 0))

        # 1. Sub-frame del formulario de configuración
        self.frame_formulario_2c = ttk.Frame(panel)
        self.frame_formulario_2c.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        ttk.Label(self.frame_formulario_2c, text="Ciudad de partida:").pack(anchor="w", pady=(0, 2))
        ttk.Combobox(
            self.frame_formulario_2c,
            textvariable=self.ciudad_inicial_genetico,
            values=CAPITALES,
            state="readonly",
        ).pack(fill="x", pady=(0, 8))

        parametros = (
            ("Cantidad de cromosomas (N):", self.cantidad_cromosomas, 50, 500, 1),
            ("Cantidad de ciclos (M):", self.cantidad_ciclos, 1, 2000, 1),
            ("Frecuencia de crossover (0 a 1):", self.frecuencia_crossover, 0.0, 1.0, 0.01),
            ("Frecuencia de mutación (0 a 1):", self.frecuencia_mutacion, 0.0, 1.0, 0.01),
        )

        for texto, variable, minimo, maximo, inc in parametros:
            ttk.Label(self.frame_formulario_2c, text=texto).pack(anchor="w", pady=(3, 1))
            ttk.Spinbox(
                self.frame_formulario_2c,
                from_=minimo,
                to=maximo,
                increment=inc,
                textvariable=variable,
            ).pack(fill="x", pady=(0, 6))

        self.boton_resolver_2c = ttk.Button(
            self.frame_formulario_2c,
            text="Resolver algoritmo genético",
            command=self.resolver_ejercicio_2c,
        )
        self.boton_resolver_2c.pack(fill="x", pady=(12, 0))

        self.progreso_2c = ttk.Progressbar(self.frame_formulario_2c, mode="indeterminate")

        # 2. Sub-frame del resultado (inicialmente oculto)
        self.frame_resultado_2c = ttk.Frame(panel)

        ttk.Label(
            self.frame_resultado_2c,
            text="Resultado de la ejecución:",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        self.salida_2c = tk.Text(
            self.frame_resultado_2c,
            width=36,
            height=16,
            wrap="word",
            state="disabled",
            borderwidth=1,
            relief="solid",
            background="#ffffff",
            font=("Consolas", 9),
        )
        self.salida_2c.pack(fill="both", expand=True, pady=(0, 12))

        self.boton_reintentar_2c = ttk.Button(
            self.frame_resultado_2c,
            text="Volver a configurar / Reintentar",
            command=self._mostrar_formulario_2c,
        )
        self.boton_reintentar_2c.pack(fill="x", pady=(0, 6))

        # Visor de mapa en la columna derecha
        visor = ttk.Frame(self.pestana_ejercicio_2c)
        visor.grid(row=0, column=1, sticky="nsew")
        visor.columnconfigure(0, weight=1)
        visor.rowconfigure(0, weight=1)
        self.mapa_2c = TkinterMapView(visor, corner_radius=0)
        self.mapa_2c.grid(row=0, column=0, sticky="nsew")
        self.mapa_2c.set_position(-35.5, -64.5)
        self.mapa_2c.set_zoom(4)
        self._agregar_marcadores_en(self.mapa_2c)

    def resolver_ejercicio_2a(self) -> None:
        ciudad = self.ciudad_inicial_heuristica.get()
        if ciudad not in CAPITALES:
            messagebox.showerror("Datos inválidos", "Seleccione una capital válida.")
            return
        self.boton_resolver_2a.configure(state="disabled")
        self.progreso_2a.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 10))
        self.progreso_2a.start(10)
        self.estado.set("Ejecutando la heurística del vecino más cercano...")
        self._escribir_salida_2a("Calculando ruta heurística...\n")
        threading.Thread(
            target=self._trabajar_2a,
            args=(CAPITALES.index(ciudad),),
            daemon=True,
        ).start()
        self.root.after(100, self._consultar_resultado_2a)

    def resolver_ejercicio_2c(self) -> None:
        try:
            cantidad = self.cantidad_cromosomas.get()
            ciclos = self.cantidad_ciclos.get()
            crossover = self.frecuencia_crossover.get()
            mutacion = self.frecuencia_mutacion.get()
            ConfiguracionGenetica(cantidad, ciclos, crossover, mutacion)
        except (tk.TclError, ValueError) as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        self.boton_resolver_2c.configure(state="disabled")
        self.progreso_2c.pack(fill="x", pady=(10, 0))
        self.progreso_2c.start(10)
        self.estado.set("Ejecutando el algoritmo genético...")
        self._escribir_salida_2c("Calculando resultado...\n")
        parametros = (
            CAPITALES.index(self.ciudad_inicial_genetico.get()),
            cantidad,
            ciclos,
            crossover,
            mutacion,
        )
        threading.Thread(target=self._trabajar_2c, args=parametros, daemon=True).start()
        self.root.after(100, self._consultar_resultado_2c)

    def _trabajar_2c(self, *parametros: object) -> None:
        try:
            resultado = ejecutar_genetico(*parametros)
            self.resultados.put(("genetico", resultado))
        except Exception as error:
            self.resultados.put(("error_2c", error))

    def _consultar_resultado_2c(self) -> None:
        try:
            tipo, valor = self.resultados.get_nowait()
        except queue.Empty:
            self.root.after(100, self._consultar_resultado_2c)
            return
        self.progreso_2c.stop()
        self.progreso_2c.pack_forget()
        self.boton_resolver_2c.configure(state="normal")
        if tipo == "error_2c":
            self.estado.set("El algoritmo genético terminó con un error.")
            messagebox.showerror("Error de ejecución", str(valor))
            return
        if tipo != "genetico" or not isinstance(valor, ResultadoGeneticoGUI):
            self.resultados.put((tipo, valor))
            self.root.after(100, self._consultar_resultado_2c)
            return
        self.estado.set("Ejecución genética finalizada.")
        self._mostrar_resultado_2c(valor)

    def _mostrar_resultado_2c(self, resultado: ResultadoGeneticoGUI) -> None:
        self.frame_formulario_2c.pack_forget()
        self.frame_resultado_2c.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        problema = crear_problema(len(CAPITALES))
        ciudades_nombres = resultado.ruta.nombres(problema)
        nombres = "\n".join(
            f"{indice + 1:2}. {nombre}" + (" (Regreso al inicio)" if indice == len(ciudades_nombres) - 1 else "")
            for indice, nombre in enumerate(ciudades_nombres)
        )
        texto = "\n".join((
            "RESUMEN",
            "Algoritmo: Algoritmo genético",
            f"Ciudad de partida: {CAPITALES[resultado.ciudad_inicial]}",
            f"Cromosomas: {resultado.cantidad_cromosomas}",
            f"Ciclos: {resultado.cantidad_ciclos}",
            f"Crossover cíclico: {resultado.frecuencia_crossover:.0%}",
            f"Mutación: {resultado.frecuencia_mutacion:.0%}",
            f"Distancia total: {resultado.ruta.distancia_total} km",
            f"Tiempo de ejecución: {resultado.segundos:.6f} s",
            "",
            "MEJOR RECORRIDO",
            nombres,
        ))
        self._escribir_salida_2c(texto)
        self._dibujar_ruta_en(self.mapa_2c, resultado.ruta, problema)

    def _mostrar_formulario_2c(self) -> None:
        self.frame_resultado_2c.pack_forget()
        self.frame_formulario_2c.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        self.boton_resolver_2c.configure(state="normal")

    def _escribir_salida_2c(self, texto: str) -> None:
        self.salida_2c.configure(state="normal")
        self.salida_2c.delete("1.0", tk.END)
        self.salida_2c.insert(tk.END, texto)
        self.salida_2c.configure(state="disabled")

    def _trabajar_2a(self, ciudad_inicial: int) -> None:
        try:
            resultado = ejecutar_heuristica(ciudad_inicial)
            self.resultados.put(("heuristica", resultado))
        except Exception as error:
            self.resultados.put(("error_2a", error))

    def _consultar_resultado_2a(self) -> None:
        try:
            tipo, valor = self.resultados.get_nowait()
        except queue.Empty:
            self.root.after(100, self._consultar_resultado_2a)
            return
        self.progreso_2a.stop()
        self.progreso_2a.grid_remove()
        self.boton_resolver_2a.configure(state="normal")
        if tipo == "error_2a":
            self.estado.set("La ejecución heurística terminó con un error.")
            messagebox.showerror("Error de ejecución", str(valor))
            return
        if tipo != "heuristica" or not isinstance(valor, ResultadoHeuristicoGUI):
            self.resultados.put((tipo, valor))
            self.root.after(100, self._consultar_resultado_2a)
            return
        self.estado.set("Ejecución heurística finalizada.")
        self._mostrar_resultado_2a(valor)

    def _mostrar_resultado_2a(self, resultado: ResultadoHeuristicoGUI) -> None:
        problema = crear_problema(len(CAPITALES))
        ciudades_nombres = resultado.ruta.nombres(problema)
        nombres = "\n".join(
            f"{indice + 1:2}. {nombre}" + (" (Regreso al inicio)" if indice == len(ciudades_nombres) - 1 else "")
            for indice, nombre in enumerate(ciudades_nombres)
        )
        texto = "\n".join(
            (
                "RESUMEN",
                "Algoritmo: Vecino más cercano",
                f"Ciudad de partida: {CAPITALES[resultado.ciudad_inicial]}",
                f"Distancia total: {resultado.ruta.distancia_total} km",
                f"Tiempo de ejecución: {resultado.segundos:.6f} s",
                "",
                "RECORRIDO COMPLETO",
                nombres,
            )
        )
        self._escribir_salida_2a(texto)
        self._dibujar_ruta(resultado.ruta, problema)

    def _escribir_salida_2a(self, texto: str) -> None:
        self.salida_2a.configure(state="normal")
        self.salida_2a.delete("1.0", tk.END)
        self.salida_2a.insert(tk.END, texto)
        self.salida_2a.configure(state="disabled")

    def resolver_ejercicio_2b(self) -> None:
        self.boton_resolver_2b.configure(state="disabled")
        self.progreso_2b.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 10))
        self.progreso_2b.start(10)
        self.estado.set("Evaluando vecino más cercano en las 24 capitales...")
        self._escribir_salida_2b("Calculando mejor origen heurístico...\n")
        threading.Thread(target=self._trabajar_2b, daemon=True).start()
        self.root.after(100, self._consultar_resultado_2b)

    def _trabajar_2b(self) -> None:
        try:
            resultado = ejecutar_heuristica_todos()
            self.resultados.put(("heuristica_todos", resultado))
        except Exception as error:
            self.resultados.put(("error_2b", error))

    def _consultar_resultado_2b(self) -> None:
        try:
            tipo, valor = self.resultados.get_nowait()
        except queue.Empty:
            self.root.after(100, self._consultar_resultado_2b)
            return
        self.progreso_2b.stop()
        self.progreso_2b.grid_remove()
        self.boton_resolver_2b.configure(state="normal")
        if tipo == "error_2b":
            self.estado.set("La evaluación terminó con un error.")
            messagebox.showerror("Error de ejecución", str(valor))
            return
        if tipo != "heuristica_todos" or not isinstance(valor, ResultadoHeuristicoTodosGUI):
            self.resultados.put((tipo, valor))
            self.root.after(100, self._consultar_resultado_2b)
            return
        self.estado.set("Evaluación de todas las capitales completada.")
        self._mostrar_resultado_2b(valor)

    def _mostrar_resultado_2b(self, resultado: ResultadoHeuristicoTodosGUI) -> None:
        problema = crear_problema(len(CAPITALES))
        ciudades_nombres = resultado.ruta.nombres(problema)
        nombres = "\n".join(
            f"{indice + 1:2}. {nombre}" + (" (Regreso al inicio)" if indice == len(ciudades_nombres) - 1 else "")
            for indice, nombre in enumerate(ciudades_nombres)
        )
        ranking_texto = "\n".join(
            f"  {idx + 1:2}. {cap:<28} {dist:>6,d} km"
            for idx, (cap, dist) in enumerate(resultado.ranking[:10])
        )
        texto = "\n".join(
            (
                "RESUMEN",
                f"Mejor partida: {CAPITALES[resultado.mejor_ciudad_inicial]}",
                f"Distancia mínima: {resultado.ruta.distancia_total} km",
                f"Tiempo de cómputo: {resultado.segundos:.6f} s",
                "",
                "TOP 10 CAPITALES DE INICIO",
                ranking_texto,
                "",
                "RECORRIDO COMPLETO",
                nombres,
            )
        )
        self._escribir_salida_2b(texto)
        self._dibujar_ruta_en(self.mapa_2b, resultado.ruta, problema)

    def _escribir_salida_2b(self, texto: str) -> None:
        self.salida_2b.configure(state="normal")
        self.salida_2b.delete("1.0", tk.END)
        self.salida_2b.insert(tk.END, texto)
        self.salida_2b.configure(state="disabled")

    def _dibujar_mapa_base(self) -> None:
        self.mapa_2a.set_position(-35.5, -64.5)
        self.mapa_2a.set_zoom(4)
        self._limpiar_capas_mapa()
        self._agregar_marcadores()

    def _limpiar_capas_mapa(self) -> None:
        self.mapa_2a.delete_all_marker()
        self.mapa_2a.delete_all_path()

    def _agregar_marcadores(self) -> None:
        self._agregar_marcadores_en(self.mapa_2a)

    def _agregar_marcadores_en(self, mapa: TkinterMapView) -> None:
        if not hasattr(self, "icono_capital"):
            self.icono_capital = tk.PhotoImage(width=7, height=7)
            self.icono_capital.put("#2c3e50", to=(0, 0, 7, 7))
            self.icono_inicio = tk.PhotoImage(width=11, height=11)
            self.icono_inicio.put("#27ae60", to=(0, 0, 11, 11))
        mostrar_nombres = mapa.zoom >= 6
        for nombre in CAPITALES:
            longitud, latitud = COORDENADAS_CAPITALES[nombre]
            mapa.set_marker(
                latitud,
                longitud,
                text=nombre if mostrar_nombres else None,
                icon=self.icono_capital,
                icon_anchor="center",
                font=("Segoe UI", 9, "bold"),
            )

    def _centrar_mapa(self) -> None:
        self.mapa_2a.set_position(-35.5, -64.5)
        self.mapa_2a.set_zoom(4)

    def _acercar_mapa(self) -> None:
        self.mapa_2a.set_zoom(self.mapa_2a.zoom + 1)
        self._actualizar_marcadores()

    def _alejar_mapa(self) -> None:
        self.mapa_2a.set_zoom(self.mapa_2a.zoom - 1)
        self._actualizar_marcadores()

    def _actualizar_marcadores_despues_zoom(self, _evento: tk.Event) -> None:
        self.root.after(100, self._actualizar_marcadores)

    def _actualizar_marcadores(self) -> None:
        ruta = getattr(self, "ruta_mapa_2a", None)
        self._limpiar_capas_mapa()
        self._agregar_marcadores()
        if ruta is not None:
            posiciones = [
                (
                    COORDENADAS_CAPITALES[self.problema_mapa_2a.nombre_ciudad(indice)][1],
                    COORDENADAS_CAPITALES[self.problema_mapa_2a.nombre_ciudad(indice)][0],
                )
                for indice in ruta.recorrido
            ]
            self.mapa_2a.set_path(posiciones, color="#1a5276", width=3)
            inicio = posiciones[0]
            nombre_inicio = self.problema_mapa_2a.nombre_ciudad(ruta.recorrido[0])
            self.mapa_2a.set_marker(
                inicio[0],
                inicio[1],
                text=f"Partida / Llegada: {nombre_inicio}",
                icon=self.icono_inicio,
                icon_anchor="center",
                font=("Segoe UI", 9, "bold"),
            )

    def _guardar_mapa(self) -> None:
        if not hasattr(self, "ruta_mapa_2a"):
            messagebox.showinfo("Mapa", "Primero debe resolver el ejercicio 2.a.")
            return
        messagebox.showinfo(
            "Mapa interactivo",
            "El mapa es interactivo: puede hacer zoom y desplazarse con el mouse.\n"
            "Para conservarlo, use una captura de pantalla del visor.",
        )

    def _dibujar_ruta(self, ruta: RutaTSP, problema: ProblemaTSP) -> None:
        self.ruta_mapa_2a = ruta
        self.problema_mapa_2a = problema
        self._dibujar_ruta_en(self.mapa_2a, ruta, problema)

    def _dibujar_ruta_en(self, mapa: TkinterMapView, ruta: RutaTSP, problema: ProblemaTSP) -> None:
        mapa.delete_all_marker()
        mapa.delete_all_path()
        self._agregar_marcadores_en(mapa)
        posiciones = [
            (
                COORDENADAS_CAPITALES[problema.nombre_ciudad(indice)][1],
                COORDENADAS_CAPITALES[problema.nombre_ciudad(indice)][0],
            )
            for indice in ruta.recorrido
        ]
        mapa.set_path(posiciones, color="#1a5276", width=3)
        inicio = posiciones[0]
        nombre_inicio = problema.nombre_ciudad(ruta.recorrido[0])
        mapa.set_marker(
            inicio[0],
            inicio[1],
            text=f"Partida / Llegada: {nombre_inicio}",
            icon=self.icono_inicio,
            icon_anchor="center",
            font=("Segoe UI", 9, "bold"),
        )
        lats = [p[0] for p in posiciones]
        lons = [p[1] for p in posiciones]
        margen = 0.8
        try:
            mapa.fit_bounding_box(
                (max(lats) + margen, min(lons) - margen),
                (min(lats) - margen, max(lons) + margen),
            )
        except Exception:
            mapa.set_position(sum(lats) / len(lats), sum(lons) / len(lons))

    def resolver_ejercicio_1(self) -> None:
        try:
            cantidad = self.cantidad_ciudades.get()
            procesos = self.cantidad_procesos.get()
            if not 1 <= cantidad <= len(CAPITALES):
                raise ValueError(f"La cantidad debe estar entre 1 y {len(CAPITALES)}.")
            if procesos < 1:
                raise ValueError("La cantidad de procesos debe ser positiva.")
        except (tk.TclError, ValueError) as error:
            messagebox.showerror("Datos inválidos", str(error))
            return

        self.boton_resolver.configure(state="disabled")
        self.progreso_1.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        self.progreso_1.start(10)
        self.estado.set("Resolviendo...")
        self._escribir_salida("Calculando resultado...\n")
        parametros = self.algoritmo.get(), cantidad, procesos
        threading.Thread(
            target=self._trabajar,
            args=parametros,
            daemon=True,
        ).start()
        self.root.after(100, self._consultar_resultado)

    def _trabajar(
        self,
        algoritmo: str,
        cantidad: int,
        procesos: int,
    ) -> None:
        try:
            resultado = ejecutar_algoritmo(algoritmo, cantidad, procesos)
            self.resultados.put(("ok", resultado))
        except Exception as error:
            self.resultados.put(("error", error))

    def _consultar_resultado(self) -> None:
        try:
            tipo, valor = self.resultados.get_nowait()
        except queue.Empty:
            self.root.after(100, self._consultar_resultado)
            return

        self.progreso_1.stop()
        self.progreso_1.grid_remove()
        self.boton_resolver.configure(state="normal")
        if tipo == "error":
            self.estado.set("La ejecución terminó con un error.")
            messagebox.showerror("Error de ejecución", str(valor))
            return

        resultado = valor
        if not isinstance(resultado, ResultadoGUI):
            raise TypeError("Resultado inesperado del algoritmo.")
        self.estado.set("Ejecución finalizada.")
        self._mostrar_resultado(resultado)

    def _mostrar_resultado(self, resultado: ResultadoGUI) -> None:
        problema = crear_problema(resultado.cantidad_ciudades)
        ciudades_nombres = resultado.ruta.nombres(problema)
        nombres = "\n".join(
            f"{indice + 1:2}. {nombre}" + (" (Regreso al inicio)" if indice == len(ciudades_nombres) - 1 else "")
            for indice, nombre in enumerate(ciudades_nombres)
        )
        salida = "\n".join(
            (
                "RESUMEN",
                f"Algoritmo: {resultado.algoritmo}",
                f"Ciudades: {resultado.cantidad_ciudades}",
                f"Distancia total: {resultado.ruta.distancia_total} km",
                f"Tiempo de ejecución: {resultado.segundos:.6f} s",
                f"Nodos explorados: {resultado.nodos_explorados}",
                f"Nodos podados: {resultado.nodos_podados}",
                "",
                "RECORRIDO COMPLETO",
                nombres,
            )
        )
        self._escribir_salida(salida)

    def _escribir_salida(self, texto: str) -> None:
        self.salida.configure(state="normal")
        self.salida.delete("1.0", tk.END)
        self.salida.insert(tk.END, texto)
        self.salida.configure(state="disabled")


def lanzar_gui() -> None:
    """Inicia la aplicación Tkinter."""
    root = tk.Tk()
    AplicacionTSP(root)
    root.mainloop()


if __name__ == "__main__":
    lanzar_gui()