"""Interfaz Tkinter para ejecutar los ejercicios del TP3."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
import queue
from pathlib import Path
import sys
import threading
from time import perf_counter
import tkinter as tk
from tkinter import messagebox, ttk

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
from interfaz.componentes import (
    ItemNavegacion,
    PanelMapa,
    SliderValor,
    TablaRecorrido,
    Tarjeta,
    TarjetaAccion,
    TarjetaMetrica,
    crear_control_segmentado,
    formatear_entero,
)
from interfaz.tema import Fuentes, Paleta, aplicar_barra_titulo_oscura, configurar_estilos


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
    """Datos de la ruta heuristica para la pestaña 2.a."""

    ciudad_inicial: int
    ruta: RutaTSP
    segundos: float


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


def ejecutar_genetico(
    ciudad_inicial: int,
    cantidad_cromosomas: int,
    cantidad_ciclos: int,
    frecuencia_crossover: float,
    frecuencia_mutacion: float,
    semilla: int | None,
) -> ResultadoGeneticoGUI:
    """Ejecuta el algoritmo genetico con los parametros seleccionados."""
    problema = crear_problema(len(CAPITALES))
    configuracion = ConfiguracionGenetica(
        cantidad_cromosomas=cantidad_cromosomas,
        cantidad_ciclos=cantidad_ciclos,
        frecuencia_crossover=frecuencia_crossover,
        frecuencia_mutacion=frecuencia_mutacion,
        semilla=semilla,
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


# ---------------------------------------------------------------------------
# Utilidades de presentacion
# ---------------------------------------------------------------------------

def formatear_segundos(segundos: float) -> tuple[str, str]:
    """Devuelve (valor, unidad) legible para un tiempo de ejecucion."""
    if segundos < 1e-3:
        return f"{segundos * 1e6:.0f}", "µs"
    if segundos < 1:
        return f"{segundos * 1e3:.1f}", "ms"
    if segundos < 120:
        return f"{segundos:.2f}", "s"
    return f"{segundos / 60:.1f}", "min"


def tramos_de(ruta: RutaTSP, problema: ProblemaTSP) -> list[int]:
    return [
        problema.distancia(origen, destino)
        for origen, destino in zip(ruta.recorrido, ruta.recorrido[1:])
    ]


def texto_recorrido(ruta: RutaTSP, problema: ProblemaTSP) -> str:
    return "\n".join(
        f"{indice + 1:2}. {nombre}" for indice, nombre in enumerate(ruta.nombres(problema))
    )


@dataclass(frozen=True)
class EspecMetrica:
    clave: str
    titulo: str
    unidad: str
    color: str


# ---------------------------------------------------------------------------
# Vista generica de un ejercicio
# ---------------------------------------------------------------------------

class VistaEjercicio(ttk.Frame):
    """Layout comun: parametros a la izquierda, metricas, mapa y recorrido."""

    def __init__(
        self,
        master: tk.Misc,
        insignia: str,
        titulo: str,
        subtitulo: str,
        etiqueta: str,
        color: str,
        metricas: Sequence[EspecMetrica],
        texto_boton: str,
        comando: Callable[[], None],
    ) -> None:
        super().__init__(master, padding=(32, 26, 32, 18))
        self.comando = comando
        self.resumen = ""
        self.ultima_distancia: int | None = None
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # Encabezado
        encabezado = ttk.Frame(self)
        encabezado.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        fila = ttk.Frame(encabezado)
        fila.pack(fill="x")
        tk.Label(
            fila, text=insignia, background=color, foreground=Paleta.FONDO,
            font=(Fuentes.MONO, 11, "bold"), width=4, pady=4,
        ).pack(side="left")
        ttk.Label(fila, text=titulo, style="H1.TLabel").pack(side="left", padx=(14, 0))
        tk.Label(
            fila, text=etiqueta, background=Paleta.SUPERFICIE_2, foreground=color,
            font=(Fuentes.BASE, 8, "bold"), padx=9, pady=3,
        ).pack(side="left", padx=(14, 0))
        ttk.Label(encabezado, text=subtitulo, style="Subtitulo.TLabel").pack(
            anchor="w", pady=(8, 0)
        )

        # Panel de parametros
        self.panel = Tarjeta(self, padding=20)
        self.panel.grid(row=1, column=0, sticky="nsw", padx=(0, 20))
        cuerpo = self.panel.cuerpo
        ttk.Label(cuerpo, text="Parámetros", style="TarjetaTitulo.TLabel").pack(anchor="w")
        ttk.Label(
            cuerpo, text="Configurá la ejecución y presioná resolver.",
            style="TarjetaAyuda.TLabel",
        ).pack(anchor="w", pady=(2, 14))
        self.campos = tk.Frame(cuerpo, background=Paleta.SUPERFICIE, width=280)
        self.campos.pack(fill="x")

        acciones = tk.Frame(cuerpo, background=Paleta.SUPERFICIE)
        acciones.pack(side="bottom", fill="x")
        self.boton = ttk.Button(
            acciones, text=f"▶  {texto_boton}", style="Acento.TButton", command=comando
        )
        self.boton.pack(fill="x")
        self.progreso = ttk.Progressbar(
            acciones, mode="indeterminate", style="Acento.Horizontal.TProgressbar"
        )
        self.texto_estado = ttk.Label(
            acciones, text="Listo · Ctrl+Enter para ejecutar", style="TarjetaAyuda.TLabel"
        )
        self.texto_estado.pack(anchor="w", pady=(10, 0))
        self.boton_copiar = ttk.Button(
            acciones, text="⧉  Copiar resumen", command=self._copiar, state="disabled"
        )
        self.boton_copiar.pack(fill="x", pady=(12, 0))

        # Zona de resultados
        derecha = ttk.Frame(self)
        derecha.grid(row=1, column=1, sticky="nsew")
        derecha.columnconfigure(0, weight=1)
        derecha.rowconfigure(1, weight=1)

        fila_metricas = ttk.Frame(derecha)
        fila_metricas.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        self.metricas: dict[str, TarjetaMetrica] = {}
        for columna, espec in enumerate(metricas):
            fila_metricas.columnconfigure(columna, weight=1, uniform="metricas")
            tarjeta = TarjetaMetrica(fila_metricas, espec.titulo, espec.unidad, espec.color)
            tarjeta.grid(
                row=0, column=columna, sticky="nsew",
                padx=(0 if columna == 0 else 8, 0),
            )
            self.metricas[espec.clave] = tarjeta

        divisor = ttk.Panedwindow(derecha, orient="horizontal")
        divisor.grid(row=1, column=0, sticky="nsew")
        self.mapa = PanelMapa(divisor)
        self.tabla = TablaRecorrido(divisor)
        divisor.add(self.mapa, weight=3)
        divisor.add(self.tabla, weight=1)

    # -- ayudas para construir el formulario ---------------------------------
    def agregar_campo(
        self,
        texto: str,
        fabrica: Callable[[tk.Misc], tk.Widget],
        ayuda: str | None = None,
    ) -> tk.Widget:
        contenedor = tk.Frame(self.campos, background=Paleta.SUPERFICIE)
        contenedor.pack(fill="x", pady=(0, 14))
        ttk.Label(contenedor, text=texto, style="TarjetaCampo.TLabel").pack(anchor="w")
        widget = fabrica(contenedor)
        widget.pack(fill="x", pady=(5, 0))
        if ayuda:
            ttk.Label(
                contenedor, text=ayuda, style="TarjetaAyuda.TLabel", wraplength=270,
                justify="left",
            ).pack(anchor="w", pady=(4, 0))
        return widget

    def agregar_widget(self, fabrica: Callable[[tk.Misc], tk.Widget]) -> tk.Widget:
        widget = fabrica(self.campos)
        widget.pack(fill="x", pady=(0, 14))
        return widget

    # -- estado ---------------------------------------------------------------
    def establecer_ocupado(self, ocupado: bool) -> None:
        if ocupado:
            self.boton.configure(state="disabled", text="⏳  Ejecutando…")
            self.progreso.pack(fill="x", pady=(10, 0), before=self.texto_estado)
            self.progreso.start(12)
        else:
            self.progreso.stop()
            self.progreso.pack_forget()
            self.boton.configure(state="normal", text=self._texto_boton_original())

    def _texto_boton_original(self) -> str:
        return getattr(self, "_texto_boton", None) or self.boton.cget("text")

    def guardar_texto_boton(self) -> None:
        self._texto_boton = self.boton.cget("text")

    def estado(self, texto: str) -> None:
        self.texto_estado.configure(text=texto)

    def mostrar_resultado(
        self,
        ruta: RutaTSP,
        problema: ProblemaTSP,
        valores: dict[str, tuple[str, str]],
        resumen: str,
    ) -> None:
        distancia = ruta.distancia_total
        for clave, (valor, detalle) in valores.items():
            self.metricas[clave].mostrar(valor, detalle)
        if "distancia" in self.metricas:
            detalle, color = "Primera ejecución", None
            if self.ultima_distancia is not None:
                delta = distancia - self.ultima_distancia
                if delta < 0:
                    detalle, color = f"▼ {formatear_entero(-delta)} km vs. anterior", Paleta.TURQUESA
                elif delta > 0:
                    detalle, color = f"▲ {formatear_entero(delta)} km vs. anterior", Paleta.ROJO
                else:
                    detalle = "= igual a la ejecución anterior"
            self.metricas["distancia"].mostrar(formatear_entero(distancia), detalle, color)
        self.ultima_distancia = distancia
        self.mapa.mostrar_ruta(ruta, problema)
        self.tabla.mostrar(ruta, problema)
        self.resumen = resumen
        self.boton_copiar.configure(state="normal")

    def _copiar(self) -> None:
        if not self.resumen:
            return
        self.clipboard_clear()
        self.clipboard_append(self.resumen)
        self.boton_copiar.configure(text="✓  Copiado al portapapeles")
        self.after(1600, lambda: self.boton_copiar.configure(text="⧉  Copiar resumen"))


# ---------------------------------------------------------------------------
# Aplicacion principal
# ---------------------------------------------------------------------------

class AplicacionTSP:
    """Ventana principal y navegacion de la aplicacion del TP3."""

    ALGORITMO_SECUENCIAL = "Branch and Bound secuencial"
    ALGORITMO_PARALELO = "Branch and Bound paralelo"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("TP3 · Problema del Viajante")
        self._configurar_ventana()
        configurar_estilos(root)
        self._crear_variables()
        self._crear_interfaz()
        self._crear_atajos()
        self.mostrar("inicio")
        aplicar_barra_titulo_oscura(root)

    # -- configuracion --------------------------------------------------------
    def _configurar_ventana(self) -> None:
        ancho, alto = 1400, 880
        x = max((self.root.winfo_screenwidth() - ancho) // 2, 0)
        y = max((self.root.winfo_screenheight() - alto) // 2 - 30, 0)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.root.minsize(1180, 740)

    def _crear_variables(self) -> None:
        self.cantidad_ciudades = tk.IntVar(value=min(12, len(CAPITALES)))
        self.algoritmo = tk.StringVar(value=self.ALGORITMO_SECUENCIAL)
        self.cantidad_procesos = tk.IntVar(value=2)
        self.ciudad_inicial_heuristica = tk.StringVar(value=CAPITALES[0])
        self.ciudad_inicial_genetico = tk.StringVar(value=CAPITALES[0])
        self.cantidad_cromosomas = tk.IntVar(value=50)
        self.cantidad_ciclos = tk.IntVar(value=200)
        self.frecuencia_crossover = tk.DoubleVar(value=0.90)
        self.frecuencia_mutacion = tk.DoubleVar(value=0.10)
        self.semilla_genetica = tk.StringVar(value="42")
        self.estado = tk.StringVar(value="Listo.")

    def _crear_atajos(self) -> None:
        self.root.bind_all("<Control-Return>", lambda _e: self._ejecutar_actual())
        self.root.bind_all("<F5>", lambda _e: self._ejecutar_actual())
        for numero, clave in enumerate(("inicio", "ej1", "ej2a", "ej2c"), start=1):
            self.root.bind_all(f"<Control-Key-{numero}>", lambda _e, c=clave: self.mostrar(c))

    # -- estructura -----------------------------------------------------------
    def _crear_interfaz(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self._crear_barra_lateral()

        contenido = ttk.Frame(self.root)
        contenido.grid(row=0, column=1, sticky="nsew")
        contenido.columnconfigure(0, weight=1)
        contenido.rowconfigure(0, weight=1)

        self.paginas: dict[str, ttk.Frame] = {
            "inicio": self._crear_inicio(contenido),
            "ej1": self._crear_ejercicio_1(contenido),
            "ej2a": self._crear_ejercicio_2a(contenido),
            "ej2c": self._crear_ejercicio_2c(contenido),
        }
        for pagina in self.paginas.values():
            pagina.grid(row=0, column=0, sticky="nsew")

        self._crear_barra_estado(contenido)

    def _crear_barra_lateral(self) -> None:
        barra = tk.Frame(self.root, background=Paleta.BARRA_LATERAL, width=260)
        barra.grid(row=0, column=0, sticky="ns")
        barra.grid_propagate(False)
        barra.pack_propagate(False)
        tk.Frame(self.root, background=Paleta.BORDE, width=1).grid(
            row=0, column=0, sticky="nse"
        )

        marca = tk.Frame(barra, background=Paleta.BARRA_LATERAL)
        marca.pack(fill="x", padx=20, pady=(24, 28))
        logo = tk.Canvas(
            marca, width=40, height=40, background=Paleta.BARRA_LATERAL,
            highlightthickness=0,
        )
        logo.pack(side="left")
        logo.create_rectangle(0, 0, 40, 40, fill=Paleta.ACENTO, outline="")
        puntos = ((10, 28), (17, 12), (27, 18), (31, 30), (10, 28))
        logo.create_line(*[c for p in puntos for c in p], fill="#ffffff", width=2)
        for px, py in puntos[:-1]:
            logo.create_oval(px - 3, py - 3, px + 3, py + 3, fill=Paleta.TURQUESA, outline="#ffffff")
        textos = tk.Frame(marca, background=Paleta.BARRA_LATERAL)
        textos.pack(side="left", padx=(12, 0))
        tk.Label(
            textos, text="TSP Lab", background=Paleta.BARRA_LATERAL,
            foreground=Paleta.TEXTO, font=(Fuentes.TITULO, 14),
        ).pack(anchor="w")
        tk.Label(
            textos, text="TP3 · Algoritmos Genéticos", background=Paleta.BARRA_LATERAL,
            foreground=Paleta.TEXTO_TENUE, font=(Fuentes.BASE, 9),
        ).pack(anchor="w")

        def seccion(texto: str) -> None:
            tk.Label(
                barra, text=texto, background=Paleta.BARRA_LATERAL,
                foreground=Paleta.TEXTO_TENUE, font=(Fuentes.BASE, 8, "bold"),
            ).pack(anchor="w", padx=22, pady=(10, 6))

        self.navegacion: dict[str, ItemNavegacion] = {}
        seccion("GENERAL")
        self._item_nav(barra, "inicio", "⌂", "Inicio", "Resumen del trabajo")
        seccion("EJERCICIOS")
        self._item_nav(barra, "ej1", "1", "Ejercicio 1", "Branch and Bound")
        self._item_nav(barra, "ej2a", "2a", "Ejercicio 2.a", "Vecino más cercano")
        self._item_nav(barra, "ej2c", "2c", "Ejercicio 2.c", "Algoritmo genético")

        pie = tk.Frame(barra, background=Paleta.BARRA_LATERAL)
        pie.pack(side="bottom", fill="x", padx=22, pady=20)
        for texto in (
            f"{len(CAPITALES)} capitales argentinas",
            "Mapas © OpenStreetMap · CARTO",
        ):
            tk.Label(
                pie, text=texto, background=Paleta.BARRA_LATERAL,
                foreground=Paleta.TEXTO_TENUE, font=(Fuentes.BASE, 8),
            ).pack(anchor="w")

    def _item_nav(self, barra: tk.Misc, clave: str, insignia: str, titulo: str, subtitulo: str) -> None:
        item = ItemNavegacion(barra, insignia, titulo, subtitulo, lambda: self.mostrar(clave))
        item.pack(fill="x", padx=(0, 10), pady=1)
        self.navegacion[clave] = item

    def _crear_barra_estado(self, contenido: ttk.Frame) -> None:
        barra = tk.Frame(contenido, background=Paleta.BARRA_LATERAL, height=30)
        barra.grid(row=1, column=0, sticky="ew")
        tk.Frame(barra, background=Paleta.BORDE, height=1).pack(side="top", fill="x")
        self.indicador_estado = tk.Label(
            barra, text="●", background=Paleta.BARRA_LATERAL,
            foreground=Paleta.TURQUESA, font=(Fuentes.BASE, 9),
        )
        self.indicador_estado.pack(side="left", padx=(18, 6), pady=5)
        tk.Label(
            barra, textvariable=self.estado, background=Paleta.BARRA_LATERAL,
            foreground=Paleta.TEXTO_SUAVE, font=(Fuentes.BASE, 9),
        ).pack(side="left")
        tk.Label(
            barra, text="Ctrl+1…4 navegar  ·  Ctrl+Enter / F5 ejecutar",
            background=Paleta.BARRA_LATERAL, foreground=Paleta.TEXTO_TENUE,
            font=(Fuentes.BASE, 9),
        ).pack(side="right", padx=18)

    def mostrar(self, clave: str) -> None:
        self.pagina_actual = clave
        self.paginas[clave].tkraise()
        for nombre, item in self.navegacion.items():
            item.establecer_activo(nombre == clave)

    # Compatibilidad con la API anterior
    def mostrar_ejercicio_1(self) -> None:
        self.mostrar("ej1")

    def mostrar_ejercicio_2a(self) -> None:
        self.mostrar("ej2a")

    def mostrar_ejercicio_2c(self) -> None:
        self.mostrar("ej2c")

    def _ejecutar_actual(self) -> None:
        acciones = {
            "ej1": self.resolver_ejercicio_1,
            "ej2a": self.resolver_ejercicio_2a,
            "ej2c": self.resolver_ejercicio_2c,
        }
        accion = acciones.get(getattr(self, "pagina_actual", ""))
        vista = self.paginas.get(getattr(self, "pagina_actual", ""))
        if accion and isinstance(vista, VistaEjercicio) and str(vista.boton.cget("state")) != "disabled":
            accion()

    # -- pagina de inicio -----------------------------------------------------
    def _crear_inicio(self, master: tk.Misc) -> ttk.Frame:
        pagina = ttk.Frame(master, padding=(48, 44, 48, 24))
        pagina.columnconfigure(0, weight=1)

        tk.Label(
            pagina, text="TP3  ·  PROBLEMA DEL VIAJANTE", background=Paleta.ACENTO_SUAVE,
            foreground="#c9bdff", font=(Fuentes.BASE, 8, "bold"), padx=10, pady=4,
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            pagina, text="Recorré las capitales argentinas\ncon la ruta más corta",
            style="Hero.TLabel", justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(16, 10))
        ttk.Label(
            pagina,
            text=(
                "Compará un método exacto, una heurística constructiva y una "
                "metaheurística evolutiva sobre la misma matriz de distancias."
            ),
            style="Subtitulo.TLabel",
        ).grid(row=2, column=0, sticky="w")

        estadisticas = ttk.Frame(pagina)
        estadisticas.grid(row=3, column=0, sticky="w", pady=(28, 34))
        distancia_maxima = max(max(fila) for fila in DISTANCIAS_KM)
        for indice, (valor, texto) in enumerate((
            (str(len(CAPITALES)), "capitales"),
            ("3", "enfoques"),
            (formatear_entero(distancia_maxima), "km tramo máximo"),
        )):
            bloque = ttk.Frame(estadisticas)
            bloque.pack(side="left", padx=(0 if indice == 0 else 40, 0))
            tk.Label(
                bloque, text=valor, background=Paleta.FONDO, foreground=Paleta.TEXTO,
                font=(Fuentes.TITULO, 22),
            ).pack(anchor="w")
            tk.Label(
                bloque, text=texto, background=Paleta.FONDO,
                foreground=Paleta.TEXTO_TENUE, font=(Fuentes.BASE, 9),
            ).pack(anchor="w")

        tarjetas = ttk.Frame(pagina)
        tarjetas.grid(row=4, column=0, sticky="ew")
        datos = (
            ("01", "Branch and Bound", "Búsqueda exacta con poda por cota. Versión secuencial y paralela con múltiples procesos.", "EXACTO", Paleta.ACENTO, "ej1"),
            ("2a", "Vecino más cercano", "Heurística constructiva: desde la capital elegida, siempre visita la más cercana no visitada.", "HEURÍSTICA", Paleta.CELESTE, "ej2a"),
            ("2c", "Algoritmo genético", "Población de recorridos que evoluciona con selección, crossover cíclico y mutación.", "METAHEURÍSTICA", Paleta.TURQUESA, "ej2c"),
        )
        for columna, (insignia, titulo, descripcion, etiqueta, color, clave) in enumerate(datos):
            tarjetas.columnconfigure(columna, weight=1, uniform="tarjetas")
            TarjetaAccion(
                tarjetas, insignia, titulo, descripcion, etiqueta, color,
                lambda c=clave: self.mostrar(c),
            ).grid(row=0, column=columna, sticky="nsew", padx=(0 if columna == 0 else 16, 0))
        return pagina

    # -- ejercicio 1 ----------------------------------------------------------
    def _crear_ejercicio_1(self, master: tk.Misc) -> VistaEjercicio:
        vista = VistaEjercicio(
            master, "01", "Branch and Bound",
            "Resolución exacta: explora el árbol de recorridos podando las ramas que superan la mejor cota.",
            "EXACTO", Paleta.ACENTO,
            (
                EspecMetrica("distancia", "Distancia total", "km", Paleta.ACENTO),
                EspecMetrica("tiempo", "Tiempo", "s", Paleta.CELESTE),
                EspecMetrica("explorados", "Nodos explorados", "", Paleta.TURQUESA),
                EspecMetrica("podados", "Nodos podados", "", Paleta.AMBAR),
            ),
            "Resolver", self.resolver_ejercicio_1,
        )
        vista.agregar_campo(
            "Cantidad de ciudades",
            lambda m: ttk.Spinbox(m, from_=2, to=len(CAPITALES), textvariable=self.cantidad_ciudades),
            "Se usan las primeras N capitales. El tiempo crece de forma exponencial.",
        )
        vista.agregar_campo(
            "Algoritmo",
            lambda m: crear_control_segmentado(
                m, self.algoritmo,
                ((self.ALGORITMO_SECUENCIAL, "Secuencial"), (self.ALGORITMO_PARALELO, "Paralelo")),
                self._actualizar_procesos,
            ),
        )
        self.spin_procesos = vista.agregar_campo(
            "Procesos",
            lambda m: ttk.Spinbox(m, from_=1, to=16, textvariable=self.cantidad_procesos),
            "Solo aplica a la versión paralela.",
        )
        vista.guardar_texto_boton()
        self.vista_1 = vista
        self._actualizar_procesos()
        return vista

    def _actualizar_procesos(self) -> None:
        paralelo = self.algoritmo.get() == self.ALGORITMO_PARALELO
        self.spin_procesos.configure(state="normal" if paralelo else "disabled")

    # -- ejercicio 2.a --------------------------------------------------------
    def _crear_ejercicio_2a(self, master: tk.Misc) -> VistaEjercicio:
        vista = VistaEjercicio(
            master, "2a", "Vecino más cercano",
            "Heurística constructiva: parte de una capital y siempre avanza hacia la más cercana sin visitar.",
            "HEURÍSTICA", Paleta.CELESTE,
            (
                EspecMetrica("distancia", "Distancia total", "km", Paleta.CELESTE),
                EspecMetrica("tiempo", "Tiempo", "s", Paleta.ACENTO),
                EspecMetrica("maximo", "Tramo más largo", "km", Paleta.AMBAR),
                EspecMetrica("promedio", "Tramo promedio", "km", Paleta.TURQUESA),
            ),
            "Resolver heurística", self.resolver_ejercicio_2a,
        )
        vista.agregar_campo(
            "Ciudad de partida",
            lambda m: ttk.Combobox(
                m, textvariable=self.ciudad_inicial_heuristica, values=CAPITALES, state="readonly"
            ),
            "Se recorren las 24 capitales y se vuelve al punto de partida.",
        )
        vista.guardar_texto_boton()
        self.vista_2a = vista
        return vista

    # -- ejercicio 2.c --------------------------------------------------------
    def _crear_ejercicio_2c(self, master: tk.Misc) -> VistaEjercicio:
        vista = VistaEjercicio(
            master, "2c", "Algoritmo genético",
            "Metaheurística evolutiva con selección por torneo, crossover cíclico y mutación.",
            "METAHEURÍSTICA", Paleta.TURQUESA,
            (
                EspecMetrica("distancia", "Mejor distancia", "km", Paleta.TURQUESA),
                EspecMetrica("tiempo", "Tiempo", "s", Paleta.ACENTO),
                EspecMetrica("maximo", "Tramo más largo", "km", Paleta.AMBAR),
                EspecMetrica("evaluaciones", "Población × ciclos", "", Paleta.CELESTE),
            ),
            "Resolver algoritmo genético", self.resolver_ejercicio_2c,
        )
        vista.agregar_campo(
            "Ciudad de partida",
            lambda m: ttk.Combobox(
                m, textvariable=self.ciudad_inicial_genetico, values=CAPITALES, state="readonly"
            ),
        )

        def par_spinboxes(m: tk.Misc) -> tk.Frame:
            marco = tk.Frame(m, background=Paleta.SUPERFICIE)
            marco.columnconfigure((0, 1), weight=1, uniform="par")
            for columna, (texto, variable, minimo, maximo) in enumerate((
                ("Cromosomas (N)", self.cantidad_cromosomas, 2, 500),
                ("Ciclos (M)", self.cantidad_ciclos, 1, 5000),
            )):
                celda = tk.Frame(marco, background=Paleta.SUPERFICIE)
                celda.grid(row=0, column=columna, sticky="ew", padx=(0 if columna == 0 else 10, 0))
                ttk.Label(celda, text=texto, style="TarjetaCampo.TLabel").pack(anchor="w")
                ttk.Spinbox(
                    celda, from_=minimo, to=maximo, textvariable=variable, width=8
                ).pack(fill="x", pady=(5, 0))
            return marco

        vista.agregar_widget(par_spinboxes)
        vista.agregar_widget(
            lambda m: SliderValor(m, "Frecuencia de crossover", self.frecuencia_crossover)
        )
        vista.agregar_widget(
            lambda m: SliderValor(m, "Frecuencia de mutación", self.frecuencia_mutacion)
        )
        vista.agregar_campo(
            "Semilla (opcional)",
            lambda m: ttk.Entry(m, textvariable=self.semilla_genetica),
            "Dejala vacía para obtener resultados distintos en cada ejecución.",
        )
        vista.guardar_texto_boton()
        self.vista_2c = vista
        return vista

    # -- ejecucion en segundo plano --------------------------------------------
    def _ejecutar_en_segundo_plano(
        self,
        vista: VistaEjercicio,
        descripcion: str,
        funcion: Callable[..., object],
        argumentos: tuple,
        al_terminar: Callable[[object], None],
    ) -> None:
        cola: queue.Queue[tuple[str, object]] = queue.Queue()
        inicio = perf_counter()
        vista.establecer_ocupado(True)
        self._fijar_estado(f"{descripcion}…", ocupado=True)

        def trabajo() -> None:
            try:
                cola.put(("ok", funcion(*argumentos)))
            except Exception as error:  # noqa: BLE001 - se muestra al usuario
                cola.put(("error", error))

        def consultar() -> None:
            try:
                tipo, valor = cola.get_nowait()
            except queue.Empty:
                vista.estado(f"Ejecutando… {perf_counter() - inicio:.1f} s")
                self.root.after(100, consultar)
                return
            vista.establecer_ocupado(False)
            if tipo == "error":
                vista.estado("La ejecución terminó con un error.")
                self._fijar_estado("La ejecución terminó con un error.", error=True)
                messagebox.showerror("Error de ejecución", str(valor))
                return
            al_terminar(valor)
            vista.estado(f"Finalizado en {perf_counter() - inicio:.2f} s")
            self._fijar_estado(f"{descripcion}: finalizado.")

        threading.Thread(target=trabajo, daemon=True).start()
        self.root.after(100, consultar)

    def _fijar_estado(self, texto: str, ocupado: bool = False, error: bool = False) -> None:
        self.estado.set(texto)
        color = Paleta.ROJO if error else Paleta.AMBAR if ocupado else Paleta.TURQUESA
        self.indicador_estado.configure(foreground=color)

    # -- ejercicio 1: logica ---------------------------------------------------
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
        self._ejecutar_en_segundo_plano(
            self.vista_1, "Branch and Bound", ejecutar_algoritmo,
            (self.algoritmo.get(), cantidad, procesos), self._mostrar_resultado,
        )

    def _mostrar_resultado(self, resultado: object) -> None:
        if not isinstance(resultado, ResultadoGUI):
            raise TypeError("Resultado inesperado del algoritmo.")
        problema = crear_problema(resultado.cantidad_ciudades)
        tiempo, unidad = formatear_segundos(resultado.segundos)
        self.vista_1.metricas["tiempo"].unidad.configure(text=unidad)
        total = resultado.nodos_explorados + resultado.nodos_podados
        porcentaje = resultado.nodos_podados / total if total else 0
        resumen = "\n".join((
            f"Algoritmo: {resultado.algoritmo}",
            f"Ciudades: {resultado.cantidad_ciudades}",
            f"Distancia total: {resultado.ruta.distancia_total} km",
            f"Tiempo de ejecución: {resultado.segundos:.6f} s",
            f"Nodos explorados: {resultado.nodos_explorados}",
            f"Nodos podados: {resultado.nodos_podados}",
            "",
            "Recorrido completo:",
            texto_recorrido(resultado.ruta, problema),
        ))
        self.vista_1.mostrar_resultado(
            resultado.ruta, problema,
            {
                "tiempo": (tiempo, resultado.algoritmo.replace("Branch and Bound ", "").capitalize()),
                "explorados": (formatear_entero(resultado.nodos_explorados), f"{resultado.cantidad_ciudades} ciudades"),
                "podados": (formatear_entero(resultado.nodos_podados), f"{porcentaje:.1%} de los nodos generados"),
            },
            resumen,
        )

    # -- ejercicio 2.a: logica -------------------------------------------------
    def resolver_ejercicio_2a(self) -> None:
        ciudad = self.ciudad_inicial_heuristica.get()
        if ciudad not in CAPITALES:
            messagebox.showerror("Datos inválidos", "Seleccione una capital válida.")
            return
        self._ejecutar_en_segundo_plano(
            self.vista_2a, "Vecino más cercano", ejecutar_heuristica,
            (CAPITALES.index(ciudad),), self._mostrar_resultado_2a,
        )

    def _mostrar_resultado_2a(self, resultado: object) -> None:
        if not isinstance(resultado, ResultadoHeuristicoGUI):
            raise TypeError("Resultado inesperado de la heurística.")
        problema = crear_problema(len(CAPITALES))
        tramos = tramos_de(resultado.ruta, problema)
        tiempo, unidad = formatear_segundos(resultado.segundos)
        self.vista_2a.metricas["tiempo"].unidad.configure(text=unidad)
        resumen = "\n".join((
            "Algoritmo: Vecino más cercano",
            f"Ciudad de partida: {CAPITALES[resultado.ciudad_inicial]}",
            f"Distancia total: {resultado.ruta.distancia_total} km",
            f"Tiempo de ejecución: {resultado.segundos:.6f} s",
            "",
            "Recorrido completo:",
            texto_recorrido(resultado.ruta, problema),
        ))
        self.vista_2a.mostrar_resultado(
            resultado.ruta, problema,
            {
                "tiempo": (tiempo, f"Desde {CAPITALES[resultado.ciudad_inicial]}"),
                **self._metricas_tramos(tramos, resultado.ruta, problema),
            },
            resumen,
        )

    def _metricas_tramos(
        self, tramos: list[int], ruta: RutaTSP, problema: ProblemaTSP
    ) -> dict[str, tuple[str, str]]:
        posicion = max(range(len(tramos)), key=tramos.__getitem__)
        origen = problema.nombre_ciudad(ruta.recorrido[posicion])
        destino = problema.nombre_ciudad(ruta.recorrido[posicion + 1])
        return {
            "maximo": (formatear_entero(tramos[posicion]), f"{origen} → {destino}"),
            "promedio": (formatear_entero(round(sum(tramos) / len(tramos))), f"{len(tramos)} tramos"),
        }

    # -- ejercicio 2.c: logica -------------------------------------------------
    def resolver_ejercicio_2c(self) -> None:
        try:
            cantidad = self.cantidad_cromosomas.get()
            ciclos = self.cantidad_ciclos.get()
            crossover = round(self.frecuencia_crossover.get(), 4)
            mutacion = round(self.frecuencia_mutacion.get(), 4)
            semilla_texto = self.semilla_genetica.get().strip()
            semilla = int(semilla_texto) if semilla_texto else None
            ConfiguracionGenetica(cantidad, ciclos, crossover, mutacion, semilla=semilla)
        except (tk.TclError, ValueError) as error:
            messagebox.showerror("Datos inválidos", str(error))
            return
        parametros = (
            CAPITALES.index(self.ciudad_inicial_genetico.get()),
            cantidad, ciclos, crossover, mutacion, semilla,
        )
        self._ejecutar_en_segundo_plano(
            self.vista_2c, "Algoritmo genético", ejecutar_genetico,
            parametros, self._mostrar_resultado_2c,
        )

    def _mostrar_resultado_2c(self, resultado: object) -> None:
        if not isinstance(resultado, ResultadoGeneticoGUI):
            raise TypeError("Resultado inesperado del algoritmo genético.")
        problema = crear_problema(len(CAPITALES))
        tramos = tramos_de(resultado.ruta, problema)
        tiempo, unidad = formatear_segundos(resultado.segundos)
        self.vista_2c.metricas["tiempo"].unidad.configure(text=unidad)
        resumen = "\n".join((
            "Algoritmo: Algoritmo genético",
            f"Ciudad de partida: {CAPITALES[resultado.ciudad_inicial]}",
            f"Cromosomas: {resultado.cantidad_cromosomas}",
            f"Ciclos: {resultado.cantidad_ciclos}",
            f"Crossover cíclico: {resultado.frecuencia_crossover:.0%}",
            f"Mutación: {resultado.frecuencia_mutacion:.0%}",
            f"Distancia total: {resultado.ruta.distancia_total} km",
            f"Tiempo de ejecución: {resultado.segundos:.6f} s",
            "",
            "Mejor recorrido:",
            texto_recorrido(resultado.ruta, problema),
        ))
        maximo = self._metricas_tramos(tramos, resultado.ruta, problema)["maximo"]
        self.vista_2c.mostrar_resultado(
            resultado.ruta, problema,
            {
                "tiempo": (tiempo, f"Desde {CAPITALES[resultado.ciudad_inicial]}"),
                "maximo": maximo,
                "evaluaciones": (
                    f"{resultado.cantidad_cromosomas}×{resultado.cantidad_ciclos}",
                    f"Crossover {resultado.frecuencia_crossover:.0%} · Mutación {resultado.frecuencia_mutacion:.0%}",
                ),
            },
            resumen,
        )


def lanzar_gui() -> None:
    """Inicia la aplicación Tkinter."""
    root = tk.Tk()
    AplicacionTSP(root)
    root.mainloop()


if __name__ == "__main__":
    lanzar_gui()