"""Componentes reutilizables (tarjetas, navegacion, mapa y tabla) de la GUI."""

from collections.abc import Callable, Sequence
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageDraw, ImageTk
from tkintermapview import TkinterMapView

from comun.modelos_tsp import ProblemaTSP, RutaTSP
from interfaz.tema import Fuentes, Paleta
from visualizacion.coordenadas_capitales import COORDENADAS_CAPITALES


def formatear_entero(valor: int) -> str:
    """Formatea enteros con separador de miles al estilo argentino."""
    return f"{valor:,}".replace(",", ".")


class Tarjeta(tk.Frame):
    """Contenedor con fondo elevado y borde de 1px."""

    def __init__(self, master: tk.Misc, padding: int = 18, **kwargs: object) -> None:
        super().__init__(
            master,
            background=Paleta.SUPERFICIE,
            highlightthickness=1,
            highlightbackground=Paleta.BORDE,
            highlightcolor=Paleta.BORDE,
            **kwargs,
        )
        self.cuerpo = tk.Frame(self, background=Paleta.SUPERFICIE)
        self.cuerpo.pack(fill="both", expand=True, padx=padding, pady=padding)


class TarjetaMetrica(Tarjeta):
    """Indicador numerico grande con titulo, unidad y una franja de color."""

    def __init__(
        self,
        master: tk.Misc,
        titulo: str,
        unidad: str = "",
        color: str = Paleta.ACENTO,
    ) -> None:
        super().__init__(master, padding=0)
        tk.Frame(self.cuerpo, background=color, height=3).pack(fill="x")
        interior = tk.Frame(self.cuerpo, background=Paleta.SUPERFICIE)
        interior.pack(fill="both", expand=True, padx=16, pady=(12, 14))
        tk.Label(
            interior,
            text=titulo.upper(),
            background=Paleta.SUPERFICIE,
            foreground=Paleta.TEXTO_TENUE,
            font=(Fuentes.BASE, 8, "bold"),
            anchor="w",
        ).pack(fill="x")
        fila = tk.Frame(interior, background=Paleta.SUPERFICIE)
        fila.pack(fill="x", pady=(4, 0))
        self.valor = tk.StringVar(value="—")
        tk.Label(
            fila,
            textvariable=self.valor,
            background=Paleta.SUPERFICIE,
            foreground=Paleta.TEXTO,
            font=(Fuentes.TITULO, 19),
            anchor="w",
        ).pack(side="left")
        self.unidad = tk.Label(
            fila,
            text=unidad,
            background=Paleta.SUPERFICIE,
            foreground=Paleta.TEXTO_SUAVE,
            font=(Fuentes.BASE, 10),
        )
        self.unidad.pack(side="left", padx=(6, 0), pady=(8, 0))
        self.detalle = tk.Label(
            interior,
            text=" ",
            background=Paleta.SUPERFICIE,
            foreground=Paleta.TEXTO_TENUE,
            font=(Fuentes.BASE, 9),
            anchor="w",
        )
        self.detalle.pack(fill="x", pady=(2, 0))

    def mostrar(self, valor: str, detalle: str = " ", color_detalle: str | None = None) -> None:
        self.valor.set(valor)
        self.detalle.configure(
            text=detalle or " ", foreground=color_detalle or Paleta.TEXTO_TENUE
        )

    def limpiar(self) -> None:
        self.valor.set("—")
        self.detalle.configure(text=" ", foreground=Paleta.TEXTO_TENUE)


def _vincular_recursivo(widget: tk.Misc, evento: str, funcion: Callable) -> None:
    widget.bind(evento, funcion, add="+")
    for hijo in widget.winfo_children():
        _vincular_recursivo(hijo, evento, funcion)


class _ConHover(tk.Frame):
    """Base para frames clickeables con estado hover."""

    def _instalar_hover(self, comando: Callable[[], None]) -> None:
        self._comando = comando
        self._hover = False
        _vincular_recursivo(self, "<Enter>", self._entrar)
        _vincular_recursivo(self, "<Leave>", self._salir)
        _vincular_recursivo(self, "<Button-1>", lambda _e: self._comando())
        self.configure(cursor="hand2")

    def _entrar(self, _evento: tk.Event) -> None:
        if not self._hover:
            self._hover = True
            self._refrescar()

    def _salir(self, _evento: tk.Event) -> None:
        x, y = self.winfo_pointerxy()
        debajo = self.winfo_containing(x, y)
        if debajo is not None and str(debajo).startswith(str(self)):
            return
        self._hover = False
        self._refrescar()

    def _pintar(self, widget: tk.Misc, fondo: str) -> None:
        if not getattr(widget, "_fondo_fijo", False):
            widget.configure(background=fondo)
        for hijo in widget.winfo_children():
            self._pintar(hijo, fondo)

    def _refrescar(self) -> None:
        raise NotImplementedError


class ItemNavegacion(_ConHover):
    """Boton de la barra lateral con indicador de seccion activa."""

    def __init__(
        self,
        master: tk.Misc,
        insignia: str,
        titulo: str,
        subtitulo: str,
        comando: Callable[[], None],
    ) -> None:
        super().__init__(master, background=Paleta.BARRA_LATERAL)
        self.activo = False
        self.indicador = tk.Frame(self, width=3, background=Paleta.BARRA_LATERAL)
        self.indicador.pack(side="left", fill="y")
        self.indicador._fondo_fijo = True  # type: ignore[attr-defined]
        interior = tk.Frame(self, background=Paleta.BARRA_LATERAL)
        interior.pack(side="left", fill="both", expand=True, padx=(12, 12), pady=9)
        self.insignia = tk.Label(
            interior,
            text=insignia,
            width=3,
            background=Paleta.SUPERFICIE_2,
            foreground=Paleta.TEXTO_SUAVE,
            font=(Fuentes.MONO, 9, "bold"),
            pady=5,
        )
        self.insignia._fondo_fijo = True  # type: ignore[attr-defined]
        self.insignia.pack(side="left")
        textos = tk.Frame(interior, background=Paleta.BARRA_LATERAL)
        textos.pack(side="left", fill="x", padx=(12, 0))
        self.titulo = tk.Label(
            textos,
            text=titulo,
            background=Paleta.BARRA_LATERAL,
            foreground=Paleta.TEXTO_SUAVE,
            font=(Fuentes.TITULO, 10),
            anchor="w",
        )
        self.titulo.pack(fill="x")
        self.subtitulo = tk.Label(
            textos,
            text=subtitulo,
            background=Paleta.BARRA_LATERAL,
            foreground=Paleta.TEXTO_TENUE,
            font=(Fuentes.BASE, 8),
            anchor="w",
        )
        self.subtitulo.pack(fill="x")
        self._instalar_hover(comando)

    def establecer_activo(self, activo: bool) -> None:
        self.activo = activo
        self._refrescar()

    def _refrescar(self) -> None:
        if self.activo:
            fondo = Paleta.SUPERFICIE_2
        elif self._hover:
            fondo = Paleta.SUPERFICIE
        else:
            fondo = Paleta.BARRA_LATERAL
        self._pintar(self, fondo)
        self.indicador.configure(
            background=Paleta.ACENTO if self.activo else Paleta.BARRA_LATERAL
        )
        self.insignia.configure(
            background=Paleta.ACENTO if self.activo else Paleta.SUPERFICIE_2,
            foreground="#ffffff" if self.activo else Paleta.TEXTO_SUAVE,
        )
        self.titulo.configure(
            foreground=Paleta.TEXTO if self.activo or self._hover else Paleta.TEXTO_SUAVE
        )


class TarjetaAccion(_ConHover):
    """Tarjeta clickeable de la pantalla de inicio."""

    def __init__(
        self,
        master: tk.Misc,
        insignia: str,
        titulo: str,
        descripcion: str,
        etiqueta: str,
        color: str,
        comando: Callable[[], None],
    ) -> None:
        super().__init__(
            master,
            background=Paleta.SUPERFICIE,
            highlightthickness=1,
            highlightbackground=Paleta.BORDE,
        )
        self._color = color
        interior = tk.Frame(self, background=Paleta.SUPERFICIE)
        interior.pack(fill="both", expand=True, padx=22, pady=22)
        cabecera = tk.Frame(interior, background=Paleta.SUPERFICIE)
        cabecera.pack(fill="x")
        insignia_label = tk.Label(
            cabecera,
            text=insignia,
            background=color,
            foreground=Paleta.FONDO,
            font=(Fuentes.MONO, 11, "bold"),
            width=4,
            pady=7,
        )
        insignia_label._fondo_fijo = True  # type: ignore[attr-defined]
        insignia_label.pack(side="left")
        chip = tk.Label(
            cabecera,
            text=etiqueta,
            background=Paleta.SUPERFICIE_2,
            foreground=color,
            font=(Fuentes.BASE, 8, "bold"),
            padx=8,
            pady=2,
        )
        chip._fondo_fijo = True  # type: ignore[attr-defined]
        chip.pack(side="right", anchor="n")
        tk.Label(
            interior,
            text=titulo,
            background=Paleta.SUPERFICIE,
            foreground=Paleta.TEXTO,
            font=(Fuentes.TITULO, 14),
            anchor="w",
        ).pack(fill="x", pady=(18, 6))
        tk.Label(
            interior,
            text=descripcion,
            background=Paleta.SUPERFICIE,
            foreground=Paleta.TEXTO_SUAVE,
            font=(Fuentes.BASE, 10),
            anchor="nw",
            justify="left",
            wraplength=250,
        ).pack(fill="both", expand=True)
        self.enlace = tk.Label(
            interior,
            text="Abrir  →",
            background=Paleta.SUPERFICIE,
            foreground=Paleta.TEXTO_SUAVE,
            font=(Fuentes.TITULO, 10),
            anchor="w",
        )
        self.enlace.pack(fill="x", pady=(16, 0))
        self._instalar_hover(comando)

    def _refrescar(self) -> None:
        fondo = Paleta.SUPERFICIE_2 if self._hover else Paleta.SUPERFICIE
        self._pintar(self, fondo)
        self.configure(
            highlightbackground=self._color if self._hover else Paleta.BORDE
        )
        self.enlace.configure(foreground=self._color if self._hover else Paleta.TEXTO_SUAVE)


class SliderValor(tk.Frame):
    """Slider ttk con etiqueta y valor porcentual a la derecha."""

    def __init__(
        self,
        master: tk.Misc,
        texto: str,
        variable: tk.DoubleVar,
        desde: float = 0.0,
        hasta: float = 1.0,
        paso: float = 0.01,
    ) -> None:
        super().__init__(master, background=Paleta.SUPERFICIE)
        self.variable = variable
        self.paso = paso
        fila = tk.Frame(self, background=Paleta.SUPERFICIE)
        fila.pack(fill="x")
        ttk.Label(fila, text=texto, style="TarjetaCampo.TLabel").pack(side="left")
        self.texto_valor = ttk.Label(fila, style="TarjetaValor.TLabel")
        self.texto_valor.pack(side="right")
        self.escala = ttk.Scale(
            self,
            from_=desde,
            to=hasta,
            variable=variable,
            orient="horizontal",
            command=self._al_mover,
        )
        self.escala.pack(fill="x", pady=(6, 0))
        self._al_mover()

    def _al_mover(self, _valor: str | None = None) -> None:
        redondeado = round(round(self.variable.get() / self.paso) * self.paso, 4)
        if redondeado != self.variable.get():
            self.variable.set(redondeado)
        self.texto_valor.configure(text=f"{redondeado:.0%}")


class TablaRecorrido(Tarjeta):
    """Tabla con el orden de visita, el tramo y la distancia acumulada."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=0)
        cabecera = tk.Frame(self.cuerpo, background=Paleta.SUPERFICIE)
        cabecera.pack(fill="x", padx=16, pady=(14, 8))
        ttk.Label(cabecera, text="Recorrido", style="TarjetaTitulo.TLabel").pack(
            side="left"
        )
        self.resumen = ttk.Label(cabecera, text="", style="TarjetaAyuda.TLabel")
        self.resumen.pack(side="right")
        tk.Frame(self.cuerpo, background=Paleta.BORDE, height=1).pack(fill="x")

        contenedor = tk.Frame(self.cuerpo, background=Paleta.SUPERFICIE)
        contenedor.pack(fill="both", expand=True, padx=(6, 0), pady=(0, 6))
        columnas = ("orden", "ciudad", "tramo", "acumulado")
        self.arbol = ttk.Treeview(
            contenedor, columns=columnas, show="headings", selectmode="browse"
        )
        encabezados = (
            ("orden", "#", 38, "center", False),
            ("ciudad", "CIUDAD", 150, "w", True),
            ("tramo", "TRAMO", 72, "e", False),
            ("acumulado", "ACUM.", 78, "e", False),
        )
        for clave, titulo, ancho, ancla, estirar in encabezados:
            self.arbol.heading(clave, text=titulo, anchor=ancla)
            self.arbol.column(clave, width=ancho, minwidth=ancho, anchor=ancla, stretch=estirar)
        self.arbol.tag_configure("par", background="#1a1d28")
        self.arbol.tag_configure("inicio", foreground=Paleta.TURQUESA)
        barra = ttk.Scrollbar(contenedor, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=barra.set)
        self.arbol.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        self.vacio = tk.Label(
            contenedor,
            text="Ejecutá el algoritmo para\nver el orden de visita.",
            background=Paleta.SUPERFICIE,
            foreground=Paleta.TEXTO_TENUE,
            font=(Fuentes.BASE, 10),
            justify="center",
        )
        self.vacio.place(relx=0.5, rely=0.45, anchor="center")

    def limpiar(self) -> None:
        self.arbol.delete(*self.arbol.get_children())
        self.resumen.configure(text="")
        self.vacio.place(relx=0.5, rely=0.45, anchor="center")

    def mostrar(self, ruta: RutaTSP, problema: ProblemaTSP) -> None:
        self.arbol.delete(*self.arbol.get_children())
        self.vacio.place_forget()
        acumulado = 0
        anterior: int | None = None
        ultimo = len(ruta.recorrido) - 1
        for posicion, indice in enumerate(ruta.recorrido):
            tramo = 0 if anterior is None else problema.distancia(anterior, indice)
            acumulado += tramo
            etiquetas = ["par"] if posicion % 2 else []
            if posicion in (0, ultimo):
                etiquetas.append("inicio")
            self.arbol.insert(
                "",
                "end",
                values=(
                    "●" if posicion in (0, ultimo) else posicion,
                    problema.nombre_ciudad(indice),
                    "—" if anterior is None else formatear_entero(tramo),
                    formatear_entero(acumulado),
                ),
                tags=etiquetas,
            )
            anterior = indice
        self.resumen.configure(
            text=f"{len(set(ruta.recorrido))} ciudades · {formatear_entero(acumulado)} km"
        )


class PanelMapa(Tarjeta):
    """Mapa interactivo (OpenStreetMap / CARTO) con la ruta dibujada encima."""

    ESTILOS: dict[str, tuple[str, bool]] = {
        "Oscuro": ("https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png", True),
        "Claro": ("https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", False),
        "OpenStreetMap": ("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", False),
    }
    CENTRO = (-39.5, -64.0)
    ZOOM_INICIAL = 4
    ZOOM_NOMBRES = 6
    _iconos: dict[str, ImageTk.PhotoImage] = {}

    def __init__(self, master: tk.Misc, titulo: str = "Mapa del recorrido") -> None:
        super().__init__(master, padding=0)
        self._ruta: RutaTSP | None = None
        self._problema: ProblemaTSP | None = None
        self._oscuro = True
        self._mostrando_nombres = False

        barra = tk.Frame(self.cuerpo, background=Paleta.SUPERFICIE)
        barra.pack(fill="x", padx=16, pady=10)
        ttk.Label(barra, text=titulo, style="TarjetaTitulo.TLabel").pack(side="left")
        ttk.Button(barra, text="+", width=3, style="Icono.TButton", command=self.acercar).pack(
            side="right"
        )
        ttk.Button(barra, text="⟲", width=3, style="Icono.TButton", command=self.centrar).pack(
            side="right", padx=4
        )
        ttk.Button(barra, text="−", width=3, style="Icono.TButton", command=self.alejar).pack(
            side="right"
        )
        self.estilo_mapa = tk.StringVar(value="OpenStreetMap")
        selector = ttk.Combobox(
            barra,
            textvariable=self.estilo_mapa,
            values=tuple(self.ESTILOS),
            state="readonly",
            width=14,
        )
        selector.pack(side="right", padx=(0, 12))
        selector.bind("<<ComboboxSelected>>", self._cambiar_estilo)
        tk.Frame(self.cuerpo, background=Paleta.BORDE, height=1).pack(fill="x")

        self.mapa = TkinterMapView(self.cuerpo, corner_radius=0)
        self.mapa.pack(fill="both", expand=True)
        self.mapa.canvas.configure(background=Paleta.FONDO)
        for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.mapa.canvas.bind(evento, self._al_zoom_rueda, add="+")

        leyenda = tk.Frame(self.cuerpo, background=Paleta.SUPERFICIE)
        leyenda.pack(fill="x", padx=16, pady=8)
        for color, texto in (
            (Paleta.TURQUESA, "Partida"),
            ("#b7a6ff", "Capital"),
            (Paleta.CORAL, "Ruta"),
        ):
            tk.Label(
                leyenda, text="●", foreground=color, background=Paleta.SUPERFICIE,
                font=(Fuentes.BASE, 10),
            ).pack(side="left")
            tk.Label(
                leyenda, text=texto, foreground=Paleta.TEXTO_SUAVE,
                background=Paleta.SUPERFICIE, font=(Fuentes.BASE, 9),
            ).pack(side="left", padx=(3, 14))
        tk.Label(
            leyenda,
            text="Rueda: zoom · Arrastrar: mover",
            foreground=Paleta.TEXTO_TENUE,
            background=Paleta.SUPERFICIE,
            font=(Fuentes.BASE, 9),
        ).pack(side="right")

        self._crear_iconos()
        self._cambiar_estilo()
        self.centrar()

    # -- iconos -------------------------------------------------------------
    def _crear_iconos(self) -> None:
        if PanelMapa._iconos:
            return
        PanelMapa._iconos = {
            "capital": self._circulo(12, "#b7a6ff", "#ffffff", 2),
            "inicio": self._circulo(20, Paleta.TURQUESA, "#ffffff", 3),
        }

    def _circulo(self, diametro: int, relleno: str, borde: str, grosor: int) -> ImageTk.PhotoImage:
        escala = 4
        lado = diametro * escala
        imagen = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
        dibujo = ImageDraw.Draw(imagen)
        dibujo.ellipse((0, 0, lado - 1, lado - 1), fill=borde)
        margen = grosor * escala
        dibujo.ellipse((margen, margen, lado - 1 - margen, lado - 1 - margen), fill=relleno)
        imagen = imagen.resize((diametro, diametro), Image.LANCZOS)
        return ImageTk.PhotoImage(imagen, master=self)

    # -- controles ----------------------------------------------------------
    def _cambiar_estilo(self, _evento: tk.Event | None = None) -> None:
        url, oscuro = self.ESTILOS[self.estilo_mapa.get()]
        self._oscuro = oscuro
        self.mapa.set_tile_server(url, max_zoom=19)
        self.redibujar()

    def centrar(self) -> None:
        self.mapa.set_position(*self.CENTRO)
        self.mapa.set_zoom(self.ZOOM_INICIAL)
        self._revisar_nombres(forzar=True)

    def acercar(self) -> None:
        self.mapa.set_zoom(round(self.mapa.zoom) + 1)
        self._revisar_nombres()

    def alejar(self) -> None:
        self.mapa.set_zoom(round(self.mapa.zoom) - 1)
        self._revisar_nombres()

    def _al_zoom_rueda(self, _evento: tk.Event) -> None:
        self.after(150, self._revisar_nombres)

    def _revisar_nombres(self, forzar: bool = False) -> None:
        mostrar = round(self.mapa.zoom) >= self.ZOOM_NOMBRES
        if forzar or mostrar != self._mostrando_nombres:
            self._mostrando_nombres = mostrar
            self.redibujar()

    # -- dibujo -------------------------------------------------------------
    def mostrar_ruta(self, ruta: RutaTSP, problema: ProblemaTSP) -> None:
        self._ruta = ruta
        self._problema = problema
        self.redibujar()

    def limpiar(self) -> None:
        self._ruta = None
        self._problema = None
        self.redibujar()

    def redibujar(self) -> None:
        self.mapa.delete_all_marker()
        self.mapa.delete_all_path()
        self.mapa.delete_all_polygon()
        color_texto = "#f1f2f6" if self._oscuro else "#1b1e28"
        fuente = (Fuentes.TITULO, 9)

        if self._ruta is not None and self._problema is not None:
            posiciones = [
                self._posicion(self._problema.nombre_ciudad(indice))
                for indice in self._ruta.recorrido
            ]
            if len(posiciones) >= 2:
                sombra = "#3b1e16" if self._oscuro else "#ffd9cc"
                self.mapa.set_path(posiciones, color=sombra, width=8)
                self.mapa.set_path(posiciones, color=Paleta.CORAL, width=3)

        inicio = None
        if self._ruta is not None and self._problema is not None:
            inicio = self._problema.nombre_ciudad(self._ruta.recorrido[0])
        for nombre in COORDENADAS_CAPITALES:
            if nombre == inicio:
                continue
            latitud, longitud = self._posicion(nombre)
            self.mapa.set_marker(
                latitud,
                longitud,
                text=nombre if self._mostrando_nombres else None,
                text_color=color_texto,
                font=fuente,
                icon=self._iconos["capital"],
                icon_anchor="center",
            )
        if inicio is not None:
            latitud, longitud = self._posicion(inicio)
            self.mapa.set_marker(
                latitud,
                longitud,
                text=f"Partida · {inicio}" if self._mostrando_nombres else "Partida",
                text_color=Paleta.TURQUESA,
                font=(Fuentes.TITULO, 10),
                icon=self._iconos["inicio"],
                icon_anchor="center",
            )

    @staticmethod
    def _posicion(nombre: str) -> tuple[float, float]:
        longitud, latitud = COORDENADAS_CAPITALES[nombre]
        return latitud, longitud


def crear_control_segmentado(
    master: tk.Misc,
    variable: tk.StringVar,
    opciones: Sequence[tuple[str, str]],
    al_cambiar: Callable[[], None] | None = None,
) -> tk.Frame:
    """Grupo de Radiobuttons con aspecto de control segmentado."""
    marco = tk.Frame(master, background=Paleta.SUPERFICIE)
    for columna, (valor, texto) in enumerate(opciones):
        marco.columnconfigure(columna, weight=1, uniform="segmento")
        ttk.Radiobutton(
            marco,
            text=texto,
            value=valor,
            variable=variable,
            style="Segmento.Toolbutton",
            command=al_cambiar,
        ).grid(row=0, column=columna, sticky="ew", padx=(0 if columna == 0 else 2, 0))
    return marco
