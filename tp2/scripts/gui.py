"""Punto de entrada ejecutable para lanzar la Interfaz Gráfica del TP2."""

import sys
from pathlib import Path

# Agregar directorio tp2 al sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.gui_app import lanzar_gui

if __name__ == "__main__":
    lanzar_gui()
