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



    def export_datos(self, directorio_salida: str, nombre_base: str, poblacion: Optional[Any] = None) -> None:
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

        if poblacion is not None:
            ruta_distribucion = os.path.join(directorio_salida, f"{nombre_base}_distribucion_final.png")
            ruta_hamming = os.path.join(directorio_salida, f"{nombre_base}_diversidad_hamming.png")
            plot.export_grafico_distribucion_final(poblacion, filename=ruta_distribucion)
            plot.export_grafico_diversidad_hamming(poblacion, filename=ruta_hamming)

    def export_metadata(self, directorio_salida: str, nombre_base: str, tiempo_ejecucion: float, aptitud_maxima: float) -> None:
        """Exporta metadatos de tiempo, aptitud máxima y desviación estándar promedio"""
        
        os.makedirs(directorio_salida, exist_ok=True)
        
        ruta_metadata = os.path.join(directorio_salida, f"{nombre_base}_metadata.txt")
        
        # Calcular desviación estándar promedio
        desviacion_promedio = float(self.df_historial['Desviacion'].mean())
        
        # Identificar el ciclo en que se alcanzó por primera vez la aptitud máxima global
        ciclo_max_aptitud = self.df_historial.loc[self.df_historial['Maximo'].idxmax(), 'Ciclo']
        
        with open(ruta_metadata, 'w') as f:
            f.write(f"Ejecución: {nombre_base}\n")
            f.write(f"Tiempo de Computo: {tiempo_ejecucion:.6f} segundos\n")
            f.write(f"Aptitud Máxima: {aptitud_maxima:.10f}\n")
            f.write(f"Generación de Aptitud Máxima: {ciclo_max_aptitud}\n")
            f.write(f"Desviación Estándar Promedio: {desviacion_promedio:.10f}\n")

class Plot_Writer:
    """Genera y exporta las visualizaciones gráficas del algoritmo genético"""
    fig: Optional[Any]
    ax: Optional[Any]

    def __init__(self) -> None:
        """Inicializa la instancia del graficador"""
        self.fig = None
        self.ax = None

    def preparar_grafico(self, titulo: str = "", xlabel: str = "", ylabel: str = "", figsize: tuple[int, int] = (9, 6.5)) -> None:
        """Configura el lienzo de matplotlib para los gráficos de evolución"""
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.ax.set_title(titulo, fontsize=12, fontweight='bold', pad=12)
        self.ax.set_xlabel(xlabel, fontsize=10)
        self.ax.set_ylabel(ylabel, fontsize=10)
        self.ax.grid(True, linestyle=':', alpha=0.5, color='gray')

    def export_grafico(self, df: pd.DataFrame, x_col: str, y_cols: list[str], filename: str = "grafico.png") -> None:
        """Exporta curvas de evolución temporal de las métricas básicas"""
        if self.ax is None or self.fig is None:
            raise Exception("Primero llamá a preparar_grafico()")

        x = df[x_col]
        colors = {
            'Minimo': '#27ae60',
            'Maximo': '#2b5c8f',
            'Promedio': '#e67e22',
            'Desviacion': '#8e44ad'
        }

        for col in y_cols:
            self.ax.plot(x, df[col], label=col, linewidth=2, color=colors.get(col))

        self.ax.legend(frameon=True, framealpha=0.9)
        self.fig.tight_layout()
        self.fig.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close(self.fig)

    def export_grafico_convergencia(self, df: pd.DataFrame, filename: str) -> None:
        """Genera un gráfico de doble eje Y para analizar convergencia vs diversidad"""
        fig, ax1 = plt.subplots(figsize=(9, 6.5))

        color = '#27ae60'
        ax1.set_xlabel('Ciclo / Generación', fontsize=10)
        ax1.set_ylabel('Aptitud (Máxima y Promedio)', color=color, fontsize=10)
        line1 = ax1.plot(df['Ciclo'], df['Maximo'], color='#2b5c8f', linewidth=2.5, label='Mejor Aptitud (Max)')
        line2 = ax1.plot(df['Ciclo'], df['Promedio'], color='#e67e22', linewidth=1.8, linestyle='-', label='Aptitud Promedio (Mean)')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_ylim(-0.05, 1.05)
        ax1.grid(True, linestyle=':', alpha=0.5, color='gray')

        line3 = ax1.axhline(y=1.0, color='crimson', linestyle='--', linewidth=1.5, label='Óptimo Global Teórico (1.0)')

        ax2 = ax1.twinx()
        color2 = '#8e44ad'
        ax2.set_ylabel('Diversidad (Desviación Estándar)', color=color2, fontsize=10)
        line4 = ax2.plot(df['Ciclo'], df['Desviacion'], color=color2, linewidth=2, linestyle=':', label='Desviación Estándar (StdDev)')
        ax2.tick_params(axis='y', labelcolor=color2)
        
        lines = line1 + line2 + [line3] + line4
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='center right', frameon=True, framealpha=0.9)

        plt.title('Dinámica de Convergencia: Progreso de Aptitud vs. Pérdida de Diversidad', fontsize=12, fontweight='bold', pad=12)
        fig.tight_layout()
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def export_grafico_distribucion_final(self, poblacion: Any, filename: str) -> None:
        """Genera y guarda el gráfico del paisaje de aptitud y distribución de la población final"""
        import numpy as np

        individuos_ordenados_x = sorted(poblacion.individuos, key=lambda ind: ind.decodificar())
        if not individuos_ordenados_x:
            return

        n = len(individuos_ordenados_x)
        L = len(individuos_ordenados_x[0].genes)
        dominio_max = 2**L - 1

        fig, ax = plt.subplots(figsize=(11.5, 6.5))

        x_vals = np.linspace(0, dominio_max, 500)
        y_vals = [poblacion.funcion_objetivo(x) for x in x_vals]

        ax.plot(x_vals, y_vals, color='#2b5c8f', linewidth=2.5, label='Función Objetivo $f(x)$', zorder=1)
        ax.fill_between(x_vals, y_vals, color='#2b5c8f', alpha=0.08, zorder=1)

        fitnesses = [ind.fitness if ind.fitness is not None else 0.0 for ind in individuos_ordenados_x]
        max_fitness = max(fitnesses) if fitnesses else 1.0
        if max_fitness == 0:
            max_fitness = 1.0

        cmap = plt.get_cmap('plasma')

        # Asignar índices estables de izquierda a derecha (0 a n-1)
        individuos_con_index = list(enumerate(individuos_ordenados_x))

        # Ordenar por fitness descendente para la leyenda
        individuos_para_leyenda = sorted(individuos_con_index, key=lambda x: x[1].fitness if x[1].fitness is not None else 0.0, reverse=True)

        s_min = 150
        s_max = 1000

        # Graficar cada individuo uno a uno en orden de fitness descendente
        for idx, ind in individuos_para_leyenda:
            fit_val = ind.fitness if ind.fitness is not None else 0.0
            label = f"#{idx} (Fit: {fit_val:.3f})"
            size = s_min + (s_max - s_min) * (fit_val / max_fitness)**2
            color = cmap(idx / (n - 1)) if n > 1 else cmap(0.5)
            
            ax.scatter(ind.decodificar(), ind.valor_funcion_objetivo, s=size, c=[color], 
                       alpha=0.6, edgecolors='black', linewidths=1.5, label=label, zorder=2)

        # Agregar anotaciones estables sobre los círculos
        for idx, ind in individuos_con_index:
            ax.annotate(f'#{idx}', (ind.decodificar(), ind.valor_funcion_objetivo), xytext=(0, 8), textcoords='offset points', 
                         ha='center', va='bottom', fontsize=9, fontweight='bold',
                         bbox=dict(boxstyle='round,pad=0.25', fc='white', alpha=0.9, ec='#cccccc', lw=0.8))

        nombre_ejecucion = os.path.basename(filename).replace("_distribucion_final.png", "").replace("_", " ").title()
        ax.set_title(f'Distribución de la Población Final y Paisaje de Aptitud\n({nombre_ejecucion})', fontsize=12, fontweight='bold', pad=12)
        ax.set_xlabel('Valor Decodificado del Cromosoma ($x$)', fontsize=10)
        ax.set_ylabel('Valor de la Función Objetivo $f(x)$', fontsize=10)
        ax.set_xlim(-0.02 * dominio_max, 1.02 * dominio_max)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle=':', alpha=0.5, color='gray')
        
        # Posicionar la leyenda ordenada al costado derecho
        ax.legend(bbox_to_anchor=(1.02, 1.0), loc='upper left', frameon=True, framealpha=0.9)

        fig.tight_layout()
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def export_grafico_diversidad_hamming(self, poblacion: Any, filename: str) -> None:
        """Genera y guarda la matriz de distancia de Hamming para analizar diversidad genotípica"""
        import numpy as np

        individuos = sorted(poblacion.individuos, key=lambda ind: ind.decodificar())
        if not individuos:
            return

        n = len(individuos)
        L = len(individuos[0].genes)

        fig, ax = plt.subplots(figsize=(9, 7.5))

        hamming_matrix = np.zeros((n, n), dtype=int)
        for i in range(n):
            for j in range(n):
                hamming_matrix[i, j] = sum(g1 != g2 for g1, g2 in zip(individuos[i].genes, individuos[j].genes))

        mask = np.triu(np.ones_like(hamming_matrix, dtype=bool), k=1)
        masked_matrix = np.ma.masked_where(mask, hamming_matrix)

        im = ax.imshow(masked_matrix, cmap='Blues', aspect='equal', zorder=1, interpolation='nearest')
        
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Distancia de Hamming (Bits Diferentes)', rotation=270, labelpad=18, fontsize=10)

        ax.grid(False)

        for i in range(1, n):
            ax.hlines(i - 0.5, -0.5, i - 0.5, colors='white', linewidths=2.5, zorder=2)
        for j in range(1, n):
            ax.vlines(j - 0.5, j - 0.5, n - 0.5, colors='white', linewidths=2.5, zorder=2)

        ax.vlines(-0.5, -0.5, n - 0.5, colors='white', linewidths=2.5, zorder=2)
        ax.hlines(n - 0.5, -0.5, n - 0.5, colors='white', linewidths=2.5, zorder=2)
        for i in range(n):
            ax.hlines(i - 0.5, i - 0.5, i + 0.5, colors='white', linewidths=2.5, zorder=2)
            ax.vlines(i + 0.5, i - 0.5, i + 0.5, colors='white', linewidths=2.5, zorder=2)

        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels([f'#{i}' for i in range(n)])
        ax.set_yticklabels([f'#{i}' for i in range(n)])
        ax.set_xlabel('Individuo en el Paisaje', fontsize=10)
        ax.set_ylabel('Individuo en el Paisaje', fontsize=10)
        
        nombre_ejecucion = os.path.basename(filename).replace("_diversidad_hamming.png", "").replace("_", " ").title()
        ax.set_title(f'Diversidad Genotípica: Distancia de Hamming\n({nombre_ejecucion})', fontsize=12, fontweight='bold', pad=12)

        max_dist = masked_matrix.max()
        if max_dist == 0:
            max_dist = 1

        for i in range(n):
            for j in range(i + 1):
                val = hamming_matrix[i, j]
                text_color = 'white' if (val / max_dist) > 0.45 else '#0f2c59'
                ax.text(j, i, str(val), ha='center', va='center', color=text_color, fontweight='bold', fontsize=10)

        ax.set_xlim(-0.5, n - 0.5)
        ax.set_ylim(n - 0.5, -0.5)

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




