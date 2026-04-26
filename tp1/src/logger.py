import pandas as pd
import matplotlib.pyplot as plt

class Logger:
    def __init__(self):
        # Para debug
        self.historial = [] #Lista de tuplas para minimo, maximo y promedio de cada ciclo
        # Para mostrar resultados y graficos
        self.df_historial = pd.DataFrame(columns=['Ciclo', 'Minimo', 'Maximo', 'Promedio','Desviacion'])
    def agregar_datos(self, minimo, maximo, promedio, desviacion):
        self.historial.append((minimo, maximo, promedio, desviacion))
        self.df_historial = self.df_historial.append({'Ciclo': len(self.historial), 'Minimo': minimo, 'Maximo': maximo, 'Promedio': promedio,'Desviacion':desviacion}, ignore_index=True)


    def export_datos(self, filename):
        """Exporta el historial a una tabla y a graficos"""

        plot = Plot_Writer()
        plot.preparar_grafico(titulo="Evolución de la población", xlabel="Ciclo", ylabel="Minimo, Máximo Promedio, Desviación")
        #Exportar a tabla
        self.df_historial.to_csv(filename, index=False) # Ver si es necesario el Table_Writer

        #Exportar a grafico
        plot.export_grafico(self.df_historial, 'Ciclo', ['Minimo', 'Maximo', 'Promedio','Desviacion'])

        

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




