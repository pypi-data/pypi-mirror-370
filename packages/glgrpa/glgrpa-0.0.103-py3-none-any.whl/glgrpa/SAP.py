# src/glgrpa/SAP.py

# Importaciones necesarias
from selenium.webdriver.common.by import By

from .Chrome import Chrome
from .Terminal import Terminal
from .Windows import Windows

class SAP(Chrome, Windows, Terminal):    
    def __init__(self, base_url: str, usuario: str, clave: str, usuario_microsoft: str = '', clave_microsoft: str = '', dev: bool = False, driver=None):
        super().__init__(dev=dev, driver=driver)
        self.base_url = base_url.split('#')[0]  # Asegurarse de que base_url no tenga fragmentos
        
        self.autentificacion_http_activo = False
        self.autentificacion_sap_activo = False
        self.autentificacion_microsoft_activo = False

        self.usuario_sap = usuario
        self.clave_sap = clave
        self.usuario_microsoft = usuario_microsoft
        self.clave_microsoft = clave_microsoft
        
        self.set_credenciales_usuario(usuario, clave)

        self.sap_iniciado = False
        
        self.mapa_transacciones = {
            'OB08': "#Shell-startGUI?sap-ui2-tcode=OB08&sap-system=FIORI_MENU",
            'FB03': '#Shell-startGUI?sap-ui2-tcode=FB03&sap-system=FIORI_MENU',
            # Agrega más transacciones según sea necesario
        }
    
    # Setter y Getter de credenciales SAP y Microsoft
    def set_credenciales_usuario(self, usuario: str, clave: str) -> dict:
        """
        Configura las credenciales del usuario de SAP.
        
        Al inicializar la clase se setean las credenciales del usuario y la clave de SAP pero se pueden cambiar en cualquier momento.
        
        ---
        ### Ejemplo
        ```python
        sap = SAP(base_url='https://sap.example.com', usuario='usuario', clave='clave')
        sap.set_credenciales_usuario('nuevo_usuario', 'nueva_clave')
        ```
        >>> {'usuario': 'nuevo_usuario', 'clave': 'nueva_clave'}
        
        ---
        ### Raises
        #### ValueError
        - Si el usuario está vacío.
        - Si la clave está vacía.
        """
        
        if usuario == '':
            raise ValueError("El usuario no puede estar vacío")
        if clave == '':
            raise ValueError("La clave no puede estar vacía")
        
        self.usuario_sap = usuario
        self.clave_sap = clave
        
        return {
            'usuario': self.usuario_sap,
            'clave': self.clave_sap
        }
        
    def set_credenciales_microsoft(self, usuario: str, clave: str) -> dict:
        """
        Configura las credenciales del usuario de Microsoft.
        
        Permite configurar las credenciales de Microsoft después de inicializar la clase SAP.
        Estas credenciales serán utilizadas automáticamente por el LoginManager cuando sea necesario.
        
        ---
        ### Ejemplo
        ```python
        sap = SAP(base_url='https://sap.example.com', usuario='usuario_sap', clave='clave_sap')
        sap.set_credenciales_microsoft('usuario@empresa.com', 'clave_microsoft')
        ```
        >>> {'usuario': 'usuario@empresa.com', 'clave': 'clave_microsoft'}
        
        ---
        ### Raises
        #### ValueError
        - Si el usuario de Microsoft está vacío.
        - Si la clave de Microsoft está vacía.
        """
        
        if usuario == '':
            raise ValueError("El usuario de Microsoft no puede estar vacío")
        if clave == '':
            raise ValueError("La clave de Microsoft no puede estar vacía")
        
        self.usuario_microsoft = usuario
        self.clave_microsoft = clave
        self.mostrar(f"🔐 Credenciales Microsoft configuradas para {self.usuario_microsoft}")
        
        return {
            'usuario': self.usuario_microsoft,
            'clave': self.clave_microsoft
        }
        
    def obtener_credenciales_microsoft(self) -> tuple[str, str]:
        """
        Obtiene las credenciales de Microsoft configuradas.
        
        ---
        ### Ejemplo
        ```python
        sap = SAP(base_url='https://sap.example.com', usuario='usuario', clave='clave')
        sap.set_credenciales_microsoft('usuario@empresa.com', 'clave_microsoft')
        usuario, clave = sap.obtener_credenciales_microsoft()
        ```
        >>> ('usuario@empresa.com', 'clave_microsoft')
        >>> ('', '') # Si no se han configurado las credenciales
        """
        return (self.usuario_microsoft, self.clave_microsoft)
        
    def obtener_usuario_sap(self) -> str:
        """ 
        Obtiene el usuario de SAP configurado.
        
        ---
        ### Ejemplo
        ```python
        sap = SAP(base_url='https://sap.example.com', usuario='usuario', clave='clave')
        sap.obtener_usuario_sap()
        ```
        >>> 'usuario'
        
        ---
        ### Raises
        #### ValueError
        - Si el usuario SAP no está configurado.
        """
        if not self.usuario_sap:
            raise ValueError("Usuario SAP no configurado. Use set_credenciales_usuario() para configurarlo.")
        
        return self.usuario_sap
    
    def obtener_clave_sap(self) -> str:
        """
        Obtiene la clave de SAP configurada.
        
        ---
        ### Ejemplo
        ```python
        sap = SAP(base_url='https://sap.example.com', usuario='usuario', clave='clave')
        sap.obtener_clave_sap()
        ```
        >>> 'clave'

        ---
        ### Raises
        #### ValueError
        - Si la clave SAP no está configurada.
        """
        if not self.clave_sap:
            raise ValueError("Clave SAP no configurada. Use set_credenciales_usuario() para configurarla.")
        return self.clave_sap
    
    # Método unificado de ingreso a SAP utilizando LoginManager
    def ingreso_a_sap(self) -> bool:
        """
        Método unificado para el ingreso a SAP que utiliza LoginManager.
        
        Este método reemplaza toda la lógica de autenticación anterior y utiliza 
        el LoginManager centralizado para manejar todos los tipos de login.
        
        ---
        ### Ejemplo
        ```python
        sap = SAP(base_url='https://sap.example.com', usuario='usuario', clave='clave')
        sap.ingreso_a_sap()
        ```
        >>> True  # Si SAP se inició correctamente
        
        ---
        ### Raises
        #### ValueError
        - Las opciones del driver no están configuradas.
        - El navegador no está abierto.
        - Error crítico en el proceso de login (credenciales vacías, driver no inicializado, etc.)
        #### Exception
        - No se pudo obtener el PID del proceso de Chrome.
        - No se pudo activar la ventana de SAP.
        """
        try:
            # Importar LoginManager para evitar importación circular
            from .LoginManager import LoginManager
            
            self.driver = self.obtener_driver()
            
            # Configurar LoginManager con las credenciales SAP y Microsoft
            login_manager = LoginManager(
                dev=self.dev, 
                driver=self.driver
            )
            
            # Configurar credenciales SAP (obligatorias)
            login_manager.configurar_credenciales_sap(self.usuario_sap, self.clave_sap)
            
            # Configurar credenciales Microsoft si están disponibles
            if self.usuario_microsoft and self.clave_microsoft:
                login_manager.configurar_credenciales_microsoft(self.usuario_microsoft, self.clave_microsoft)
                
            # Identificar si se requiere login unificado
            if login_manager.manejar_login_automatico():
                self.mostrar("🧮 Ingresando a SAP...")

            # Navegar a SAP pasando el LoginManager configurado
            self.navegar(self.base_url, login_manager=login_manager)
            self.activar_ventana()
            
            # Verificación final del estado
            if self.__en_pagina_de_inicio():
                self.sap_iniciado = True
                return self.sap_iniciado
            
            # Si llegamos aquí y no estamos en la página de inicio, puede que necesitemos login adicional
            self.mostrar("🔍 Verificando si se requiere login adicional...")
            
            # Intentar manejar cualquier login pendiente
            try:
                if login_manager.manejar_login_automatico():
                    self.mostrar("🔓 Login adicional completado")
                    # Verificar nuevamente
                    if self.__en_pagina_de_inicio():
                        self.sap_iniciado = True
                        self.mostrar("✅ SAP iniciado correctamente después de login adicional")
                        return self.sap_iniciado
                else:
                    self.mostrar("⚠️ Login automático retornó False - posible fallo en autenticación")
            except ValueError as login_error:
                # Los errores críticos del LoginManager se propagan como ValueError
                self.mostrar(f"❌ Error crítico en login automático: {str(login_error)}", True)
                raise ValueError(f"Error crítico durante el login: {str(login_error)}") from login_error
            
            # Si aún no estamos en la página correcta
            self.mostrar("❌ No se pudo completar el ingreso a SAP", True)
            self.sap_iniciado = False
            return self.sap_iniciado
            
        except ValueError as ve:
            # Re-propagar errores críticos del LoginManager o de configuración
            self.mostrar(f"❌ Error crítico en ingreso_a_sap: {str(ve)}", True)
            self.sap_iniciado = False
            raise ve
        except Exception as e:
            # Manejar otros errores inesperados
            self.mostrar(f"❌ Error inesperado en ingreso_a_sap: {str(e)}", True)
            self.sap_iniciado = False
            raise Exception(f"Error inesperado durante el ingreso a SAP: {str(e)}") from e
    
    def __en_pagina_de_inicio(self) -> bool:
        """
        Verifica si se está en la página de inicio de SAP.

        Comprueba si el título de la página es "Página de inicio", lo que indica que se ha iniciado sesión correctamente.

        ---
        Se utiliza dentro del método `navegar_inicio_SAP()`.

        ---
        ### Ejemplo
        ```python
        self.__en_pagina_de_inicio():
        ```
        >>> True
        """
        for reintentos in range(5):
            if self.driver.title == "Página de inicio":
                return True
            self.demora(3)
            self.driver.refresh()

        return False

    # Navegación a transacciones específicas
    def ir_a_transaccion(self, codigo_transaccion: str) -> None:
        """
        Navega a una transacción específica en SAP a través de su código.
        
        Busca la transacción en el mapa de transacciones y navega a la URL correspondiente comprobando el acceso correcto al mismo.
        
        ---
        ### Ejemplo
        ```python
        codigo_transaccion = 'OB08'
        sap = SAP(base_url='https://sap.example.com')
        sap.set_credenciales_usuario('usuario', 'clave')
        sap.ingreso_a_sap()
        sap.ir_a_transaccion(codigo_transaccion)
        ```
        >>> None  # Si la transacción se navega correctamente
        
        ---
        ### Raises
        #### ValueError
        - Si SAP no ha sido iniciado
        - Si la transacción no se encuentra en el mapa de transacciones.
        - Si se encuentra una alerta desconocida.
        #### PermissionError
        - Si no se tiene acceso a la transacción.
        - Si los datos están bloqueados para la transacción.        
        """
        
        if self.sap_iniciado is False:
            raise ValueError("SAP no ha sido iniciado. Use ingreso_a_sap() primero.")
        
        self.mostrar(f"Navegando a la transacción {codigo_transaccion}")

        transaccion = self.__obtener_transaccion_por_codigo(codigo_transaccion)
        self.navegar(f"{self.base_url}{transaccion}")
        self.__comprobar_acceso_transaccion()
        
        self.mostrar(f"Transacción {codigo_transaccion} navegada")
        
    def __obtener_transaccion_por_codigo(self, codigo_transaccion: str) -> str:
        """ 
        Obtiene la url relativa de la transacción por su código si es que existe en el mapa de transacciones.
        Si no se encuentra, lanza una excepción.
        
        ---
        Se utiliza dentro del metodo `ir_a_transaccion()`.
        
        ---
        Ejemplo
        ```python
        codigo = 'OB08'
        transaccion = self.__obtener_transaccion_por_codigo(codigo)
        ```
        >>> "Shell-startGUI?sap-ui2-tcode=OB08&sap-system=FIORI_MENU"

        ---
        ### Raises 
        #### ValueError: 
        - Si la transacción no se encuentra en el mapa de transacciones.
        """
        
        transaccion = self.mapa_transacciones.get(codigo_transaccion)
        
        if transaccion is None:
            raise ValueError(f"Transacción {codigo_transaccion} no encontrada en el mapa de transacciones")

        return transaccion
    
    def __comprobar_acceso_transaccion(self) -> None:
        """
        Comprueba el acceso a la transacción.
        
        ---
        Se utiliza dentro del metodo `ir_a_transaccion()`.
        
        ---
        Ejemplo
        ```python
        codigo_transaccion = 'OB08'
        transaccion = self.__obtener_transaccion_por_codigo(codigo_transaccion)
        self.navegar(f"{self.base_url}{transaccion}")
        self.__comprobar_acceso_transaccion()
        ```
        >>> None  # Si el acceso a la transacción se verifica correctamente
        
        ---
        ### Raises
        #### ValueError
        - Si se encuentra una alerta desconocida.
        #### PermissionError
        - Si no se tiene autorización para la transacción.
        - Si los datos están bloqueados para la transacción.
        """
        self.mostrar("Comprobando acceso a la transacción")
        
        alerta = self.__buscar_alertas()
        if alerta:
            self.mostrar(f"Alerta encontrada: {alerta}", True)
            if 'No tiene autorización' in alerta:
                raise PermissionError("No tiene autorización para esta transacción")
            elif 'Datos bloqueados' in alerta:
                raise PermissionError("Datos bloqueados para esta transacción")
            else:
                raise ValueError(f"Alerta desconocida: {alerta}")   
    
    # Métodos de búsqueda de alertas        
    def __buscar_alertas(self) -> str|None:
        """ 
        Busca alertas emergentes en SAP. 
        
        En caso de encontrar una alerta, devuelve el texto de la alerta.
        
        ---
        Se utiliza dentro del metodo `__comprobar_acceso_transaccion()`.
        
        ---
        Ejemplo
        ```python
        alerta = self.__buscar_alertas()
        ```
        >>> "Alerta\\nNo tiene autorización para esta transacción\\nAcepter\\nCancelar"  # Si se encuentra una alerta
        """
        span_alerta, texto_alerta = self.buscar_elemento_en_iframes(By.CLASS_NAME, 'lsPWNew', False)
        
        if span_alerta and texto_alerta:
            return texto_alerta.strip().split('\n')[0]
        
        return None
    
    def buscar_alerta_transaccion(self) -> dict[str, bool | str] | None:
        """ 
        Busca una alerta de transacción en SAP.
        
        Busca un elemento con la clase `lsMessageBar` en los iframes de la página y verifica si contiene una alerta de error o una alerta de transacción.  
        En caso de encontrar una alerta, evalua si es un error buscando clases como `lsMessageBar__icon--Error` o `lsMessageBar__image--Error` en los hijos del elemento encontrado.
        
        ---
        Ejemplo
        ```python
        alerta = self.buscar_alerta_transaccion()
        ```
        >>> {'isError': True, 'content': 'Alerta de error encontrada'}
        >>> {'isError': False, 'content': 'Alerta de transacción encontrada'}
        
        """
        self.mostrar("Obteniendo alerta de transacción")
        span_alerta, texto_alerta = self.buscar_elemento_en_iframes(By.CLASS_NAME, 'lsMessageBar')
        
        if span_alerta and texto_alerta:
            # Verifica si algún hijo tiene clase de error
            hijos = span_alerta.find_elements(By.XPATH, ".//*")
            for h in hijos:
                clase_hijo = h.get_attribute("class")
                if clase_hijo is not None:
                    if "lsMessageBar__icon--Error" in clase_hijo or "lsMessageBar__image--Error" in clase_hijo:
                        self.mostrar("Alerta de error encontrada", True)
                        isError = True
                        break    
            else:
                self.mostrar("Alerta de transacción encontrada", True)
                isError = False
            
            return {'isError': isError, 'content': texto_alerta.strip().split('\n')[0]}
        
        self.mostrar("No se encontró alerta de transacción", True)
        return None