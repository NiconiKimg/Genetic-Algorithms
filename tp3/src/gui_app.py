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
from datos_distancia_capitales import CAPITALES, DISTANCIAS_KM
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
        self.pestanas.add(self.pestana_inicio, text="Inicio")
        self.pestanas.add(self.pestana_ejercicio_1, text="Ejercicio 1")
        self._crear_inicio()
        self._crear_ejercicio_1()

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