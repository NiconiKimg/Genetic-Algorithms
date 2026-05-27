import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import Optional, Any
from individuo import Individuo

class Logger:
    """Registra y almacena el historial evolutivo de la población"""
    historial: list[tuple[float, float, float, float, Individuo]]
    df_historial: pd.DataFrame

    def __init__(self) -> None:
        """Inicializa las estructuras para almacenar las métricas de evolución"""
        self.historial = []
        self.df_historial = pd.DataFrame(columns=[
            'Ciclo', 'Minimo', 'Maximo', 'Promedio', 'Desviacion', 
            'Mejor_Cromosoma', 'Mejor_Valor_Obj', 'Mejor_Fitness'
        ])
    
    def agregar_datos(self, minimo: float, maximo: float, promedio: float, desviacion: float, mejor_individuo: Individuo) -> None:
        """Agrega un registro con las estadísticas de la generación actual"""
        self.historial.append((minimo, maximo, promedio, desviacion, mejor_individuo))
        genes_str = "".join(str(g) for g in mejor_individuo.genes)
        nueva_fila = pd.DataFrame([{
            'Ciclo': len(self.historial), 
            'Minimo': minimo, 
            'Maximo': maximo, 
            'Promedio': promedio, 
            'Desviacion': desviacion,
            'Mejor_Cromosoma': genes_str,
            'Mejor_Valor_Obj': mejor_individuo.valor_funcion_objetivo,
            'Mejor_Fitness': mejor_individuo.fitness
        }])
    
        # Concatenas el nuevo registro al DataFrame existente
        self.df_historial = pd.concat([self.df_historial, nueva_fila], ignore_index=True)



    def export_datos(self, directorio_salida: str, nombre_base: str) -> None:
        """Exporta el historial a una tabla y a graficos"""

        os.makedirs(directorio_salida, exist_ok=True)

        plot = Plot_Writer()
        plot.preparar_grafico(titulo=f"Evolución - {nombre_base}", xlabel="Ciclo", ylabel="Métricas")

        ruta_csv = os.path.join(directorio_salida, f"{nombre_base}_stats.csv")
        ruta_tabla_md = os.path.join(directorio_salida, f"{nombre_base}_tabla.md")
        ruta_grafico = os.path.join(directorio_salida, f"{nombre_base}_grafico.png")
        ruta_convergencia = os.path.join(directorio_salida, f"{nombre_base}_convergencia.png")

        table_writer = Table_Writer()
        table_writer.exportar_tabla(self.df_historial, ruta_csv, ruta_tabla_md)

        plot.export_grafico(self.df_historial, 'Ciclo', ['Minimo', 'Maximo', 'Promedio','Desviacion'], filename=ruta_grafico)
        plot.export_grafico_convergencia(self.df_historial, filename=ruta_convergencia)

    def export_metadata(self, directorio_salida: str, nombre_base: str, tiempo_ejecucion: float, aptitud_maxima: float) -> None:
        """Exporta metadatos de tiempo, aptitud máxima y desviación estándar promedio"""
        
        os.makedirs(directorio_salida, exist_ok=True)
        
        ruta_metadata = os.path.join(directorio_salida, f"{nombre_base}_metadata.txt")
        
        # Calcular desviación estándar promedio
        desviacion_promedio = float(self.df_historial['Desviacion'].mean())
        
        with open(ruta_metadata, 'w') as f:
            f.write(f"Ejecución: {nombre_base}\n")
            f.write(f"Tiempo de Computo: {tiempo_ejecucion:.6f} segundos\n")
            f.write(f"Aptitud Máxima: {aptitud_maxima:.10f}\n")
            f.write(f"Desviación Estándar Promedio: {desviacion_promedio:.10f}\n")

class Plot_Writer:
    """Genera representaciones gráficas de las métricas de evolución"""
    fig: Optional[Any]
    ax: Optional[Any]

    def __init__(self) -> None:
        """Inicializa el contenedor de la figura y los ejes de matplotlib"""
        self.fig = None
        self.ax = None

    def preparar_grafico(self, titulo: str = "", xlabel: str = "", ylabel: str = "", figsize: tuple[int, int] = (8,5)) -> None:
        """Inicializa las propiedades del lienzo y ejes para el gráfico"""
        self.fig, self.ax = plt.subplots(figsize=figsize)

        self.ax.set_title(titulo)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True)

    def export_grafico(self, df: pd.DataFrame, x_col: str, y_cols: list[str], filename: str = "grafico.png") -> None:
        """Guarda un gráfico con la evolución de múltiples columnas indicadas"""
        if self.ax is None or self.fig is None:
            raise Exception("Primero llamá a preparar_grafico()")

        x = df[x_col]

        for col in y_cols:
            self.ax.plot(x, df[col], label=col)

        self.ax.legend()
        self.fig.savefig(filename)
        plt.close(self.fig)

    def export_grafico_convergencia(self, df: pd.DataFrame, filename: str) -> None:
        """Genera un gráfico de doble eje Y que analiza la convergencia frente a la diversidad"""
        fig, ax1 = plt.subplots(figsize=(8, 5))

        color = 'forestgreen'
        ax1.set_xlabel('Ciclo / Generación', fontsize=10)
        ax1.set_ylabel('Aptitud (Máxima y Promedio)', color=color, fontsize=10)
        line1 = ax1.plot(df['Ciclo'], df['Maximo'], color=color, linewidth=2, label='Mejor Aptitud (Max)')
        line2 = ax1.plot(df['Ciclo'], df['Promedio'], color='darkorange', linewidth=1.5, linestyle='-', label='Aptitud Promedio (Mean)')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_ylim(-0.05, 1.05)
        ax1.grid(True, linestyle=':', alpha=0.5)

        line3 = ax1.axhline(y=1.0, color='crimson', linestyle='--', linewidth=1.5, label='Óptimo Global Teórico (1.0)')

        ax2 = ax1.twinx()
        color2 = 'purple'
        ax2.set_ylabel('Diversidad (Desviación Estándar)', color=color2, fontsize=10)
        line4 = ax2.plot(df['Ciclo'], df['Desviacion'], color=color2, linewidth=1.8, linestyle=':', label='Desviación Estándar (StdDev)')
        ax2.tick_params(axis='y', labelcolor=color2)
        
        lines = line1 + line2 + [line3] + line4
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='center right', frameon=True, framealpha=0.9, shadow=True)

        plt.title('Dinámica de Convergencia: Progreso de Aptitud vs. Pérdida de Diversidad', fontsize=11, fontweight='bold', pad=15)
        fig.tight_layout()
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close(fig)

        
class Table_Writer:
    """Exporta dataframes tabulares a formatos legibles como CSV y Markdown"""
    def __init__(self) -> None:
        """Inicializa el escritor de tablas"""

    def exportar_tabla(self, df: pd.DataFrame, filepath_csv: str, filepath_md: str) -> None:
        """Exporta la tabla a CSV y genera un reporte Markdown"""
        df.to_csv(filepath_csv, index=False)

        df_formatted = df.copy()
        
        float_cols = ['Minimo', 'Maximo', 'Promedio', 'Desviacion', 'Mejor_Valor_Obj', 'Mejor_Fitness']
        for col in float_cols:
            if col in df_formatted.columns:
                df_formatted[col] = df_formatted[col].map(lambda x: f"{x:.8f}" if isinstance(x, (int, float)) else x)
        
        headers = list(df_formatted.columns)
        header_line = "| " + " | ".join(headers) + " |"
        separator_line = "| " + " | ".join([" :---: " for _ in headers]) + " |"
        
        lines = [
            f"# Reporte de Evolución Poblacional\n",
            f"Estadísticas detalladas del algoritmo genético por cada ciclo/generación:\n",
            header_line,
            separator_line
        ]
        
        for _, row in df_formatted.iterrows():
            row_str = "| " + " | ".join(str(val) for val in row) + " |"
            lines.append(row_str)
            
        with open(filepath_md, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
            f.write("\n")




