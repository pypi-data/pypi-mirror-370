# LoginManager.py
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .Chrome import Chrome
from .Windows import Windows
from .Terminal import Terminal

# Import condicional de pyautogui para evitar errores en CI headless
try:
    # Solo importar si no estamos en CI o si se solicita explícitamente
    if os.getenv('CI') != 'true' or os.getenv('FORCE_PYAUTOGUI') == '1':
        import pyautogui
    else:
        pyautogui = None
except ImportError:
    pyautogui = None

class LoginManager(Chrome, Windows, Terminal):
    """
    Clase centralizada para manejar todos los tipos de autenticación y login
    que pueden aparecer durante la navegación.
    
    Tipos de login soportados:
    - Microsoft/SSO (correo y contraseña corporativa)
    - SAP (credenciales específicas de SAP)
    """
    
    def __init__(self, dev: bool = False, driver=None):
        super().__init__(dev=dev, driver=driver)
        
        # Credenciales Microsoft
        self.usuario_microsoft = ''
        self.clave_microsoft = ''
        
        # Credenciales SAP 
        self.usuario_sap = ''
        self.clave_sap = ''
        
        # Configuración de reintentos
        self.max_reintentos_login = 3
        self.timeout_login = 5
        
        # Patrones de detección de páginas de login
        self.patrones_login = {
            'microsoft': {
                'titulos': ['iniciar sesión', 'sign in to your account', 'microsoft', 'office 365', 'azure'],
                'urls': ['login.microsoftonline'],
                'elementos': ['loginfmt', 'i0116', 'displayName']
            },
            'sap': {
                'titulos': ['sap logon', 'sap gui'],
                'urls': ['sap.logon', 'fiori'],
                'elementos': ['LOGIN_MAIN', 'USERNAME_FIELD', 'PASSWORD_FIELD']
            }
        }

    def _safe_pyautogui_action(self, action_name, *args, **kwargs):
        """
        Ejecuta acciones de pyautogui de forma segura, con fallback para CI.
        
        Args:
            action_name: Nombre del método de pyautogui ('press', 'hotkey', etc.)
            *args, **kwargs: Argumentos para la acción
        
        Returns:
            bool: True si la acción se ejecutó, False si no está disponible
        """
        if pyautogui is None:
            self.mostrar(f"⚠️ pyautogui no disponible, saltando acción: {action_name}", True)
            return False
        
        try:
            action = getattr(pyautogui, action_name)
            action(*args, **kwargs)
            return True
        except Exception as e:
            self.mostrar(f"❌ Error en pyautogui.{action_name}: {str(e)}", True)
            return False

    # Getters y Setters para credenciales
    def obtener_credenciales_sap(self) -> tuple[str, str]:
        """
        Obtiene las credenciales SAP configuradas.
        
        ---
        ### Ejemplo
        ```
        from src.glgrpa.LoginManager import LoginManager
        
        login_manager = LoginManager()
        usuario, clave = login_manager.obtener_credenciales_sap()
        ```
        >>> ('usuario_sap', 'clave_sap')
        >>> ('', '') # Si no se han configurado las credenciales
        """
        return (self.usuario_sap, self.clave_sap)
    
    def obtener_credenciales_microsoft(self) -> tuple[str, str]:
        """
        Obtiene las credenciales Microsoft configuradas.
        
        ---
        ### Ejemplo
        ```
        from src.glgrpa.LoginManager import LoginManager
        
        login_manager = LoginManager()
        usuario, clave = login_manager.obtener_credenciales_microsoft()
        ```
        >>> ('usuario_microsoft', 'clave_microsoft')
        >>> ('', '') # Si no se han configurado las credenciales
        """
        return (self.usuario_microsoft, self.clave_microsoft)
    
    def configurar_credenciales_sap(self, usuario: str, clave: str) -> tuple[str, str]:
        """
        Configura las credenciales específicas de SAP.
        
        ---
        ### Ejemplo
        ```
        from src.glgrpa.LoginManager import LoginManager
        
        login_manager = LoginManager()
        login_manager.configurar_credenciales_sap('usuario_sap', 'clave_sap')
        ```
        >>> ('usuario_sap', 'clave_sap')
        
        ---
        ### Excepciones
        - `ValueError`: Si el usuario o la clave están vacíos.
        """
        if not usuario or not clave:
            raise ValueError("Usuario y clave SAP no pueden estar vacíos")
        
        self.usuario_sap = usuario
        self.clave_sap = clave
        self.mostrar(f"🔐 Credenciales SAP configuradas para: {usuario}")
        
        return (self.usuario_sap, self.clave_sap)
    
    def configurar_credenciales_microsoft(self, usuario: str, clave: str) -> tuple[str, str]:
        """
        Configura las credenciales de Microsoft/SSO.
        
        ---
        ### Ejemplo
        ```
        from src.glgrpa.LoginManager import LoginManager
        
        login_manager = LoginManager()
        login_manager.configurar_credenciales_microsoft('usuario_microsoft', 'clave_microsoft')
        ```
        >>> ('usuario_microsoft', 'clave_microsoft')
        
        ---
        ### Excepciones
        - `ValueError`: Si el usuario o la clave están vacíos.
        """
        if not usuario or not clave:
            raise ValueError("Usuario y clave Microsoft no pueden estar vacíos")
        
        self.usuario_microsoft = usuario
        self.clave_microsoft = clave
        self.mostrar(f"🔐 Credenciales Microsoft configuradas para: {usuario}")
        
        return (self.usuario_microsoft, self.clave_microsoft)
    
    # Login automático
    def detectar_tipo_login(self) -> str | None:
        """
        Detecta qué tipo de login está presente en la página actual.
        
        ---
        ### Ejemplo
        ```
        from src.glgrpa.LoginManager import LoginManager
        
        login_manager = LoginManager()
        tipo_login = login_manager.detectar_tipo_login()
        ```
        >>> 'microsoft' # Si se detecta un login de Microsoft
        >>> None # Si no se detecta ningún login conocido pero no hay error
        
        ---
        ### Returns
            str: Tipo de login detectado ('microsoft', 'sap', 'navegador') o None
            
        ---
        ### Excepciones
        - `ValueError`: Si el driver no está inicializado
        - `ValueError`: Si ocurre un error al detectar el tipo de login
        """
        if not self._driver:
            raise ValueError("El driver no está inicializado")
        
        try:
            self.demora(1)  # Esperar un segundo para que la página cargue completamente
            
            titulo_actual = self._driver.title.lower()
            url_actual = self._driver.current_url.lower()
            
            self.mostrar(f"🔍 Detectando login") 
            # self.mostrar(f"Título actual: '{titulo_actual}'")
            # self.mostrar(f"URL actual: '{url_actual}'")
            
            # Verificar cada tipo de login
            for tipo_login, patrones in self.patrones_login.items():
                # Verificar títulos
                if any(titulo in titulo_actual for titulo in patrones['titulos']):
                    self.mostrar(f"🔒 Login {tipo_login.upper()} detectado por título")
                    return tipo_login
                
                # Verificar URLs
                if any(url_patron in url_actual for url_patron in patrones['urls'] if url_patron):
                    self.mostrar(f"🔒 Login {tipo_login.upper()} detectado por URL")
                    return tipo_login
                
                # Verificar elementos específicos
                for elemento_id in patrones['elementos']:
                    if self.encontrar_elemento(By.ID, elemento_id, tiene_que_estar=False):
                        self.mostrar(f"🔒 Login {tipo_login.upper()} detectado por elemento: {elemento_id}")
                        return tipo_login
            
            self.mostrar("🔓 No se detectó ningún tipo de login conocido")
            return None
            
        except Exception as e:
            self.mostrar(f"❌ Error detectando tipo de login: {str(e)}", True)
            raise ValueError("Error al detectar tipo de login")
    
    def manejar_login_automatico(self) -> bool:
        """
        Detecta y maneja automáticamente cualquier tipo de login presente.
        
        ---
        ### Ejemplo
        ```
        from src.glgrpa.LoginManager import LoginManager
        
        login_manager = LoginManager()
        login_exitoso = login_manager.manejar_login_automatico()
        ```
        >>> True # Si se manejó un login exitosamente
        >>> False # Si no había login automatico programado o falló
        
        ---        
        ### Excepciones
        - `ValueError`: Si ocurre un error al detectar o manejar el login
        """
        try:
            tipo_login = self.detectar_tipo_login()
            if not tipo_login: return False
            
            # Delegar al método específico
            if tipo_login == 'microsoft':
                return self.manejar_login_microsoft()
            elif tipo_login == 'sap':
                return self.manejar_login_sap()
            
            self.mostrar(f"🌐 Manejo de login desconocido. No hay método asignado.")
            return False
        except ValueError as ve:
            raise ve
    
    # Métodos específicos para manejar cada tipo de login
    def manejar_login_microsoft(self) -> bool:
        """
        Maneja el login de Microsoft/SSO usando credenciales de variables de entorno.
        
        ---
        ### Ejemplo
        ```
        from src.glgrpa.LoginManager import LoginManager
        
        login_manager = LoginManager()
        login_exitoso = login_manager.manejar_login_microsoft()
        ```
        >>> True # Si el login fue exitoso
        
        ---
        ### Excepciones
        - `ValueError`: Si las credenciales de Microsoft no están configuradas
        - `ValueError`: Si ocurre un error al manejar el login de Microsoft
        """
        if not self.usuario_microsoft or not self.clave_microsoft:
            self.mostrar("❌ Credenciales Microsoft no configuradas", True)
            raise ValueError("Credenciales Microsoft no configuradas")
        
        self.mostrar("🔐 Procesando login Microsoft...")
        
        for intento in range(self.max_reintentos_login):
            try:
                self.mostrar(f"🔄 Intento {intento + 1}")
                
                # Paso 1: Ingresar email/usuario
                if not self._ingresar_usuario_microsoft():
                    continue
                
                # Paso 2: Ingresar contraseña
                if not self._ingresar_clave_microsoft():
                    continue
                
                # Paso 3: Manejar "No mantener sesión iniciada"
                self._manejar_no_mantener_sesion()
                
                # Paso 4: Verificar éxito
                if self._verificar_login_exitoso():
                    self.mostrar("🔓 Login Microsoft exitoso")
                    return True
                
            except Exception as e:
                self.mostrar(f"❌ Error en intento {intento + 1} de login Microsoft: {str(e)}", True)
                
            self.demora(2)  # Esperar antes del siguiente intento
        
        self.mostrar("❌ Login Microsoft falló después de todos los intentos", True)
        raise ValueError("Login Microsoft fallido después de todos los intentos")
    
    def manejar_login_sap(self) -> bool:
        """
        Maneja el login específico de SAP.
        
        Returns:
            bool: True si el login fue exitoso, False en caso contrario
        """
        if not self.usuario_sap or not self.clave_sap:
            self.mostrar("❌ Credenciales SAP no configuradas", True)
            return False
        
        self.mostrar("🏢 Procesando login SAP...")
        
        for intento in range(self.max_reintentos_login):
            try:
                self.mostrar(f"🔄 Intento {intento + 1} de login SAP")
                
                # Verificar si está el elemento LOGIN_MAIN
                if not self.encontrar_elemento(By.ID, 'LOGIN_MAIN', tiene_que_estar=False):
                    self.mostrar("⚠️ Elemento LOGIN_MAIN no encontrado, puede que no sea login SAP")
                    return False
                
                # Ingresar usuario SAP
                if self.encontrar_elemento(By.ID, 'USERNAME_FIELD-inner', tiene_que_estar=False):
                    self.ingresar_texto(By.ID, 'USERNAME_FIELD-inner', self.usuario_sap)
                    self.mostrar("📝 Usuario SAP ingresado")
                
                # Ingresar contraseña SAP
                if self.encontrar_elemento(By.ID, 'PASSWORD_FIELD-inner', tiene_que_estar=False):
                    self.ingresar_texto(By.ID, 'PASSWORD_FIELD-inner', self.clave_sap)
                    self.mostrar("🔑 Contraseña SAP ingresada")
                
                # Enviar formulario
                self._safe_pyautogui_action('press', 'enter')
                self.demora(3)
                
                # Verificar éxito
                if self._verificar_login_exitoso():
                    self.mostrar("🔓 Login SAP exitoso")
                    return True
                
            except Exception as e:
                self.mostrar(f"❌ Error en intento {intento + 1} de login SAP: {str(e)}", True)
                
            self.demora(2)
        
        self.mostrar("❌ Login SAP falló después de todos los intentos", True)
        return False
    
    def manejar_login_navegador(self) -> bool:
        """
        Maneja el login básico del navegador (HTTP Auth).
        
        Returns:
            bool: True si el login fue exitoso, False en caso contrario
        """
        self.mostrar("🌐 Procesando login del navegador...")
        
        try:
            # Para login HTTP básico, usualmente se maneja con Shift+Tab y Enter
            self._safe_pyautogui_action('hotkey', 'shift', 'tab')
            self._safe_pyautogui_action('press', 'enter')
            self.demora(2)
            
            if self._verificar_login_exitoso():
                self.mostrar("🔓 Login navegador exitoso")
                return True
                
        except Exception as e:
            self.mostrar(f"❌ Error en login navegador: {str(e)}", True)
        
        return False
    
    # Métodos privados para manejar el login de Microsoft
    def _ingresar_usuario_microsoft(self) -> bool:
        """
        Ingresa el usuario en el formulario de Microsoft.
        
        ---
        Utilizado en `manejar_login_microsoft`.
        
        ---
        ### Excepciones
        - `ValueError`: Si no se encuentra el campo de usuario o ocurre un error al ingresar el usuario
        """
        
        try:
            # Intentar diferentes selectores para el campo de usuario
            selectores_usuario = [
                (By.NAME, 'loginfmt'),
                (By.ID, 'i0116'),
                (By.ID, 'displayName'),
                (By.XPATH, '//input[@type="email"]'),
                (By.XPATH, '//input[@placeholder*="correo"]')
            ]
            
            for selector_tipo, selector_valor in selectores_usuario:
                elemento = self.encontrar_elemento(selector_tipo, selector_valor, tiene_que_estar=False)
                if elemento:
                    self.ingresar_texto(selector_tipo, selector_valor, self.usuario_microsoft)
                    self.mostrar("📧 Usuario Microsoft ingresado")
                    
                    # Buscar y hacer clic en "Siguiente"
                    self._click_siguiente_microsoft()
                    return True
            
            self.mostrar("❌ Campo de usuario Microsoft no encontrado", True)
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error ingresando usuario Microsoft: {str(e)}", True)
            raise ValueError("Error al ingresar usuario Microsoft")
    
    def _ingresar_clave_microsoft(self) -> bool:
        """
        Ingresa la contraseña en el formulario de Microsoft.
        
        ---
        Utilizado en `manejar_login_microsoft`.
        
        ---
        ### Excepciones
        - `ValueError`: Si no se encuentra el campo de contraseña o ocurre un error al ingresar la contraseña
        """
        try:
            # Esperar a que aparezca el campo de contraseña
            self.demora(2)
            
            selectores_clave = [
                (By.ID, 'i0118'),
                (By.NAME, 'passwd'),
                (By.XPATH, '//input[@type="password"]'),
                (By.XPATH, '//input[@placeholder*="contraseña"]')
            ]
            
            for selector_tipo, selector_valor in selectores_clave:
                elemento = self.encontrar_elemento(selector_tipo, selector_valor, tiene_que_estar=False)
                if elemento:
                    self.ingresar_texto(selector_tipo, selector_valor, self.clave_microsoft)
                    self.mostrar("🔑 Contraseña Microsoft ingresada")
                    
                    # Buscar y hacer clic en "Iniciar sesión"
                    self._click_iniciar_sesion_microsoft()
                    return True
            
            self.mostrar("❌ Campo de contraseña Microsoft no encontrado", True)
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error ingresando contraseña Microsoft: {str(e)}", True)
            return False
    
    def _click_siguiente_microsoft(self) -> bool:
        """Hace clic en el botón 'Siguiente' de Microsoft."""
        botones_siguiente = [
            (By.ID, 'idSIButton9'),
            (By.XPATH, '//input[@value="Siguiente"]'),
            (By.XPATH, '//button[contains(text(), "Siguiente")]'),
            (By.XPATH, '//input[@value="Next"]'),
            (By.XPATH, '//button[contains(text(), "Next")]')
        ]
        
        for selector_tipo, selector_valor in botones_siguiente:
            if self.click_elemento(selector_tipo, selector_valor):
                return True
        
        return False
    
    def _click_iniciar_sesion_microsoft(self) -> bool:
        """Hace clic en el botón 'Iniciar sesión' de Microsoft."""
        botones_login = [
            (By.ID, 'idSIButton9'),
            (By.XPATH, '//input[@value="Iniciar sesión"]'),
            (By.XPATH, '//button[contains(text(), "Iniciar sesión")]'),
            (By.XPATH, '//input[@value="Sign in"]'),
            (By.XPATH, '//button[contains(text(), "Sign in")]')
        ]
        
        for selector_tipo, selector_valor in botones_login:
            if self.click_elemento(selector_tipo, selector_valor):
                return True
        
        return False
    
    def _manejar_no_mantener_sesion(self) -> None:
        """
        Maneja la pantalla 'No mantener sesión iniciada'.
        
        ---
        Utilizado en `manejar_login_microsoft`.
        
        ---
        ### Excepciones
        - `ValueError`: Si ocurre un error al manejar la opción 'No mantener sesión'
        """
        try:
            botones_no = [
                (By.ID, 'idBtn_Back'),
                (By.XPATH, '//button[contains(text(), "No")]'),
                (By.XPATH, '//input[@value="No"]')
            ]
            
            for selector_tipo, selector_valor in botones_no:
                if self.click_elemento(selector_tipo, selector_valor):
                    self.mostrar("✅ Opción 'No mantener sesión' seleccionada")
                    self.demora(2)
                    return
            
        except Exception as e:
            self.mostrar(f"⚠️ No se pudo manejar 'No mantener sesión': {str(e)}")
            raise ValueError("Error al manejar 'No mantener sesión' en Microsoft")
    
    # Verificación de login exitoso
    def _verificar_login_exitoso(self) -> bool:
        """
        Verifica si el login fue exitoso comprobando indicadores comunes.
        En casos dudosos, reintenta 3 veces esperando 3 segundos cada vez.
        
        ---
        Utilizado en `manejar_login_microsoft` y `manejar_login_sap`.
        
        ---
        ### Ejemplo
        ```
        from src.glgrpa.LoginManager import LoginManager
        
        login_manager = LoginManager()
        login_exitoso = login_manager.manejar_login_microsoft()
        print(login_exitoso)
        ```
        >>> True # Si el login fue exitoso
        >>> False # Si el login no fue exitoso o si fue dudoso después de reintentos
        
        ---
        ### Excepciones
        - `ValueError`: Si el driver no está inicializado
        - `ValueError`: Si ocurre un error al verificar el login exitoso

        """
        try:
            if not self._driver:
                raise ValueError("El driver no está inicializado")
            
            # Definir indicadores una sola vez
            indicadores_exito = [
                'página de inicio', 'home', 'dashboard', 'inicio',
                'main page', 'portal', 'fiori', 'launchpad'
            ]
            
            indicadores_login = [
                'sign in', 'login', 'iniciar sesión', 'autenticación',
                'authentication', 'logon', 'credentials'
            ]
            
            # Intentar verificar hasta 3 veces en casos dudosos
            max_reintentos = 3
            tiempo_espera = 3
            
            for intento in range(max_reintentos):
                titulo_actual = self._driver.title.lower()
                url_actual = self._driver.current_url.lower()
                
                # Si encontramos indicadores de éxito
                if any(indicador in titulo_actual for indicador in indicadores_exito):
                    if intento > 0:
                        self.mostrar(f"✅ Login exitoso confirmado en intento {intento + 1}")
                    return True
                
                # Si encontramos indicadores de login, definitivamente no es éxito
                if any(indicador in titulo_actual for indicador in indicadores_login):
                    if intento > 0:
                        self.mostrar(f"❌ Login fallido confirmado en intento {intento + 1}")
                    return False
                
                # Si no hay indicadores claros y no es el último intento, esperar y reintentar
                if intento < max_reintentos - 1:
                    self.mostrar(f"👀 Login dudoso (intento {intento + 1}). Esperando {tiempo_espera}s para recargar página...")
                    self.mostrar(f"Título actual: '{titulo_actual}'")
                    self.mostrar(f"URL actual: '{url_actual}'")
                    self.demora(tiempo_espera)
                else:
                    # Último intento, definitivamente dudoso
                    self.mostrar(f"👀 Login dudoso después de {max_reintentos} intentos. Asumiendo fallo.")
                    self.mostrar(f"Título final: '{titulo_actual}'")
                    self.mostrar(f"URL final: '{url_actual}'")
                    return False
            
            return False
        
        except ValueError as ve:
            # Re-lanzar ValueError sin cambiar el mensaje
            raise ve
        except Exception as e:
            self.mostrar(f"❌ Error verificando login exitoso: {str(e)}", True)
            raise ValueError("Error al verificar login exitoso")
