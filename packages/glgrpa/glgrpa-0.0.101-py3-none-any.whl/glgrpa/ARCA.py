# src/ARCA/ARCA.py

# Librerías para el manejo de la consola
from .Terminal import Terminal

# Librerías para el manejo del navegador
from .Chrome import Chrome

# Librerías para el manejo de los elementos de la página
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Librerías para el manejo de los tiempos
import time

class ARCA(Chrome, Terminal):    
    def __init__(self, usuario: str, clave: str, dev: bool = False):
        super().__init__(dev=dev)
        self.dev = dev   
        self.urlArca = r"https://auth.afip.gob.ar/contribuyente_/login.xhtml"
        self.titulo_pestaña = "Acceso con Clave Fiscal - ARCA"
        
        self.usuario_arca = usuario
        self.clave_arca = clave  
        
        self.reintentos_login = 3
        self.reintentos_aplicativo = 3
        
    def navegar_inicio(self):
        """ Navega a la página de inicio de ARCA """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de navegar.")
        
        self.mostrar("Navegando a la página de inicio de ARCA")
        self.navegar(self.urlArca)
        if self._driver.title == self.titulo_pestaña:
            self.mostrar("Página de inicio de ARCA cargada")
    
    def ingresar_credenciales(self):
        """ Ingresa las credenciales de ARCA y verifica que se haya ingresado correctamente """
        for intento in range(self.reintentos_login):
            if self.ingresar_usuario() and self.ingresar_contrasena():
                break
            else:
                self.mostrar(f"Ingreso incorrecto. Reintentando {intento + 1}/{self.reintentos_login}...", True)
                self.navegar_inicio()
                self.demora()
        else:
            self.mostrar("No se pudo ingresar después de varios intentos.", True)
    
    def ingresar_usuario(self) -> bool:
        """ Ingresa el usuario """
        self.mostrar("Ingresando usuario")
        self.ingresar_texto(By.ID, "F1:username", self.usuario_arca)
        self.demora()
        self.click_elemento(By.ID, "F1:btnSiguiente")
        if self.ingreso_correcto():
            self.mostrar("Usuario ingresado correctamente")
            return True
        return False
        
    def ingresar_contrasena(self) -> bool:
        """ Ingresa la contraseña """
        self.mostrar("Ingresando contraseña")
        self.ingresar_texto(By.ID, "F1:password", self.clave_arca)
        self.demora()
        self.click_elemento(By.ID, "F1:btnIngresar")
        if self.ingreso_correcto():
            self.mostrar("Contraseña ingresada correctamente")
            return True
        return False
        
    def ingreso_correcto(self) -> bool:
        """ Verifica que se haya ingresado correctamente """
        msg = self.encontrar_elemento(By.ID, "F1:msg", False)
        if msg:
            if msg.text == "Clave o usuario incorrecto" or msg.text == "El captcha ingresado es incorrecto.":
                return False
        else:
            captcha = self.encontrar_elemento(By.ID, "captcha", False)
            if captcha:
                return False
        
        return True
    
    def buscar_aplicativo(self, aplicativo:str, intentos:int=0) -> bool| None:
        """ Busca el aplicativo """
        aplicativo = aplicativo.lower()
        self.mostrar(f"Buscando aplicativo {aplicativo}")
        self.ingresar_texto(By.ID, "buscadorInput", aplicativo)
        self.demora()
        self.presionar_tecla(By.ID, "buscadorInput", Keys.TAB)
        self.mostrar("Aplicativo encontrado")
        
        self.cambiar_ventana()
        
        # Tengo que probar cuando el aplicativo no se encuentra
        
        # Tengo que validar que el aplicativo se haya encontrado de alguna forma. que haya creado una segunda pestaña
        
    def aplicativo_correcto(self, nombreAplicativo:str) -> bool:
        """ Verifica que se haya encontrado el aplicativo """
        aplicativo = self.encontrar_elemento(By.XPATH, f'//h1[text()={nombreAplicativo}]')
        if not aplicativo or aplicativo.text.lower() != nombreAplicativo.lower(): 
            self.mostrar(f"No se encontró el aplicativo {nombreAplicativo}", True)
            return False

        return True
    
    def cerrar_pestaña(self):
        """ Cierra la pestaña actual """
        if not self._driver:
            raise ValueError("El driver no está inicializado.")
        
        self._driver.close()
        self._driver.switch_to.window(self._driver.window_handles[-1])