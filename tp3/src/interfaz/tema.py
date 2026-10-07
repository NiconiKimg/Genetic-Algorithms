"""Paleta de colores, tipografias y estilos ttk de la interfaz del TP3."""

import sys
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk


class Paleta:
    """Colores del tema oscuro."""

    FONDO = "#0e1016"
    BARRA_LATERAL = "#0a0c11"
    SUPERFICIE = "#161922"
    SUPERFICIE_2 = "#1e2230"
    SUPERFICIE_3 = "#272c3d"
    BORDE = "#262b3a"
    BORDE_FUERTE = "#363c50"
    TEXTO = "#e7e9f0"
    TEXTO_SUAVE = "#9aa1b4"
    TEXTO_TENUE = "#646b80"
    ACENTO = "#7c5cff"
    ACENTO_HOVER = "#6b4cf0"
    ACENTO_PRESIONADO = "#5a3de0"
    ACENTO_SUAVE = "#2a2350"
    TURQUESA = "#2dd4a7"
    CORAL = "#ff7a59"
    AMBAR = "#f5b544"
    ROJO = "#ff5d6c"
    CELESTE = "#4cc3ff"


def _elegir_fuente(*candidatas: str) -> str:
    disponibles = set(tkfont.families())
    for candidata in candidatas:
        if candidata in disponibles:
            return candidata
    return "TkDefaultFont"


class Fuentes:
    """Tipografias resueltas una vez creada la ventana raiz."""

    BASE = "Segoe UI"
    TITULO = "Segoe UI Semibold"
    MONO = "Consolas"

    @classmethod
    def resolver(cls) -> None:
        cls.BASE = _elegir_fuente("Segoe UI", "Inter", "Helvetica Neue", "Arial")
        cls.TITULO = _elegir_fuente(
            "Segoe UI Semibold", "Segoe UI", "Inter SemiBold", "Helvetica Neue"
        )
        cls.MONO = _elegir_fuente("Cascadia Mono", "Consolas", "Menlo", "Courier New")


def aplicar_barra_titulo_oscura(root: tk.Tk) -> None:
    """Pide a Windows 10/11 una barra de titulo oscura (no-op en otros SO)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        valor = ctypes.c_int(1)
        for atributo in (20, 19):
            resultado = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, atributo, ctypes.byref(valor), ctypes.sizeof(valor)
            )
            if resultado == 0:
                break
    except Exception:
        pass


def configurar_estilos(root: tk.Tk) -> ttk.Style:
    """Configura todos los estilos ttk usados por la aplicacion."""
    Fuentes.resolver()
    p = Paleta
    estilo = ttk.Style(root)
    estilo.theme_use("clam")

    root.configure(background=p.FONDO)
    root.option_add("*Font", (Fuentes.BASE, 10))
    root.option_add("*TCombobox*Listbox.background", p.SUPERFICIE_2)
    root.option_add("*TCombobox*Listbox.foreground", p.TEXTO)
    root.option_add("*TCombobox*Listbox.selectBackground", p.ACENTO)
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
    root.option_add("*TCombobox*Listbox.borderWidth", 0)
    root.option_add("*TCombobox*Listbox.font", (Fuentes.BASE, 10))

    estilo.configure(
        ".",
        background=p.FONDO,
        foreground=p.TEXTO,
        bordercolor=p.BORDE,
        darkcolor=p.SUPERFICIE_2,
        lightcolor=p.SUPERFICIE_2,
        troughcolor=p.SUPERFICIE_2,
        focuscolor=p.ACENTO,
        selectbackground=p.ACENTO,
        selectforeground="#ffffff",
        insertcolor=p.TEXTO,
        font=(Fuentes.BASE, 10),
    )

    # Contenedores
    estilo.configure("TFrame", background=p.FONDO)
    estilo.configure("Tarjeta.TFrame", background=p.SUPERFICIE)

    # Etiquetas sobre el fondo
    estilo.configure("TLabel", background=p.FONDO, foreground=p.TEXTO)
    estilo.configure("H1.TLabel", font=(Fuentes.TITULO, 22), foreground=p.TEXTO)
    estilo.configure("Hero.TLabel", font=(Fuentes.TITULO, 30), foreground=p.TEXTO)
    estilo.configure(
        "Subtitulo.TLabel", font=(Fuentes.BASE, 11), foreground=p.TEXTO_SUAVE
    )
    estilo.configure("Suave.TLabel", foreground=p.TEXTO_SUAVE)
    estilo.configure("Estado.TLabel", foreground=p.TEXTO_SUAVE, font=(Fuentes.BASE, 9))

    # Etiquetas dentro de tarjetas
    estilo.configure("Tarjeta.TLabel", background=p.SUPERFICIE, foreground=p.TEXTO)
    estilo.configure(
        "TarjetaTitulo.TLabel",
        background=p.SUPERFICIE,
        foreground=p.TEXTO,
        font=(Fuentes.TITULO, 12),
    )
    estilo.configure(
        "TarjetaCampo.TLabel",
        background=p.SUPERFICIE,
        foreground=p.TEXTO_SUAVE,
        font=(Fuentes.BASE, 9),
    )
    estilo.configure(
        "TarjetaAyuda.TLabel",
        background=p.SUPERFICIE,
        foreground=p.TEXTO_TENUE,
        font=(Fuentes.BASE, 9),
    )
    estilo.configure(
        "TarjetaValor.TLabel",
        background=p.SUPERFICIE,
        foreground=p.ACENTO,
        font=(Fuentes.MONO, 10, "bold"),
    )

    # Botones
    estilo.configure(
        "TButton",
        background=p.SUPERFICIE_2,
        foreground=p.TEXTO,
        bordercolor=p.BORDE,
        lightcolor=p.SUPERFICIE_2,
        darkcolor=p.SUPERFICIE_2,
        focuscolor=p.SUPERFICIE_2,
        padding=(12, 7),
        relief="flat",
    )
    estilo.map(
        "TButton",
        background=[
            ("disabled", p.SUPERFICIE),
            ("pressed", p.SUPERFICIE_3),
            ("active", p.SUPERFICIE_3),
        ],
        foreground=[("disabled", p.TEXTO_TENUE)],
        bordercolor=[("active", p.BORDE_FUERTE)],
        lightcolor=[("active", p.SUPERFICIE_3)],
        darkcolor=[("active", p.SUPERFICIE_3)],
    )
    estilo.configure(
        "Acento.TButton",
        background=p.ACENTO,
        foreground="#ffffff",
        bordercolor=p.ACENTO,
        lightcolor=p.ACENTO,
        darkcolor=p.ACENTO,
        focuscolor=p.ACENTO,
        font=(Fuentes.TITULO, 11),
        padding=(16, 11),
    )
    estilo.map(
        "Acento.TButton",
        background=[
            ("disabled", p.ACENTO_SUAVE),
            ("pressed", p.ACENTO_PRESIONADO),
            ("active", p.ACENTO_HOVER),
        ],
        foreground=[("disabled", p.TEXTO_SUAVE)],
        bordercolor=[("disabled", p.ACENTO_SUAVE), ("active", p.ACENTO_HOVER)],
        lightcolor=[("disabled", p.ACENTO_SUAVE), ("active", p.ACENTO_HOVER)],
        darkcolor=[("disabled", p.ACENTO_SUAVE), ("active", p.ACENTO_HOVER)],
    )
    estilo.configure(
        "Icono.TButton",
        padding=(9, 4),
        font=(Fuentes.TITULO, 11),
        background=p.SUPERFICIE_2,
    )

    # Control segmentado (Radiobutton sin indicador)
    estilo.configure(
        "Segmento.Toolbutton",
        background=p.SUPERFICIE_2,
        foreground=p.TEXTO_SUAVE,
        bordercolor=p.BORDE,
        lightcolor=p.SUPERFICIE_2,
        darkcolor=p.SUPERFICIE_2,
        focuscolor=p.SUPERFICIE_2,
        padding=(10, 7),
        anchor="center",
    )
    estilo.map(
        "Segmento.Toolbutton",
        background=[("selected", p.ACENTO), ("active", p.SUPERFICIE_3)],
        foreground=[("selected", "#ffffff"), ("active", p.TEXTO)],
        bordercolor=[("selected", p.ACENTO)],
        lightcolor=[("selected", p.ACENTO)],
        darkcolor=[("selected", p.ACENTO)],
    )

    # Campos de entrada
    campos = dict(
        fieldbackground=p.SUPERFICIE_2,
        background=p.SUPERFICIE_2,
        foreground=p.TEXTO,
        bordercolor=p.BORDE,
        lightcolor=p.SUPERFICIE_2,
        darkcolor=p.SUPERFICIE_2,
        arrowcolor=p.TEXTO_SUAVE,
        insertcolor=p.TEXTO,
        padding=(8, 6),
    )
    mapa_campos = dict(
        fieldbackground=[("disabled", p.SUPERFICIE), ("readonly", p.SUPERFICIE_2)],
        foreground=[("disabled", p.TEXTO_TENUE)],
        bordercolor=[("focus", p.ACENTO), ("hover", p.BORDE_FUERTE)],
        lightcolor=[("focus", p.ACENTO)],
        darkcolor=[("focus", p.ACENTO)],
        arrowcolor=[("disabled", p.TEXTO_TENUE), ("hover", p.TEXTO)],
        background=[("active", p.SUPERFICIE_3)],
    )
    for nombre in ("TEntry", "TSpinbox", "TCombobox"):
        estilo.configure(nombre, **campos)
        estilo.map(nombre, **mapa_campos)
    estilo.map(
        "TCombobox",
        selectbackground=[("readonly", p.SUPERFICIE_2)],
        selectforeground=[("readonly", p.TEXTO)],
        **mapa_campos,
    )

    # Slider
    estilo.configure(
        "Horizontal.TScale",
        background=p.ACENTO,
        troughcolor=p.SUPERFICIE_3,
        bordercolor=p.SUPERFICIE,
        lightcolor=p.ACENTO,
        darkcolor=p.ACENTO,
        gripcount=0,
    )
    estilo.map("Horizontal.TScale", background=[("active", p.ACENTO_HOVER)])

    # Barra de progreso
    estilo.configure(
        "Acento.Horizontal.TProgressbar",
        background=p.ACENTO,
        troughcolor=p.SUPERFICIE_2,
        bordercolor=p.SUPERFICIE,
        lightcolor=p.ACENTO,
        darkcolor=p.ACENTO,
        thickness=4,
    )

    # Tabla
    estilo.configure(
        "Treeview",
        background=p.SUPERFICIE,
        fieldbackground=p.SUPERFICIE,
        foreground=p.TEXTO,
        bordercolor=p.SUPERFICIE,
        lightcolor=p.SUPERFICIE,
        darkcolor=p.SUPERFICIE,
        rowheight=28,
        font=(Fuentes.BASE, 10),
    )
    estilo.map(
        "Treeview",
        background=[("selected", p.ACENTO_SUAVE)],
        foreground=[("selected", p.TEXTO)],
    )
    estilo.configure(
        "Treeview.Heading",
        background=p.SUPERFICIE,
        foreground=p.TEXTO_TENUE,
        bordercolor=p.BORDE,
        lightcolor=p.SUPERFICIE,
        darkcolor=p.SUPERFICIE,
        relief="flat",
        font=(Fuentes.BASE, 9, "bold"),
        padding=(6, 6),
    )
    estilo.map("Treeview.Heading", background=[("active", p.SUPERFICIE_2)])
    estilo.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    # Barras de desplazamiento
    estilo.configure(
        "Vertical.TScrollbar",
        background=p.SUPERFICIE_3,
        troughcolor=p.SUPERFICIE,
        bordercolor=p.SUPERFICIE,
        lightcolor=p.SUPERFICIE_3,
        darkcolor=p.SUPERFICIE_3,
        arrowcolor=p.TEXTO_SUAVE,
        gripcount=0,
        arrowsize=12,
    )
    estilo.map("Vertical.TScrollbar", background=[("active", p.BORDE_FUERTE)])

    # Divisor redimensionable
    estilo.configure("TPanedwindow", background=p.FONDO)
    estilo.configure("Sash", sashthickness=10, gripcount=0, background=p.FONDO)

    return estilo
