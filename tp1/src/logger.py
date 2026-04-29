import pandas as pd
import matplotlib.pyplot as plt
import os

class Logger:
    def __init__(self):
        # Para debug
        self.historial = [] #Lista de tuplas para minimo, maximo y promedio de cada ciclo
        # Para mostrar resultados y graficos
        self.df_historial = pd.DataFrame(columns=['Ciclo', 'Minimo', 'Maximo', 'Promedio','Desviacion'])
    
    
    def agregar_datos(self, minimo, maximo, promedio, desviacion):
        self.historial.append((minimo, maximo, promedio, desviacion))
        nueva_fila = pd.DataFrame([{
        'Ciclo': len(self.historial), 
        'Minimo': minimo, 
        'Maximo': maximo, 
        'Promedio': promedio, 
        'Desviacion': desviacion
    }])
    
        # Concatenas el nuevo registro al DataFrame existente
        self.df_historial = pd.concat([self.df_historial, nueva_fila], ignore_index=True)



    def export_datos(self, directorio_salida, nombre_base):
        """Exporta el historial a una tabla y a graficos"""

        os.makedirs(directorio_salida, exist_ok=True)

        plot = Plot_Writer()
        plot.preparar_grafico(titulo=f"Evolución - {nombre_base}", xlabel="Ciclo", ylabel="Métricas")

        # Generar rutas dinámicas
        ruta_csv = os.path.join(directorio_salida, f"{nombre_base}_stats.csv")
        ruta_grafico = os.path.join(directorio_salida, f"{nombre_base}_grafico.png")

        #Exportar a tabla
        self.df_historial.to_csv(ruta_csv, index=False) 

        #Exportar a grafico
        plot.export_grafico(self.df_historial, 'Ciclo', ['Minimo', 'Maximo', 'Promedio','Desviacion'], filename=ruta_grafico)

class Plot_Writer:
    def __init__(self):
        self.fig = None
        self.ax = None

    def preparar_grafico(self, titulo="", xlabel="", ylabel="", figsize=(8,5)):
        self.fig, self.ax = plt.subplots(figsize=figsize)

        self.ax.set_title(titulo)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True)

    def export_grafico(self, df, x_col, y_cols, filename="grafico.png"):
        if self.ax is None:
            raise Exception("Primero llamá a preparar_grafico()")

        x = df[x_col]

        for col in y_cols:
            self.ax.plot(x, df[col], label=col)

        self.ax.legend()
        self.fig.savefig(filename)
        plt.close(self.fig)

        
class Table_Writer:
    def __init__(self):
        pass




