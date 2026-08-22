"""Interfaz Tkinter para ejecutar el ejercicio 1 del TP3."""

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

from branch_bound import BranchBound
from branch_bound_paralelo import BranchBoundParalelo
from coordenadas_capitales import COORDENADAS_CAPITALES
from datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
from heuristica_vecino import VecinoMasCercano
from modelos_tsp import ProblemaTSP, RutaTSP


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


class AplicacionTSP:
    """Ventana principal y navegacion de la aplicacion del TP3."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("TP3 - Problema del Viajante")
        self.root.geometry("820x620")
        self.root.minsize(700, 500)
        self.resultados: queue.Queue[tuple[str, object]] = queue.Queue()
        self._crear_variables()
        self._crear_estilos()
        self._crear_interfaz()

    def _crear_variables(self) -> None:
        self.cantidad_ciudades = tk.IntVar(value=len(CAPITALES))
        self.algoritmo = tk.StringVar(value="Branch and Bound secuencial")
        self.cantidad_procesos = tk.IntVar(value=2)
        self.ciudad_inicial_heuristica = tk.StringVar(value=CAPITALES[0])
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
        self.pestanas.add(self.pestana_inicio, text="Inicio")
        self.pestanas.add(self.pestana_ejercicio_1, text="Ejercicio 1")
        self.pestanas.add(self.pestana_ejercicio_2a, text="Ejercicio 2.a")
        self._crear_inicio()
        self._crear_ejercicio_1()
        self._crear_ejercicio_2a()

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

    def _crear_ejercicio_1(self) -> None:
        self.pestana_ejercicio_1.columnconfigure(1, weight=1)
        self.pestana_ejercicio_1.rowconfigure(4, weight=1)

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

        self.salida = tk.Text(
            self.pestana_ejercicio_1,
            height=18,
            wrap="word",
            state="disabled",
        )
        self.salida.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(20, 0))

    def mostrar_ejercicio_1(self) -> None:
        self.pestanas.select(self.pestana_ejercicio_1)

    def mostrar_ejercicio_2a(self) -> None:
        self.pestanas.select(self.pestana_ejercicio_2a)

    def _crear_ejercicio_2a(self) -> None:
        self.pestana_ejercicio_2a.columnconfigure(1, weight=1)
        self.pestana_ejercicio_2a.rowconfigure(3, weight=1)

        ttk.Label(
            self.pestana_ejercicio_2a,
            text="Ejercicio 2.a - Vecino más cercano",
            style="Titulo.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        ttk.Label(
            self.pestana_ejercicio_2a,
            text="Desde cada ciudad se visita la capital no visitada más cercana.",
            style="Subtitulo.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 16))
        ttk.Label(
            self.pestana_ejercicio_2a,
            text="Ciudad de partida:",
        ).grid(row=2, column=0, sticky="w", pady=6)
        ttk.Combobox(
            self.pestana_ejercicio_2a,
            textvariable=self.ciudad_inicial_heuristica,
            values=CAPITALES,
            state="readonly",
            width=38,
        ).grid(row=2, column=1, sticky="w", padx=(12, 0), pady=6)
        self.boton_resolver_2a = ttk.Button(
            self.pestana_ejercicio_2a,
            text="Resolver heurística",
            command=self.resolver_ejercicio_2a,
        )
        self.boton_resolver_2a.grid(row=2, column=2, padx=(20, 0), pady=6)

        contenido = ttk.Frame(self.pestana_ejercicio_2a)
        contenido.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(16, 0))
        contenido.columnconfigure(0, weight=1)
        contenido.columnconfigure(1, weight=2)
        contenido.rowconfigure(0, weight=1)
        self.salida_2a = tk.Text(contenido, width=36, wrap="word", state="disabled")
        self.salida_2a.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.mapa_2a = tk.Canvas(
            contenido,
            background="#f2f5f4",
            highlightthickness=1,
            highlightbackground="#b8c8c2",
        )
        self.mapa_2a.grid(row=0, column=1, sticky="nsew")
        self.mapa_2a.bind("<Configure>", self._redibujar_mapa)
        self._dibujar_mapa_base()

    def resolver_ejercicio_2a(self) -> None:
        ciudad = self.ciudad_inicial_heuristica.get()
        if ciudad not in CAPITALES:
            messagebox.showerror("Datos inválidos", "Seleccione una capital válida.")
            return
        self.boton_resolver_2a.configure(state="disabled")
        self.estado.set("Ejecutando la heurística del vecino más cercano...")
        self._escribir_salida_2a("Calculando ruta heurística...\n")
        threading.Thread(
            target=self._trabajar_2a,
            args=(CAPITALES.index(ciudad),),
            daemon=True,
        ).start()
        self.root.after(100, self._consultar_resultado_2a)

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
        nombres = "\n".join(
            f"{indice + 1:2}. {nombre}"
            for indice, nombre in enumerate(resultado.ruta.nombres(problema))
        )
        texto = "\n".join(
            (
                "Algoritmo: Vecino más cercano",
                f"Ciudad de partida: {CAPITALES[resultado.ciudad_inicial]}",
                f"Distancia total: {resultado.ruta.distancia_total} km",
                f"Tiempo de ejecución: {resultado.segundos:.6f} s",
                "",
                "Recorrido completo:",
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

    def _dibujar_mapa_base(self) -> None:
        self.mapa_2a.delete("all")
        self.mapa_2a.create_text(
            12,
            12,
            anchor="nw",
            text="Mapa esquemático de la República Argentina",
            fill="#34443e",
            font=("Segoe UI", 10, "bold"),
        )

    def _redibujar_mapa(self, _evento: tk.Event) -> None:
        if not hasattr(self, "ruta_mapa_2a"):
            self._dibujar_mapa_base()
            return
        self._dibujar_ruta(self.ruta_mapa_2a, crear_problema(len(CAPITALES)))

    def _dibujar_ruta(self, ruta: RutaTSP, problema: ProblemaTSP) -> None:
        self.ruta_mapa_2a = ruta
        self.mapa_2a.delete("all")
        ancho = max(self.mapa_2a.winfo_width(), 420)
        alto = max(self.mapa_2a.winfo_height(), 360)
        longitudes = [COORDENADAS_CAPITALES[nombre][0] for nombre in CAPITALES]
        latitudes = [COORDENADAS_CAPITALES[nombre][1] for nombre in CAPITALES]
        min_lon, max_lon = min(longitudes), max(longitudes)
        min_lat, max_lat = min(latitudes), max(latitudes)

        def punto(indice: int) -> tuple[float, float]:
            nombre = problema.nombre_ciudad(indice)
            longitud, latitud = COORDENADAS_CAPITALES[nombre]
            x = 30 + (longitud - min_lon) / (max_lon - min_lon) * (ancho - 60)
            y = 38 + (max_lat - latitud) / (max_lat - min_lat) * (alto - 78)
            return x, y

        self.mapa_2a.create_text(
            12,
            12,
            anchor="nw",
            text="Mapa esquemático - recorrido heurístico",
            fill="#34443e",
            font=("Segoe UI", 10, "bold"),
        )
        puntos = [punto(indice) for indice in ruta.recorrido]
        for origen, destino in zip(puntos, puntos[1:]):
            self.mapa_2a.create_line(*origen, *destino, fill="#197c72", width=2)
        for indice, (x, y) in zip(ruta.recorrido[:-1], puntos[:-1]):
            inicio = indice == ruta.recorrido[0]
            color = "#d05a3d" if inicio else "#245b63"
            radio = 6 if inicio else 4
            self.mapa_2a.create_oval(
                x - radio,
                y - radio,
                x + radio,
                y + radio,
                fill=color,
                outline="white",
            )
            self.mapa_2a.create_text(
                x + 7,
                y,
                anchor="w",
                text=problema.nombre_ciudad(indice),
                fill="#28332f",
                font=("Segoe UI", 7),
            )

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
        self.estado.set("Resolviendo... la interfaz seguirá disponible.")
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
        nombres = "\n".join(
            f"{indice + 1:2}. {nombre}"
            for indice, nombre in enumerate(resultado.ruta.nombres(crear_problema(resultado.cantidad_ciudades)))
        )
        salida = "\n".join(
            (
                f"Algoritmo: {resultado.algoritmo}",
                f"Ciudades: {resultado.cantidad_ciudades}",
                f"Distancia total: {resultado.ruta.distancia_total} km",
                f"Tiempo de ejecución: {resultado.segundos:.6f} s",
                f"Nodos explorados: {resultado.nodos_explorados}",
                f"Nodos podados: {resultado.nodos_podados}",
                "",
                "Recorrido completo:",
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