from ..SAP import SAP
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By

import pandas as pd

class FB03(SAP):
    titulo_pagina_inicio = 'Visualizar documento: Acceso a vista de libro mayor'
    
    def __init__(self, base_url: str, usuario: str, clave: str, usuario_microsoft: str = '', clave_microsoft: str = '', driver = None, dev: bool = False):
        super().__init__(
            base_url=base_url, 
            usuario=usuario,
            clave=clave,
            usuario_microsoft=usuario_microsoft,
            clave_microsoft=clave_microsoft,
            driver=driver, 
            dev=dev
        )
    
    def finalizar(self) -> None:
        """ Finaliza la transacción FB03. """
        self.mostrar("Finalizando transacción FB03")
        self.enviar_tecla_ventana('SHIFT', 'F3')
    
    def guardar(self) -> None:
        """ Guarda los cambios realizados en la transacción FB03. """
        self.mostrar("Guardando cambios en la transacción FB03")
        self.enviar_tecla_ventana('CTRL', 'S')
        self.demora()
        
    def buscar_documento(self, numero_documento: str, sociedad: str = 'LGA0', ejercicio: str = '2025') -> bool:
        """
        Busca un documento contable en la transacción FB03 de SAP.
        
        Ingresa el número de documento, la sociedad y el ejercicio en los campos correspondientes de la interfaz de SAP, y ejecuta la búsqueda presionando la tecla Enter.
        
        ---
        ### Ejemplo
        ```python
        sap = FB03()
        sap.buscar_documento(numero_documento='1234567890', sociedad='LGA0', ejercicio='2025')
        ```
        >>> True  # Si la búsqueda se realizó correctamente
        
        ---
        ### Raises
        #### ValueError
        - Si el número de documento no es un string numérico de entre 7 y 14 caracteres.
        - Si la sociedad no es 'LGA0' o 'AGF0'.
        - Si el ejercicio no es un año en formato YYYY.
        
        #### Exception
        - No se pudo ingresar el texto en los campos de SAP.
        - No se pudo enviar la tecla Enter para ejecutar la búsqueda.
        - No se pudo acceder a la página de visualización del documento después de 3 segundos.
        """
        if not numero_documento or not numero_documento.isdigit() or not (7 <= len(numero_documento) <= 14):
            raise ValueError("El número de documento debe ser un string numérico de entre 7 y 14 caracteres")
        if not sociedad or sociedad not in ['LGA0', 'AGF0']:
            raise ValueError("La sociedad debe ser 'LGA0' o 'AGF0'")
        if not ejercicio or not ejercicio.isdigit() or len(ejercicio) != 4:
            raise ValueError("El ejercicio debe ser un año en formato YYYY")
        
        self.mostrar(f"Buscando documento {numero_documento} en sociedad {sociedad} y ejercicio {ejercicio}")
        
        # Ingresar el número de documento
        self.ingresar_texto(By.XPATH, f"//*[@title='Número de un documento contable']", numero_documento)
        
        # Ingresar la sociedad
        self.ingresar_texto(By.XPATH, f"//*[@title='Sociedad']", sociedad) 
        
        # Ingresar el ejercicio
        self.ingresar_texto(By.XPATH, f"//*[@title='Ejercicio']", ejercicio)
        
        # Presionar Enter para buscar
        self.enviar_tecla_ventana('ENTER')
        
        # Esperar a que se cargue la alerta de transacción
        alerta = self.buscar_alerta_transaccion()
        if alerta:
            if alerta['isError']:
                self.mostrar(f"Error al buscar el documento: {alerta['texto']}", True)
                self.enviar_tecla_ventana('ESC')
                self.finalizar()
                self.cerrar_navegador()
                raise Exception(f"Error al buscar el documento: {alerta['texto']}")
        
        # Verificar si se ha cargado la página correctamente
        nuevo_titulo_pagina = 'Visualizar documento: Resumen de documento contable'
        reintentos = 0
        while self.driver.title != nuevo_titulo_pagina and reintentos < 3:
            self.demora(1)
            reintentos += 1
            
        if reintentos >= 3:
            self.mostrar("No se pudo acceder a la página de visualización del documento después de 3 segundos", True)
            self.finalizar()
            self.cerrar_navegador()
            raise Exception("No se pudo acceder a la página de visualización del documento")
        
        self.mostrar("Documento encontrado y visualizado correctamente")
        return True  
    
        
    