# src/Excel/Excel.py

# Librerías para el manejo de la consola
from .Terminal import Terminal

# Librerías para el manejo de archivos excel
from openpyxl import Workbook
from openpyxl import load_workbook

# Librerías para el manejo de datos
import pandas as pd

class Excel(Terminal):
    """ Clase para leer archivos excel """
    def __init__(self, ruta:str):
        self.ruta = ruta
    
    def leer_excel(self, hoja:str) -> pd.DataFrame | None:
        """ Lee un archivo excel """
        try: 
            dF = pd.read_excel(self.ruta, sheet_name=hoja, engine='openpyxl', dtype=str)
        except Exception as e:
            self.mostrar(f"Ocurrió un error al leer el archivo {self.ruta}", True)
            return None
        
        return dF 