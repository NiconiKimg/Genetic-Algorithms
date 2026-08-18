import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from src.mochila import Elemento, crear_elementos_desde_tabla, crear_elementos_por_peso
from src.algoritmos import resolver_exhaustivo, resolver_greedy
from src.datos_mochila import (
    TABLA_VOLUMEN_EJ1_EJ2,
    CAPACIDAD_VOLUMEN_EJ1_EJ2,
    PESOS_EJ3,
    VALORES_EJ3,
    CAPACIDAD_PESO_EJ3,
)
from src.logger import Logger
from src.graficadores import graficar_tiempo_vs_n, graficar_uso_capacidad, graficar_heatmap_elementos


class AplicacionMochilaGUI(tk.Tk):

    def __init__(self) -> None:
        super().__init__()
        self.title("TP2 — Problema de la Mochila")
        self.geometry("960x640")

        self.elementos: list[Elemento] = []
        self.capacidad: float = 4200.0
        self.dimension: str = "volumen"
        self.filas_tabla_memoria: list[dict] = []

        self._crear_interfaz()
        self._cargar_ejercicio("Ejercicio 1")

    def _crear_interfaz(self) -> None:
        """Construye la distribución de la ventana"""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Panel Izquierdo (Selección, Opciones, Botón Ejecutar y Elementos)
        left_frame = ttk.Frame(main_frame, width=380)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))

        # Panel Derecho (Resultados y Tabla de Salida)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 1. Marco de Selección u Opciones
        self.frame_opciones = ttk.LabelFrame(left_frame, text=" Control de Ejecución ", padding=10)
        self.frame_opciones.pack(fill=tk.X, pady=(0, 10))

        # Selector de Ejercicio
        ttk.Label(self.frame_opciones, text="Ejercicio:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.var_ejercicio = tk.StringVar(value="Ejercicio 1")
        combo_ej = ttk.Combobox(
            self.frame_opciones,
            textvariable=self.var_ejercicio,
            values=["Ejercicio 1", "Ejercicio 2", "Ejercicio 3"],
            state="readonly",
            width=22,
        )
        combo_ej.grid(row=0, column=1, sticky=tk.W, pady=3, padx=5)
        combo_ej.bind("<<ComboboxSelected>>", lambda e: self._cargar_ejercicio(self.var_ejercicio.get()))

        # Checkbox Ejercicio 1 (Ocultar no válidos)
        self.var_ocultar_no_factibles = tk.BooleanVar(value=False)
        self.chk_no_factibles = ttk.Checkbutton(
            self.frame_opciones,
            text="Ocultar subconjuntos no válidos",
            variable=self.var_ocultar_no_factibles,
            command=self._filtrar_y_poblar_tabla,
        )

        # Checkbox "Ordenar de mejor a peor" (Ej1 y Ej3)
        self.var_ordenar_mejor_peor = tk.BooleanVar(value=False)
        self.chk_ordenar = ttk.Checkbutton(
            self.frame_opciones,
            text="Ordenar de mejor a peor",
            variable=self.var_ordenar_mejor_peor,
            command=self._filtrar_y_poblar_tabla,
        )

        # Toggle Ejercicio 3 (Exhaustivo / Greedy / Ambos)
        self.var_toggle_ej3 = tk.StringVar(value="Exhaustivo")
        self.frame_toggle_ej3 = ttk.Frame(self.frame_opciones)
        ttk.Radiobutton(self.frame_toggle_ej3, text="Exhaustivo", variable=self.var_toggle_ej3, value="Exhaustivo").pack(side=tk.LEFT)
        ttk.Radiobutton(self.frame_toggle_ej3, text="Greedy", variable=self.var_toggle_ej3, value="Greedy").pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(self.frame_toggle_ej3, text="Ambos", variable=self.var_toggle_ej3, value="Ambos").pack(side=tk.LEFT)

        # Info Ejercicio 2
        self.lbl_info_ej2 = ttk.Label(self.frame_opciones, text="Ejecuta el Algoritmo Goloso (Greedy)")

        # BOTÓN EJECUTAR
        self.btn_ejecutar = ttk.Button(self.frame_opciones, text="Ejecutar", command=self._ejecutar)
        self.btn_ejecutar.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(10, 2))

        # BOTÓN BENCHMARKS Y GRÁFICOS
        self.btn_benchmarks = ttk.Button(
            self.frame_opciones,
            text="Generar Análisis Comparativo",
            command=self._generar_benchmarks_y_graficos,
        )
        self.btn_benchmarks.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(4, 2))

        # 2. Tabla de Elementos del Enunciado
        frame_elem = ttk.LabelFrame(left_frame, text=" Elementos del Enunciado ", padding=10)
        frame_elem.pack(fill=tk.BOTH, expand=True)

        cols_elem = ("id", "capacidad", "valor", "ratio")
        self.tree_elem = ttk.Treeview(frame_elem, columns=cols_elem, show="headings", height=7)
        self.tree_elem.heading("id", text="ID")
        self.tree_elem.heading("capacidad", text="Capacidad")
        self.tree_elem.heading("valor", text="Valor ($)")
        self.tree_elem.heading("ratio", text="Ratio ($/cap)")

        self.tree_elem.column("id", width=35, anchor=tk.CENTER)
        self.tree_elem.column("capacidad", width=90, anchor=tk.E)
        self.tree_elem.column("valor", width=75, anchor=tk.E)
        self.tree_elem.column("ratio", width=85, anchor=tk.E)

        scroll_elem = ttk.Scrollbar(frame_elem, orient=tk.VERTICAL, command=self.tree_elem.yview)
        self.tree_elem.configure(yscroll=scroll_elem.set)
        self.tree_elem.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_elem.pack(side=tk.RIGHT, fill=tk.Y)

        # 3. Resultados Superiores
        frame_res = ttk.LabelFrame(right_frame, text=" Métricas de Ejecución ", padding=10)
        frame_res.pack(fill=tk.X, pady=(0, 10))

        self.lbl_res1 = ttk.Label(frame_res, text="Valor Obtenido: -", font=("Segoe UI", 9, "bold"))
        self.lbl_res1.pack(anchor=tk.W, pady=2)

        self.lbl_res2 = ttk.Label(frame_res, text="Capacidad Usada: -", font=("Segoe UI", 9))
        self.lbl_res2.pack(anchor=tk.W, pady=2)

        self.lbl_tiempo = ttk.Label(frame_res, text="Tiempo de Cómputo: -", font=("Segoe UI", 8, "italic"))
        self.lbl_tiempo.pack(anchor=tk.W, pady=2)

        # 4. Tabla de Salida (Incluye columna de Método/Búsqueda)
        frame_sub = ttk.LabelFrame(right_frame, text=" Tabla de Subconjuntos y Resultados ", padding=10)
        frame_sub.pack(fill=tk.BOTH, expand=True)

        cols_sub = ("metodo", "pos", "valor", "capacidad", "factible", "elementos")
        self.tree_sub = ttk.Treeview(frame_sub, columns=cols_sub, show="headings")
        self.tree_sub.heading("metodo", text="Método")
        self.tree_sub.heading("pos", text="Pos")
        self.tree_sub.heading("valor", text="Valor ($)")
        self.tree_sub.heading("capacidad", text="Cap. Usada")
        self.tree_sub.heading("factible", text="Factible")
        self.tree_sub.heading("elementos", text="Elementos Incluidos")

        self.tree_sub.column("metodo", width=85, anchor=tk.CENTER)
        self.tree_sub.column("pos", width=40, anchor=tk.CENTER)
        self.tree_sub.column("valor", width=80, anchor=tk.E)
        self.tree_sub.column("capacidad", width=90, anchor=tk.E)
        self.tree_sub.column("factible", width=75, anchor=tk.CENTER)
        self.tree_sub.column("elementos", width=170, anchor=tk.W)

        scroll_sub = ttk.Scrollbar(frame_sub, orient=tk.VERTICAL, command=self.tree_sub.yview)
        self.tree_sub.configure(yscroll=scroll_sub.set)
        self.tree_sub.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_sub.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_sub.tag_configure("factible", background="#e8f8f5")
        self.tree_sub.tag_configure("no_factible", background="#fadbd8")

    def _cargar_ejercicio(self, nombre: str) -> None:
        """Carga los datos y ajusta las opciones específicas por ejercicio"""
        # Ocultar controles secundarios
        self.chk_no_factibles.grid_forget()
        self.lbl_info_ej2.grid_forget()
        self.frame_toggle_ej3.grid_forget()
        self.chk_ordenar.grid_forget()

        if nombre == "Ejercicio 1":
            self.elementos = crear_elementos_desde_tabla(TABLA_VOLUMEN_EJ1_EJ2)
            self.capacidad = CAPACIDAD_VOLUMEN_EJ1_EJ2
            self.dimension = "volumen"
            self.chk_no_factibles.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=3)
            self.chk_ordenar.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=3)
        elif nombre == "Ejercicio 2":
            self.elementos = crear_elementos_desde_tabla(TABLA_VOLUMEN_EJ1_EJ2)
            self.capacidad = CAPACIDAD_VOLUMEN_EJ1_EJ2
            self.dimension = "volumen"
            self.lbl_info_ej2.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=3)
        elif nombre == "Ejercicio 3":
            self.elementos = crear_elementos_por_peso(PESOS_EJ3, VALORES_EJ3)
            self.capacidad = CAPACIDAD_PESO_EJ3
            self.dimension = "peso"
            self.frame_toggle_ej3.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=3)
            self.chk_no_factibles.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=3)
            self.chk_ordenar.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=3)

        # Actualizar tabla de elementos
        for item in self.tree_elem.get_children():
            self.tree_elem.delete(item)

        for elem in self.elementos:
            cap_val = elem.volumen if self.dimension == "volumen" else elem.peso
            ratio = elem.obtener_ratio(self.dimension)
            self.tree_elem.insert(
                "",
                tk.END,
                values=(
                    elem.id,
                    f"{cap_val:.1f}",
                    f"${elem.valor:.1f}",
                    f"{ratio:.4f}",
                ),
            )

        # Limpiar resultados previos
        self.lbl_res1.config(text="Valor Obtenido: -")
        self.lbl_res2.config(text="Capacidad Usada: -")
        self.lbl_tiempo.config(text="Tiempo de Cómputo: -")
        self.filas_tabla_memoria = []
        for item in self.tree_sub.get_children():
            self.tree_sub.delete(item)

    def _ejecutar(self) -> None:
        """Despacha la ejecución al método del ejercicio activo"""
        self.filas_tabla_memoria = []
        {
            "Ejercicio 1": self._ejecutar_ej1,
            "Ejercicio 2": self._ejecutar_ej2,
            "Ejercicio 3": self._ejecutar_ej3,
        }[self.var_ejercicio.get()]()
        self._filtrar_y_poblar_tabla()

    def _ejecutar_ej1(self) -> None:
        logger = Logger()
        logger.iniciar_ejecucion("exhaustivo", len(self.elementos), self.capacidad, "volumen")

        optimo, tabla = resolver_exhaustivo(self.elementos, self.capacidad, "volumen")

        t = logger.finalizar_ejecucion(
            optimo.valor_total, optimo.volumen_total, optimo.peso_total,
            optimo.etiquetas_elementos(), len(tabla),
        )

        self.lbl_res1.config(text=f"Valor Óptimo (Exhaustivo): ${optimo.valor_total:.2f}")
        self.lbl_res2.config(
            text=f"Capacidad Ocupada: {optimo.volumen_total:.1f} / {self.capacidad:.1f} cm³  |  Elementos: [{optimo.etiquetas_elementos()}]"
        )
        self.lbl_tiempo.config(text=f"Tiempo de Ejecución: {t:.6f} segundos")

        for idx, sol in enumerate(tabla, 1):
            self.filas_tabla_memoria.append({
                "metodo": "Exhaustivo",
                "pos": idx,
                "valor": f"${sol.valor_total:.2f}",
                "valor_float": sol.valor_total,
                "capacidad": f"{sol.volumen_total:.1f} cm³",
                "factible": "SÍ" if sol.es_factible else "NO",
                "elementos": f"[{sol.etiquetas_elementos()}]",
                "es_factible": sol.es_factible,
            })

        dir_salida = Path(__file__).resolve().parent.parent / "outputs"
        logger.exportar_tabla(dir_salida, "ejercicio_1")

    def _ejecutar_ej2(self) -> None:
        """Algoritmo Greedy — selección secuencial por densidad de valor (ratio $/cm³)"""
        logger = Logger()
        logger.iniciar_ejecucion("greedy", len(self.elementos), self.capacidad, "volumen")

        greedy = resolver_greedy(self.elementos, self.capacidad, "volumen")

        t = logger.finalizar_ejecucion(
            greedy.valor_total, greedy.volumen_total, greedy.peso_total,
            greedy.etiquetas_elementos(),
        )

        self.lbl_res1.config(text=f"Valor Obtenido (Greedy): ${greedy.valor_total:.2f}")
        self.lbl_res2.config(
            text=f"Capacidad Ocupada: {greedy.volumen_total:.1f} / {self.capacidad:.1f} cm³  |  Elementos: [{greedy.etiquetas_elementos()}]"
        )
        self.lbl_tiempo.config(text=f"Tiempo de Ejecución: {t:.6f} segundos")

        self.filas_tabla_memoria.append({
            "metodo": "Greedy",
            "pos": 1,
            "valor": f"${greedy.valor_total:.2f}",
            "valor_float": greedy.valor_total,
            "capacidad": f"{greedy.volumen_total:.1f} cm³",
            "factible": "SÍ" if greedy.es_factible else "NO",
            "elementos": f"[{greedy.etiquetas_elementos()}]",
            "es_factible": greedy.es_factible,
        })

        dir_salida = Path(__file__).resolve().parent.parent / "outputs"
        logger.exportar_tabla(dir_salida, "ejercicio_2")

    def _ejecutar_ej3(self) -> None:
        """Comparativa Exhaustivo vs Greedy — mochila con restricción de peso (3000 grs).

        Demuestra que el Greedy puede no alcanzar el óptimo global al priorizar la densidad
        de valor sin evaluar todas las combinaciones posibles.
        """
        logger = Logger()
        mode = self.var_toggle_ej3.get()
        t_exh = 0.0
        t_gre = 0.0
        optimo = None
        greedy = None

        if mode in ("Exhaustivo", "Ambos"):
            logger.iniciar_ejecucion("exhaustivo", len(self.elementos), self.capacidad, "peso")
            optimo, tabla = resolver_exhaustivo(self.elementos, self.capacidad, "peso")
            t_exh = logger.finalizar_ejecucion(
                optimo.valor_total, optimo.volumen_total, optimo.peso_total,
                optimo.etiquetas_elementos(), len(tabla),
            )
            for idx, sol in enumerate(tabla, 1):
                self.filas_tabla_memoria.append({
                    "metodo": "Exhaustivo",
                    "pos": idx,
                    "valor": f"${sol.valor_total:.2f}",
                    "valor_float": sol.valor_total,
                    "capacidad": f"{sol.peso_total:.1f} grs",
                    "factible": "SÍ" if sol.es_factible else "NO",
                    "elementos": f"[{sol.etiquetas_elementos()}]",
                    "es_factible": sol.es_factible,
                })

        if mode in ("Greedy", "Ambos"):
            logger.iniciar_ejecucion("greedy", len(self.elementos), self.capacidad, "peso")
            greedy = resolver_greedy(self.elementos, self.capacidad, "peso")
            t_gre = logger.finalizar_ejecucion(
                greedy.valor_total, greedy.volumen_total, greedy.peso_total,
                greedy.etiquetas_elementos(),
            )
            self.filas_tabla_memoria.append({
                "metodo": "Greedy",
                "pos": 1,
                "valor": f"${greedy.valor_total:.2f}",
                "valor_float": greedy.valor_total,
                "capacidad": f"{greedy.peso_total:.1f} grs",
                "factible": "SÍ" if greedy.es_factible else "NO",
                "elementos": f"[{greedy.etiquetas_elementos()}]",
                "es_factible": greedy.es_factible,
            })

        if mode == "Exhaustivo" and optimo:
            self.lbl_res1.config(text=f"Exhaustivo: ${optimo.valor_total:.2f} | Peso: {optimo.peso_total:.1f}/{self.capacidad:.1f} grs")
            self.lbl_res2.config(text=f"Elementos Incluidos: [{optimo.etiquetas_elementos()}]")
            self.lbl_tiempo.config(text=f"Tiempo de Cómputo: {t_exh:.6f} segundos")
        elif mode == "Greedy" and greedy:
            self.lbl_res1.config(text=f"Greedy: ${greedy.valor_total:.2f} | Peso: {greedy.peso_total:.1f}/{self.capacidad:.1f} grs")
            self.lbl_res2.config(text=f"Elementos Incluidos: [{greedy.etiquetas_elementos()}]")
            self.lbl_tiempo.config(text=f"Tiempo de Cómputo: {t_gre:.6f} segundos")
        elif mode == "Ambos" and optimo and greedy:
            self.lbl_res1.config(
                text=f"Exhaustivo: ${optimo.valor_total:.2f} [{optimo.etiquetas_elementos()}]  |  Greedy: ${greedy.valor_total:.2f} [{greedy.etiquetas_elementos()}]"
            )
            self.lbl_res2.config(text=f"Capacidad Máxima: {self.capacidad:.1f} grs")
            self.lbl_tiempo.config(text=f"Tiempo Exhaustivo: {t_exh:.6f}s | Tiempo Greedy: {t_gre:.6f}s")

        dir_salida = Path(__file__).resolve().parent.parent / "outputs"
        logger.exportar_tabla(dir_salida, "ejercicio_3")

    def _filtrar_y_poblar_tabla(self) -> None:
        """Llena la tabla de salida con los resultados almacenados"""
        for item in self.tree_sub.get_children():
            self.tree_sub.delete(item)

        ocultar_no_factibles = (
            self.var_ocultar_no_factibles.get()
            if self.var_ejercicio.get() in ("Ejercicio 1", "Ejercicio 3")
            else False
        )

        filas_a_mostrar = (
            sorted(self.filas_tabla_memoria, key=lambda f: f.get("valor_float", 0), reverse=True)
            if self.var_ordenar_mejor_peor.get()
            else self.filas_tabla_memoria
        )

        for fila in filas_a_mostrar:
            if ocultar_no_factibles and not fila["es_factible"]:
                continue

            tag = "factible" if fila["es_factible"] else "no_factible"

            self.tree_sub.insert(
                "",
                tk.END,
                values=(
                    fila["metodo"],
                    fila["pos"],
                    fila["valor"],
                    fila["capacidad"],
                    fila["factible"],
                    fila["elementos"],
                ),
                tags=(tag,),
            )


    def _generar_benchmarks_y_graficos(self) -> None:
        """Ejecuta benchmarks comparativos y guarda los gráficos en outputs/plots/"""
        self.btn_benchmarks.config(state="disabled", text="Generando...")

        def _tarea() -> None:
            try:
                logger = Logger()
                tabla_base = TABLA_VOLUMEN_EJ1_EJ2
                for n in [4, 6, 8, 10]:
                    elementos = crear_elementos_desde_tabla(tabla_base[:n])
                    for _ in range(5):
                        logger.iniciar_ejecucion("exhaustivo", n, CAPACIDAD_VOLUMEN_EJ1_EJ2, "volumen")
                        opt, todas = resolver_exhaustivo(elementos, CAPACIDAD_VOLUMEN_EJ1_EJ2, "volumen")
                        logger.finalizar_ejecucion(
                            opt.valor_total, opt.volumen_total, opt.peso_total,
                            opt.etiquetas_elementos(), len(todas),
                        )
                        logger.iniciar_ejecucion("greedy", n, CAPACIDAD_VOLUMEN_EJ1_EJ2, "volumen")
                        gre = resolver_greedy(elementos, CAPACIDAD_VOLUMEN_EJ1_EJ2, "volumen")
                        logger.finalizar_ejecucion(
                            gre.valor_total, gre.volumen_total, gre.peso_total,
                            gre.etiquetas_elementos(),
                        )

                dir_out = Path(__file__).resolve().parent.parent / "outputs"
                ruta_csv = logger.exportar_tabla(dir_out, "benchmarks")

                graficar_tiempo_vs_n(ruta_csv)
                graficar_uso_capacidad(ruta_csv)
                graficar_heatmap_elementos(ruta_csv)

                dir_plots = str(dir_out / "plots")
                self.after(0, lambda p=dir_plots: messagebox.showinfo(
                    "Análisis generado",
                    f"Gráficos guardados en:\n{p}",
                ))

            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("Error en Benchmarks", str(exc)))
            finally:
                self.after(
                    0,
                    lambda: self.btn_benchmarks.config(
                        state="normal", text="Generar Análisis Comparativo"
                    ),
                )

        threading.Thread(target=_tarea, daemon=True).start()



def lanzar_gui() -> None:
    """Abre la ventana principal de la interfaz gráfica"""
    app = AplicacionMochilaGUI()
    app.mainloop()


if __name__ == "__main__":
    lanzar_gui()
