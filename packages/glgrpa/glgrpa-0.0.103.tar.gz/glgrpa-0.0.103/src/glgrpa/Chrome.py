# src/Chrome/Chrome.py

# Librerías para el manejo de la consola
from .Terminal import Terminal

# Librerías estándar
import os
import tempfile
import uuid

# Librerías para el manejo de elementos web
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# Librerías para el manejo de datos
import pandas as pd
from io import StringIO
import os


class Chrome(Terminal):
    # Variables de clase para el singleton del driver
    _chrome_options: Options | None = None
    _driver: WebDriver | None = None
        
    def __init__(self, dev:bool=False, mostrar_mensajes_por_consola:bool=False, modo_oculto:bool=False, modo_minimizado:bool=False, driver:WebDriver|None=None):
        super().__init__(dev=dev)
        
        # Agregar herencia de Windows dinámicamente para evitar importación circular
        try:
            from .Windows import Windows
            windows_instance = Windows(dev=dev)
            # Copiar atributos específicos que Chrome necesita
            self.carpeta_descargas_personalizada = windows_instance.carpeta_descargas_personalizada
            # Agregar métodos de Windows como métodos bound
            self.tomar_screenshot = windows_instance.tomar_screenshot
        except ImportError:
            # Fallback para entornos donde Windows no está disponible
            self.carpeta_descargas_personalizada = os.path.join(os.environ.get("HOME", os.environ.get("USERPROFILE", "")), "DescargaPersonalizada")
            def dummy_screenshot(*args, **kwargs):
                self.mostrar("⚠️ Screenshots no disponibles en este entorno", True)
                return ""
            self.tomar_screenshot = dummy_screenshot
        self.dev = dev
        self.tiempo_demora = 2 if self.dev else 5
        self.reintentos = 3

        self._nuevo_driver = False  # <-- Añadido para saber si se crea un nuevo driver

        if driver is not None:
            Chrome._driver = driver

        if not Chrome._chrome_options:
            self._chrome_options = self.__configuracion_driver(
                mostrar_mensajes_por_consola=mostrar_mensajes_por_consola,
                modo_oculto=modo_oculto,
                modo_minimizado=modo_minimizado
            )
        if not Chrome._driver:
            self._driver = self.obtener_driver()
            self._nuevo_driver = True  # <-- Se creó un nuevo driver
        else:
            self._driver = Chrome._driver

        if self._nuevo_driver:
            self.mostrar("Iniciando navegador Chrome")        
        
    def __configuracion_driver(self, mostrar_mensajes_por_consola:bool=False, modo_oculto:bool=False, modo_minimizado:bool=False) -> Options:
        """ Configuración del driver """
        import tempfile
        import uuid
        
        chrome_options = Options()
        
        # Configuración específica para CI/CD y entornos sin display
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS') or os.getenv('SYSTEM_TEAMFOUNDATIONCOLLECTIONURI'):
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--remote-debugging-port=9222')
        
        # Directorio temporal único para evitar conflictos de concurrencia
        temp_dir = tempfile.mkdtemp(prefix=f'chrome_user_data_{uuid.uuid4().hex[:8]}_')
        chrome_options.add_argument(f'--user-data-dir={temp_dir}')
        
        # Configuraciones para evitar detección de automatización
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        if not mostrar_mensajes_por_consola:
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.add_argument('--log-level=3')
        if modo_oculto:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')  # Necesario para Windows
        if modo_minimizado:
            chrome_options.add_argument('--start-minimized')
        else:
            chrome_options.add_argument('--start-maximized')
            
        prefs = {
            "download.default_directory": self.carpeta_descargas_personalizada, # Carpeta de descargas
            "download.prompt_for_download": False, # No preguntar por la descarga
            "download.directory_upgrade": True, # Actualizar automaticamente la carpeta de descargas
            "safebrowsing.enabled": True, # Habilitar navegacion segura
            "profile.default_content_setting_values.notifications": 2,  # Bloquear notificaciones
            "profile.default_content_settings.popups": 0  # Permitir popups si es necesario
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        return chrome_options
        
    def obtener_driver(self) -> WebDriver:
        """ Obtiene el driver de Chrome """
        return self._driver if self._driver else self.__iniciar_driver()
    
    def __iniciar_driver(self) -> WebDriver:
        """ Inicia el driver de Chrome """
        if self._chrome_options is None:
            raise ValueError("Las opciones del driver no están configuradas. Por favor, inicializa el objeto Chrome correctamente.")
        
        self._driver = webdriver.Chrome(service=Service(log_path=os.devnull), options=self._chrome_options)
        self._driver.implicitly_wait(self.tiempo_demora)
        self._driver.set_page_load_timeout(30)  # <-- Cambiado a 30 segundos
        self._driver.set_script_timeout(30)     # <-- Cambiado a 30 segundos
        
        # Eliminar propiedades de automatización para máximo sigilo
        self._driver.execute_script("""
            // Eliminar propiedades que detectan automatización
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Eliminar el atributo cdc_ que usa ChromeDriver
            delete navigator.__proto__.webdriver;
            
            // Simular propiedades de usuario real
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['es-ES', 'es', 'en-US', 'en'],
            });
            
            // Redefinir la propiedad chrome para evitar detección
            if (navigator.chrome) {
                Object.defineProperty(navigator, 'chrome', {
                    get: () => ({
                        runtime: {},
                        // ... otras propiedades que un navegador real tendría
                    }),
                });
            }
        """)
        
        return self._driver
    
    def abrir_navegador(self) -> None:
        """ Abre el navegador """
        self._driver = self.obtener_driver()
        self.mostrar("Navegador abierto")
        
    def cerrar_navegador(self) -> None:
        """ Cierra el navegador """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de cerrarlo.")
        self._driver.quit()
        
        self.demora()
        
        Chrome._driver = None
        Chrome._chrome_options = None
        
        self.fin_ejecucion()
        
    def navegar(self, url:str, max_intentos:int=5, timeout_entre_intentos:int=3, login_manager=None, requiereLogin=False) -> None:
        """ 
        Navega a la URL con reintentos para manejar redirecciones automáticas de la empresa 
        y login automático integrado
        
        Args:
            url: URL de destino
            max_intentos: Número máximo de intentos de navegación (default: 5)
            timeout_entre_intentos: Segundos de espera entre intentos (default: 3)
            login_manager: LoginManager preconfigurado opcional para manejar login automático
        """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de navegar.")
        
        # Usar LoginManager proporcionado o crear uno básico
        if login_manager is None:
            # Importar LoginManager aquí para evitar importación circular
            from .LoginManager import LoginManager
            login_manager = LoginManager(dev=self.dev, driver=self._driver)
        
        for intento in range(max_intentos):
            try:
                if requiereLogin:
                    if login_manager.manejar_login_automatico():
                        self.mostrar("🔐 Login automático completado, reintentando navegación...")
                        self._driver.get(url)
                        self.demora()
                
                # Esperar a que la página esté completamente cargada antes de navegar
                WebDriverWait(self._driver, self.tiempo_demora).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                self.mostrar(f"🔍 Intento {intento + 1}: Navegando a {url}")
                self._driver.get(url)
                
                # Esperar a que la nueva página se cargue
                self.demora()
                
                # Verificar si estamos en la URL correcta
                url_actual = self._driver.current_url
                
                if url_actual == url or url in url_actual.split('?')[0] or url_actual.startswith(url):
                    self.mostrar(f"✅ Navegación exitosa")
                    return                   
                
                # Si no estamos en la URL correcta, verificar si es SharePoint
                if "sharepoint" in url_actual.lower() or "microsoft" in url_actual.lower():
                    self.mostrar(f"⚠️ Redirección detectada a política empresarial: {url_actual}")
                    
                    # Intentar manejar login de SharePoint/Microsoft
                    if login_manager.manejar_login_automatico():
                        self.mostrar("🔐 Login empresarial completado, reintentando navegación...")
                        continue  # Reintentar navegación después del login
                    
                    self.mostrar(f"🔄 Reintentando navegación en {timeout_entre_intentos} segundos...")
                    
                    # Esperar más tiempo si detectamos SharePoint para evitar conflictos
                    import time
                    time.sleep(timeout_entre_intentos)
                    continue
                else:
                    self.mostrar(f"⚠️ URL inesperada: {url_actual}")
                    self.mostrar(f"🎯 URL esperada: {url}")
                    
                    # Verificar si hay algún tipo de login en la página inesperada
                    if login_manager.detectar_tipo_login():
                        self.mostrar("🔐 Login detectado en URL inesperada, intentando manejar...")
                        if login_manager.manejar_login_automatico():
                            continue  # Reintentar después del login
                    
                    if intento < max_intentos - 1:
                        self.mostrar(f"🔄 Reintentando en {timeout_entre_intentos} segundos...")
                        import time
                        time.sleep(timeout_entre_intentos)
                        continue
                
            except TimeoutException as e:
                self.mostrar(f"❌ Intento {intento + 1}: Timeout al cargar la página {url}", True)
                if intento < max_intentos - 1:
                    self.mostrar(f"🔄 Reintentando en {timeout_entre_intentos} segundos...")
                    import time
                    time.sleep(timeout_entre_intentos)
                    continue
                else:
                    self.mostrar(f"❌ No se pudo cargar la página {url} después de {max_intentos} intentos", True)
                    
                    # Tomar screenshot para debugging
                    try:
                        nombre_screenshot = f"error_navegacion_{url.replace('/', '_').replace(':', '_')}"
                        self.tomar_screenshot(nombre_screenshot)
                    except Exception:
                        pass
                    
                    self.cerrar_navegador()
                    raise e
                    
            except Exception as e:
                self.mostrar(f"❌ Intento {intento + 1}: Error al navegar a {url}: {e}", True)
                if intento < max_intentos - 1:
                    self.mostrar(f"🔄 Reintentando en {timeout_entre_intentos} segundos...")
                    import time
                    time.sleep(timeout_entre_intentos)
                    continue
                else:
                    self.cerrar_navegador()
                    if "net::ERR_NAME_NOT_RESOLVED" in str(e):
                        self.mostrar("Parece que hay un problema con la conexión a Internet o el dominio no existe.", True)
                        raise ValueError("Dominio no encontrado o conexión a Internet inestable.")
                    raise e
        
        # Si llegamos aquí, todos los intentos fallaron
        url_final = self._driver.current_url
        self.mostrar(f"❌ No se pudo navegar a {url} después de {max_intentos} intentos", True)
        self.mostrar(f"🌐 URL final: {url_final}", True)
        
        # Tomar screenshot para debugging
        try:
            nombre_screenshot = f"error_navegacion_final_{url.replace('/', '_').replace(':', '_')}"
            self.tomar_screenshot(nombre_screenshot)
        except Exception:
            pass
        
        raise ValueError(f"No se pudo navegar a la URL solicitada. URL actual: {url_final}")
    
    def verificar_url_actual(self, url_esperada:str, tolerancia_parametros:bool=True) -> bool:
        """ 
        Verifica si la URL actual coincide con la esperada 
        
        Args:
            url_esperada: URL que se espera estar visitando
            tolerancia_parametros: Si True, ignora parámetros y fragmentos en la comparación
            
        Returns:
            bool: True si las URLs coinciden, False en caso contrario
        """
        if not self._driver:
            return False
        
        try:
            url_actual = self._driver.current_url
            
            if tolerancia_parametros:
                # Limpiar URLs para comparación (remover parámetros y fragmentos)
                url_esperada_limpia = url_esperada.split('?')[0].split('#')[0].lower()
                url_actual_limpia = url_actual.split('?')[0].split('#')[0].lower()
                
                # Verificar coincidencia exacta o si la URL actual empieza con la esperada
                return (url_actual_limpia == url_esperada_limpia or 
                       url_actual_limpia.startswith(url_esperada_limpia))
            else:
                return url_actual.lower() == url_esperada.lower()
                
        except Exception as e:
            self.mostrar(f"❌ Error al verificar URL: {str(e)}", True)
            return False
    
    def esperar_url_correcta(self, url_esperada:str, timeout:int=10) -> bool:
        """ 
        Espera hasta que la URL actual coincida con la esperada 
        
        Args:
            url_esperada: URL que se espera estar visitando
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            bool: True si se alcanza la URL esperada, False si se agota el timeout
        """
        if not self._driver:
            return False
        
        try:
            self.mostrar(f"⏱️ Esperando URL correcta: {url_esperada}")
            
            # Esperar hasta que la URL coincida o se agote el tiempo
            WebDriverWait(self._driver, timeout).until(
                lambda driver: self.verificar_url_actual(url_esperada)
            )
            
            self.mostrar(f"✅ URL correcta alcanzada: {self._driver.current_url}")
            return True
            
        except TimeoutException:
            self.mostrar(f"⏰ Timeout esperando URL correcta. URL actual: {self._driver.current_url}", True)
            return False
        except Exception as e:
            self.mostrar(f"❌ Error esperando URL correcta: {str(e)}", True)
            return False
    
    def navegar_con_bypass_empresarial(self, url:str, espera_inicial:int=5) -> None:
        """ 
        Navega a una URL esperando las redirecciones automáticas de políticas empresariales
        
        Args:
            url: URL de destino
            espera_inicial: Segundos de espera inicial para permitir redirecciones automáticas
        """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de navegar.")
        
        self.mostrar(f"🏢 Navegación empresarial a {url}")
        self.mostrar(f"⏱️ Esperando {espera_inicial} segundos para redirecciones automáticas...")
        
        # Espera inicial para permitir que las políticas empresariales actúen
        import time
        time.sleep(espera_inicial)
        
        # Ahora intentar navegar con el método mejorado
        self.navegar(url)
        
    def detectar_y_manejar_sharepoint(self) -> bool:
        """ 
        Detecta si estamos en una página de SharePoint y trata de manejarla
        
        Returns:
            bool: True si se detectó y manejó SharePoint, False en caso contrario
        """
        if not self._driver:
            return False
        
        try:
            url_actual = self._driver.current_url.lower()
            titulo_actual = self._driver.title.lower()
            
            # Detectar indicadores de SharePoint
            indicadores_sharepoint = [
                "sharepoint", "microsoft", "login.microsoftonline", 
                "office365", "office.com", "aad.portal.azure"
            ]
            
            es_sharepoint = any(indicador in url_actual for indicador in indicadores_sharepoint)
            es_login = any(palabra in titulo_actual for palabra in ["sign", "login", "authenticate", "iniciar"])
            
            if es_sharepoint or es_login:
                self.mostrar(f"🔍 SharePoint/Login detectado:")
                self.mostrar(f"  📄 Título: {self._driver.title}")
                self.mostrar(f"  🌐 URL: {self._driver.current_url}")
                
                # Tomar screenshot para debugging
                try:
                    nombre_screenshot = f"sharepoint_detectado"
                    self.tomar_screenshot(nombre_screenshot)
                except Exception:
                    pass
                                
                return True
            
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error detectando SharePoint: {str(e)}", True)
            return False
    
    def ScrollToUp(self):
        """ Hace scroll hasta el principio de la página """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de hacer scroll.")
        
        self._driver.execute_script("window.scrollTo(0, 0);")   
        self.demora() 
        
    def esperar_elemento_clickeable(self, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True, elemento_padre:WebElement|None=None) -> WebElement | None:
        """ Espera a que el elemento sea clickeable, opcionalmente dentro de un elemento padre """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de esperar un elemento clickeable.")
        
        try:
            if elemento_padre:
                elemento = WebDriverWait(elemento_padre, self.tiempo_demora).until(
                    EC.element_to_be_clickable((str(metodo_busqueda), texto_busqueda))
                )
                elemento = self.encontrar_elemento_desde_elemento(elemento_padre, metodo_busqueda, texto_busqueda, tiene_que_estar)
            else:
                elemento = WebDriverWait(self._driver, self.tiempo_demora).until(
                    EC.element_to_be_clickable((str(metodo_busqueda), texto_busqueda))
                )
                elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda, tiene_que_estar)
        except Exception as e:
            return None
        
        return elemento
    
    def click_elemento(self, metodo_busqueda:By|str, texto_busqueda:str) -> bool:
        """ Clickea el elemento con múltiples estrategias de reintento """
        return self._click_elemento_con_reintentos(metodo_busqueda, texto_busqueda)
    
    def _click_elemento_con_reintentos(self, metodo_busqueda:By|str, texto_busqueda:str, max_intentos:int=3) -> bool:
        """ 
        Clickea el elemento usando múltiples estrategias de reintento
        Estrategias:
        1. Click directo en elemento HTML (ideal para VMs e iframes)
        2. JavaScript click 
        3. ActionChains click
        """
        
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de hacer click en un elemento.")
        
        elemento = self.esperar_elemento_clickeable(metodo_busqueda, texto_busqueda)
        if not elemento: return False
        
        for intento in range(max_intentos):
            try:
                if intento == 0:
                    # Estrategia 1: Click directo en elemento HTML
                    # self.mostrar(f"🔍 Intento {intento + 1}: Click directo en elemento")
                    self.__desplazar_elemento_a_vista(elemento)
                    elemento.click()
                    # self.mostrar(f"✅ Click exitoso en elemento {texto_busqueda}")
                    return True
                    
                elif intento == 1:
                    # Estrategia 2: JavaScript click (ideal para elementos interceptados)
                    # self.mostrar(f"🔍 Intento {intento + 1}: JavaScript click")
                    self._driver.execute_script("arguments[0].click();", elemento)
                    # self.mostrar(f"✅ JavaScript click exitoso en elemento {texto_busqueda}")
                    return True
                    
                elif intento == 2:
                    # Estrategia 3: ActionChains click (para elementos complejos)
                    # self.mostrar(f"🔍 Intento {intento + 1}: ActionChains click")
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self._driver)
                    actions.move_to_element(elemento).click().perform()
                    # self.mostrar(f"✅ ActionChains click exitoso en elemento {texto_busqueda}")
                    return True
                    
            except ElementClickInterceptedException as e:
                self.mostrar(f"❌ Intento {intento + 1}: Elemento {texto_busqueda} está siendo interceptado", True)
                if intento < max_intentos - 1:
                    self.mostrar(f"🔄 Reintentando con estrategia alternativa...")
                    self.demora()
                continue
                
            except Exception as e:
                self.mostrar(f"❌ Intento {intento + 1}: Error al hacer click en {texto_busqueda}: {str(e)}", True)
                if intento < max_intentos - 1:
                    self.mostrar(f"🔄 Reintentando con estrategia alternativa...")
                    self.demora()
                continue
        
        # Si todas las estrategias fallan, tomar screenshot para debugging
        try:
            # Limpiar el texto_busqueda para usar como nombre de archivo
            texto_limpio = texto_busqueda.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            nombre_screenshot = f"error_click_{texto_limpio}"
            self.tomar_screenshot(nombre_screenshot)
        except Exception as e:
            self.mostrar(f"❌ Error al tomar screenshot: {str(e)}", True)
        
        self.mostrar(f"❌ No se pudo hacer click en elemento {texto_busqueda} después de {max_intentos} intentos", True)
        return False
        
    def click_elemento_desde_elemento(self, elemento_padre:WebElement, metodo_busqueda:By|str, texto_busqueda:str) -> bool:
        """ Clickea el elemento hijo con estrategias de reintento """
        elemento = self.encontrar_elemento_desde_elemento(elemento_padre, metodo_busqueda, texto_busqueda, False)
        elemento = self.esperar_elemento_clickeable(metodo_busqueda, texto_busqueda, elemento_padre=elemento_padre)
        if not elemento: return False
        
        return self._click_elemento_con_reintentos_desde_elemento(elemento, texto_busqueda)
    
    def _click_elemento_con_reintentos_desde_elemento(self, elemento: WebElement, texto_busqueda:str, max_intentos:int=3) -> bool:
        """ Clickea el elemento hijo usando múltiples estrategias """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de hacer click en un elemento hijo.")
        
        for intento in range(max_intentos):
            try:
                if intento == 0:
                    # Estrategia 1: Click directo
                    self.mostrar(f"🔍 Intento {intento + 1}: Click directo en elemento hijo")
                    self.__desplazar_elemento_a_vista(elemento)
                    elemento.click()
                    # self.mostrar(f"✅ Click exitoso en elemento hijo {texto_busqueda}")
                    return True
                    
                elif intento == 1:
                    # Estrategia 2: JavaScript click
                    # self.mostrar(f"🔍 Intento {intento + 1}: JavaScript click en elemento hijo")
                    self._driver.execute_script("arguments[0].click();", elemento)
                    # self.mostrar(f"✅ JavaScript click exitoso en elemento hijo {texto_busqueda}")
                    return True
                    
                elif intento == 2:
                    # Estrategia 3: ActionChains click
                    # self.mostrar(f"🔍 Intento {intento + 1}: ActionChains click en elemento hijo")
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self._driver)
                    actions.move_to_element(elemento).click().perform()
                    # self.mostrar(f"✅ ActionChains click exitoso en elemento hijo {texto_busqueda}")
                    return True
                    
            except ElementClickInterceptedException:
                self.mostrar(f"❌ Intento {intento + 1}: Elemento hijo {texto_busqueda} está siendo interceptado", True)
                if intento < max_intentos - 1:
                    self.mostrar(f"🔄 Reintentando con estrategia alternativa...")
                    self.demora()
                continue
                
            except Exception as e:
                self.mostrar(f"❌ Intento {intento + 1}: Error al hacer click en elemento hijo {texto_busqueda}: {str(e)}", True)
                if intento < max_intentos - 1:
                    self.mostrar(f"🔄 Reintentando con estrategia alternativa...")
                    self.demora()
                continue
        
        self.mostrar(f"❌ No se pudo hacer click en elemento hijo {texto_busqueda} después de {max_intentos} intentos", True)
        return False
    
    def click_elemento_en_iframe(self, iframe_selector:str, metodo_busqueda:By|str, texto_busqueda:str) -> bool:
        """ 
        Clickea un elemento dentro de un iframe específico 
        
        Args:
            iframe_selector: Selector del iframe (ej: 'iframe[name="main"]' o '#iframe-id')
            metodo_busqueda: Método para buscar el elemento dentro del iframe
            texto_busqueda: Selector del elemento dentro del iframe
        """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de buscar un elemento dentro de un iframe.")
        
        try:
            # Guardar el contexto actual
            contexto_original = self._driver.current_window_handle
            
            # Encontrar y cambiar al iframe
            iframe = self.encontrar_elemento(By.CSS_SELECTOR, iframe_selector)
            if not iframe:
                self.mostrar(f"❌ No se encontró el iframe {iframe_selector}", True)
                return False
            
            self.mostrar(f"🔄 Cambiando al iframe {iframe_selector}")
            self._driver.switch_to.frame(iframe)
            
            # Intentar hacer click en el elemento dentro del iframe
            resultado = self._click_elemento_con_reintentos(metodo_busqueda, texto_busqueda)
            
            # Volver al contexto original
            self._driver.switch_to.default_content()
            self.mostrar(f"🔄 Volviendo al contexto principal")
            
            return resultado
            
        except Exception as e:
            # Asegurar que volvemos al contexto original en caso de error
            try:
                self._driver.switch_to.default_content()
            except:
                pass
            
            self.mostrar(f"❌ Error al hacer click en elemento dentro del iframe: {str(e)}", True)
            return False
        
    def click_button(self, texto_descripcion:str, metodo_busqueda:By|str, texto_busqueda:str) -> None:
        """ Clickea el botón primero por su texto_descripcion y sino encuentra por el texto_busqueda """
        xpath = f"//button[(text()='{texto_descripcion}' or @value='{texto_descripcion}')]"
        if not self.click_elemento(By.XPATH, xpath):
            if not self.click_elemento(metodo_busqueda, texto_busqueda):
                self.mostrar(f"No se encontró el botón {texto_descripcion} o {texto_busqueda}", True)
                self.cerrar_navegador()
            
    def __desplazar_elemento_a_vista(self, elemento: WebElement) -> None:
        """ Se desplaza la vista hasta el elemento """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de desplazar un elemento a la vista.")
        
        self._driver.execute_script("""arguments[0].scrollIntoView({block: 'center', inline: 'center'});""", elemento)
        self.demora()
        
    def encontrar_elemento(self, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> WebElement | None:
        """ Encuentra el elemento y espera a que esté presente """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de buscar un elemento.")
        
        try:
            elemento = WebDriverWait(self._driver, self.tiempo_demora).until(
                EC.visibility_of_element_located((str(metodo_busqueda), texto_busqueda))
            )
            elemento = WebDriverWait(self._driver, self.tiempo_demora).until(
                EC.presence_of_element_located((str(metodo_busqueda), texto_busqueda))
            )
            self.__desplazar_elemento_a_vista(elemento)
        except TimeoutException as e:
            if tiene_que_estar: self.mostrar(f"No se encontró el elemento {texto_busqueda} en el tiempo previsto", True)
            elemento = None
        except Exception as e:
            elemento = None
        finally:
            return elemento
    
    def encontrar_elemento_desde_elemento(self, elemento_padre:WebElement, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> WebElement | None:
        """ Encuentra el elemento hijo"""
        try:
            elemento = elemento_padre.find_element(str(metodo_busqueda), texto_busqueda)
        except NoSuchElementException as e:
            if tiene_que_estar: self.mostrar(f"No se encontró el elemento {texto_busqueda} con el metodo {metodo_busqueda}", True)
            return None
        except Exception as e:
            if tiene_que_estar: self.mostrar(f"Ocurrió un error al buscar {texto_busqueda}", True)
            return None
        return elemento
    
    def encontrar_elemento_y_elementos(self, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> list[WebElement] | None:
        """ Encuentra al elemento padre desde el metodo y el texto introducido y retorna los elementos hijos cuando estén presentes """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de buscar un elemento.")
        
        elemento_padre = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        try:
            if elemento_padre:
                elementos = WebDriverWait(self._driver, self.tiempo_demora).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//*"))
                )
                elementos = elemento_padre.find_elements(By.XPATH, ".//*")
            else:
                elementos = []
            
        except Exception as e:
            if tiene_que_estar: self.mostrar(f"No se encontraron los elementos en {texto_busqueda}", True)
            return None
        return elementos 
    
    def encontrar_elementos_desde_elemento(self, elemento_padre:WebElement, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> list[WebElement] | None:
        """ Encuentra los elementos hijos """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de buscar un elemento.")
        
        try:
            elementos = WebDriverWait(self._driver, self.tiempo_demora).until(
                EC.presence_of_all_elements_located((str(metodo_busqueda), texto_busqueda))
            )
            elementos = elemento_padre.find_elements(str(metodo_busqueda), texto_busqueda)
        except NoSuchElementException as e:
            if tiene_que_estar: self.mostrar(f"No se encontraron los elementos {texto_busqueda}", True)
            return None
        return elementos   
    
    def encontrar_elementos(self, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> list[WebElement] | None:
        """ Encuentra los elementos y espera a que estén presentes """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de buscar un elemento.")
        
        try:
            elementos = WebDriverWait(self._driver, self.tiempo_demora).until(
                EC.presence_of_all_elements_located((str(metodo_busqueda), texto_busqueda))
            )
        except Exception as e:
            if tiene_que_estar: self.mostrar(f"No se encontraron los elementos {texto_busqueda}", True)
            return None
        return elementos    
        
    def ingresar_texto(self, metodo_busqueda:By|str, texto_busqueda:str, texto_a_ingresar:str) -> None:
        """ Ingresa texto en el elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            elemento.clear()
            elemento.send_keys(texto_a_ingresar)
            self.demora()
            
    def ingresar_comando(self, comando:str) -> None:
        """ Ingresa un comando en la consola """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de ingresar un comando.")
        
        self._driver.execute_script(comando)
        
    def presionar_enter(self, metodo_busqueda:By|str, texto_busqueda: str) -> None:
        """ Presiona la tecla Enter en el elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            elemento.send_keys(Keys.ENTER)
            
    def presionar_tecla(self, metodo_busqueda:By|str, texto_busqueda: str, tecla: str) -> None:
        """ Presiona una tecla en el elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            elemento.send_keys(tecla)     
   
    def seleccionar_opcion_en_desplegable(self, metodo_busqueda:By|str, texto_busqueda: str, nombre_opcion: str, valor_opcion: str|None=None, reintentos: int=0) -> bool:
        """ Selecciona una opción en un desplegable """
        if reintentos >= self.reintentos:
            self.mostrar(f"No se encontró la opción {nombre_opcion} después de varios intentos", True)
            return False

        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if not elemento: 
            self.demora()
            return self.seleccionar_opcion_en_desplegable(metodo_busqueda, texto_busqueda, nombre_opcion, valor_opcion, reintentos + 1)
        if not isinstance(elemento, WebElement): 
            return False

        desplegable = Select(elemento)

        if valor_opcion: 
            try:
                desplegable.select_by_value(valor_opcion)
                if self.__verificar_opcion_seleccionada(metodo_busqueda, texto_busqueda, nombre_opcion): 
                    return True
            except NoSuchElementException as e:
                # self.mostrar(f"No se encontró la opción por su valor {valor_opcion}", True)
                self.demora()
            return self.seleccionar_opcion_en_desplegable(metodo_busqueda, texto_busqueda, nombre_opcion, valor_opcion, reintentos + 1)

        try:
            desplegable.select_by_visible_text(nombre_opcion)
            if self.__verificar_opcion_seleccionada(metodo_busqueda, texto_busqueda, nombre_opcion): 
                return True
        except NoSuchElementException as e:
            # self.mostrar(f"No se encontró la opción {nombre_opcion}", True)
            return False

        self.demora()
        return self.seleccionar_opcion_en_desplegable(metodo_busqueda, texto_busqueda, nombre_opcion, valor_opcion, reintentos + 1)
        
    def __verificar_opcion_seleccionada(self, metodo_busqueda:By|str, texto_busqueda: str, nombre_opcion: str) -> bool:
        """ Verifica que la opción seleccionada sea la correcta """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if not isinstance(elemento, WebElement): return False
        desplegable = Select(elemento)
        return desplegable.first_selected_option.text == nombre_opcion
            
    def valor_en_elemento(self, metodo_busqueda:By|str, texto_busqueda: str) -> str|None:
        """ Obtiene el valor de un elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            return elemento.get_attribute("value")
        return ""
    
    def obtener_texto_elemento(self, metodo_busqueda:By|str, texto_busqueda: str) -> str:
        """ Obtiene el texto de un elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            return elemento.text.strip()
        return ''
   
    def cambiar_ventana(self):
        """ Cambia a la última ventana del navegador """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de cambiar de ventana.")
        
        ventanas = self.esperar_nueva_pestaña(self._driver.window_handles)
        self._driver.switch_to.window(ventanas[-1])
        self.mostrar(f"Cambiando a la ventana {self._driver.title}")
        self.demora()
        
    def esperar_nueva_pestaña(self, ventanas: list[str]) -> list[str]:
        """ Espera a que se abra una nueva pestaña """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de esperar una nueva pestaña.")
        
        WebDriverWait(self._driver, self.tiempo_demora).until(
            EC.new_window_is_opened(ventanas)
        )
        return self._driver.window_handles
    
    def cambiar_directorio_descargas(self):
        """ Cambia el directorio de descargas """
        pass

    def obtener_tabla_en_data_frame(self, metedo_busqueda:By|str, texto_busqueda: str) -> pd.DataFrame| None:
        """ 
        Obtiene una tabla en un DataFrame con múltiples parsers como fallback.
        Prioriza lxml > html5lib > bs4 para máxima compatibilidad.
        """
        tabla = self.encontrar_elemento(metedo_busqueda, texto_busqueda)
        if not tabla: return None
        
        outer_html = tabla.get_attribute('outerHTML') or ""
        if not outer_html: return None
        
        # Lista de parsers en orden de preferencia
        parsers = ['lxml', 'html5lib', 'bs4', None]  # None usa el parser por defecto
        
        for parser in parsers:
            try:
                if parser:
                    df = pd.read_html(StringIO(outer_html), flavor=parser)[0]
                else:
                    df = pd.read_html(StringIO(outer_html))[0]
                
                # Si llegamos aquí, el parsing fue exitoso
                if parser:
                    self.mostrar(f"✅ Tabla parseada exitosamente con: {parser}")
                else:
                    self.mostrar("✅ Tabla parseada exitosamente con parser por defecto")
                return df
                
            except ImportError as e:
                if 'lxml' in str(e):
                    self.mostrar(f"⚠️ Parser {parser} no disponible: {e}", True)
                    continue
                else:
                    raise e
            except Exception as e:
                self.mostrar(f"⚠️ Error con parser {parser}: {e}", True)
                continue
        
        # Si ningún parser funcionó, retornar None
        self.mostrar("❌ No se pudo parsear la tabla con ningún parser disponible", True)
        return None
    
    def obtener_filas_tabla(self, metedo_busqueda:By|str, texto_busqueda: str) -> list[WebElement]| None:
        """ Obtiene las filas de una tabla """
        tabla = self.encontrar_elemento(metedo_busqueda, texto_busqueda)
        if not tabla: return []
        self.demora()
        self.__desplazar_elemento_a_vista(tabla)
        return self.encontrar_elementos_desde_elemento(tabla, By.TAG_NAME, "tr")
    
    def obtener_columnas_fila(self, fila: WebElement) -> list[WebElement]| None:
        """ Obtiene las columnas de una fila """
        return self.encontrar_elementos_desde_elemento(fila, By.TAG_NAME, "th")
    
    def click_boton_en_celda(self, fila: WebElement) -> None:
        """ Clickea un botón en una celda """
        celdas = self.encontrar_elementos_desde_elemento(fila, By.TAG_NAME, "td")
        if not celdas or len(celdas) == 0: return
        
        for celda in celdas:
            if not self.click_elemento_desde_elemento(celda, By.CLASS_NAME, "fa-print"):
                self.mostrar("No se encontró el botón de descarga", True)
                self.demora()
                
            return
    
    def _obtener_PID_activo(self):
        """Obtiene el PID del proceso de Chrome controlado por Selenium."""
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de obtener el PID.")
        chrome_pid = None
        if hasattr(self._driver, "service") and self._driver.service is not None and hasattr(self._driver.service, "process") and self._driver.service.process is not None:
            chrome_pid = self._driver.service.process.pid
        if not chrome_pid:
            raise Exception("No se pudo obtener el PID del proceso de Chrome.")
        return chrome_pid

    def _buscar_proceso_chrome(self, chrome_pid):
        """Busca el proceso hijo que es la ventana real de Chrome."""
        import psutil
        chrome_process = psutil.Process(chrome_pid)
        child_pids = [p.pid for p in chrome_process.children(recursive=True) if "chrome" in p.name().lower()]
        if not child_pids:
            raise Exception("No se encontró el proceso de la ventana de Chrome.")
        return child_pids[0]

    def _set_focus(self, child_pid):
        """Establece el foco en la ventana de Chrome correspondiente al PID dado."""
        from pywinauto import Application
        app = Application(backend="uia").connect(process=child_pid, timeout=5)
        window = app.top_window()
        window.set_focus()
        return window

    def activar_ventana(self):
        """ Trae al frente la ventana de Chrome asociada a esta instancia """
        try:
            chrome_pid = self._obtener_PID_activo()
            child_pid = self._buscar_proceso_chrome(chrome_pid)
            self._set_focus(child_pid)
        except Exception as e:
            self.mostrar(f"No se pudo activar la ventana de Chrome: {e}", True)
            
    def enviar_tecla_ventana(self, *teclas: str):
        """
        Envía una o varias teclas directamente a la ventana de Chrome.
        Ejemplo: enviar_tecla_ventana("F5"), enviar_tecla_ventana("ctrl", "s")
        """
        # Verificación básica de GUI para entornos sin GUI
        try:
            import psutil
            # Verificar si explorer.exe está corriendo (indicativo de GUI activa en Windows)
            gui_available = any(proc.name().lower() == 'explorer.exe' for proc in psutil.process_iter(['name']))
            if not gui_available:
                self.mostrar("⚠️ GUI no disponible (explorer.exe no encontrado), saltando envío de teclas", True)
                return
        except Exception as e:
            self.mostrar(f"⚠️ No se pudo verificar GUI: {str(e)}, continuando...", True)

        try:
            from pywinauto import keyboard

            self.activar_ventana()
            # Mapear nombres de teclas especiales a la sintaxis de pywinauto
            special_keys = {
                "F1": "{F1}", "F2": "{F2}", "F3": "{F3}", "F4": "{F4}", "F5": "{F5}", "F6": "{F6}",
                "F7": "{F7}", "F8": "{F8}", "F9": "{F9}", "F10": "{F10}", "F11": "{F11}", "F12": "{F12}",
                "ESC": "{ESC}", "TAB": "{TAB}", "ENTER": "{ENTER}", "DEL": "{DEL}", "DELETE": "{DEL}",
                "INS": "{INSERT}", "INSERT": "{INSERT}", "HOME": "{HOME}", "END": "{END}",
                "PGUP": "{PGUP}", "PGDN": "{PGDN}", "LEFT": "{LEFT}", "RIGHT": "{RIGHT}", "UP": "{UP}", "DOWN": "{DOWN}",
                "CTRL": "^", "CONTROL": "^", "ALT": "%", "SHIFT": "+", "WIN": "{LWIN}"
            }

            def translate_key(key: str):
                k = key.upper()
                return special_keys.get(k, key)

            if len(teclas) == 1:
                # Si es una sola tecla, traducir si es especial
                secuencia = translate_key(teclas[0])
            else:
                # Traducir cada tecla y unir con combinadores
                secuencia = ""
                for t in teclas:
                    tk = translate_key(t)
                    # Si es un modificador (^, +, %) no agregar espacio
                    if tk in ("^", "+", "%"):
                        secuencia += tk
                    else:
                        secuencia += tk
            keyboard.send_keys(secuencia, pause=0.05)
            self.demora()
            
        except Exception as e:
            self.mostrar(f"No se pudo enviar la(s) tecla(s) '{'+'.join(teclas)}' a la ventana de Chrome: {e}", True)
            
    def enviar_tecla_ventana_con_selenium(self, *teclas: str, elemento: WebElement | None = None):
        """
        Envía una o varias teclas simultaneas directamente a la ventana de Chrome usando Selenium.
        
        Tambien permite enviar teclas a un elemento específico si se pasa como argumento.
        
        ---
        Ejemplo
        ```
        enviar_tecla_ventana_con_selenium("F5")
        enviar_tecla_ventana_con_selenium(("ctrl", "s"), elemento=elemento)
        enviar_tecla_ventana_con_selenium(("ctrl", "c"), elemento=elemento)
        ```
        
        ---
        Excepciones:
        - Si no se puede activar la ventana de Chrome.
        - Si no se puede enviar la(s) tecla(s) a la ventana de Chrome.
        """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de enviar teclas.")
        
        try:
            from selenium.webdriver.common.keys import Keys
            
            self.activar_ventana()
            
            keys_to_send = []
            for tecla in teclas:
                if hasattr(Keys, tecla.upper()):
                    keys_to_send.append(getattr(Keys, tecla.upper()))
                else:
                    keys_to_send.append(tecla)
                    
            if elemento:
                # Si se pasa un elemento, enviar las teclas a ese elemento de forma simultanea
                elemento.send_keys(*keys_to_send)
            else:
                # Si no se pasa un elemento, enviar las teclas a la ventana activa
                self._driver.find_element(By.TAG_NAME, 'body').send_keys(*keys_to_send)

            self.demora()
            self.mostrar(f"Tecla(s) '{'+'.join(teclas)}' enviada(s) a la ventana activa de Chrome")
        except Exception as e:
            self.mostrar(f"No se pudo enviar la(s) tecla(s) '{'+'.join(teclas)}' a la ventana de Chrome: {e}", True)
            
    def enviar_tecla_elemento_en_iframe(self, metodo_busqueda:By|str, texto_busqueda:str, *teclas: str, iframe:WebElement|None=None):
        """
        
        """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de enviar teclas.")
        
        try:
            from selenium.webdriver.common.keys import Keys
            
            if iframe:
                self._driver.switch_to.frame(iframe)
            else:
                # Buscar todos los iframes
                iframes = self.encontrar_elementos(By.TAG_NAME, "iframe", tiene_que_estar=False)
                if not iframes:
                    self.mostrar("No se encontraron iframes en la página", True)
                    return
                
            # Buscar el elemento dentro de los iframes
            for iframe in iframes:
                try:
                    self._driver.switch_to.frame(iframe)
                    elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
                    if elemento:
                        break
                    self._driver.switch_to.default_content()
                except Exception:
                    self._driver.switch_to.default_content()
                    continue
                
            # Si no se encontró el elemento en ningún iframe
            if not elemento:
                self.mostrar(f"No se encontró el elemento {texto_busqueda} en el iframe", True)
                self._driver.switch_to.default_content()
                return
            
            keys_to_send = []
            for tecla in teclas:
                if hasattr(Keys, tecla.upper()):
                    keys_to_send.append(getattr(Keys, tecla.upper()))
                else:
                    keys_to_send.append(tecla)
                    
            elemento.send_keys(*keys_to_send)
            self.demora()
            self.mostrar(f"Tecla(s) '{'+'.join(teclas)}' enviada(s) al elemento {texto_busqueda} en el iframe")
            
            # Volver al contexto principal
            self._driver.switch_to.default_content()
            
        except Exception as e:
            try:
                self._driver.switch_to.default_content()
            except:
                pass
            self.mostrar(f"No se pudo enviar la(s) tecla(s) '{'+'.join(teclas)}' al elemento {texto_busqueda} en el iframe: {e}", True)        
    
    def pegar_portapapeles_en_ventana_activa(self):
        """ Pega el contenido del portapapeles en la ventana activa de Chrome """
        # Verificación básica de GUI para entornos sin GUI
        try:
            import psutil
            # Verificar si explorer.exe está corriendo (indicativo de GUI activa en Windows)
            gui_available = any(proc.name().lower() == 'explorer.exe' for proc in psutil.process_iter(['name']))
            if not gui_available:
                self.mostrar("⚠️ GUI no disponible (explorer.exe no encontrado), saltando pegado", True)
                return
        except Exception as e:
            self.mostrar(f"⚠️ No se pudo verificar GUI: {str(e)}, continuando...", True)

        try:
            from pywinauto import keyboard

            self.activar_ventana()
            keyboard.send_keys("^v")  # Ctrl + V para pegar
            self.demora()
            self.mostrar("Contenido del portapapeles pegado en la ventana activa de Chrome")
        except Exception as e:
            self.mostrar(f"No se pudo pegar el contenido del portapapeles: {e}", True)
            
    def buscar_elemento_en_iframes(self, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> tuple[WebElement | None, str | None]:
        """ Busca un elemento dentro de iframes y devuelve el primer elemento encontrado y su texto """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de buscar un elemento en iframes.")
        
        iframes = self.encontrar_elementos(By.TAG_NAME, "iframe", tiene_que_estar)
        if iframes:
            for iframe in iframes:
                try:
                    self._driver.switch_to.frame(iframe)
                    elementos = self.encontrar_elementos(metodo_busqueda, texto_busqueda, tiene_que_estar)
                    if elementos:
                        texto = elementos[0].text  # Accede al texto antes de salir del iframe
                        self._driver.switch_to.default_content()
                        return elementos[0], texto
                    self._driver.switch_to.default_content()
                except Exception:
                    self._driver.switch_to.default_content()
                    continue
        return None, None
    
    def buscar_elemento_en_iframes_sin_cerrar(self, metodo_busqueda:By|str, texto_busqueda:str, tiene_que_estar:bool=True) -> WebElement | None:
        """ Busca un elemento dentro de iframes sin cerrar el contexto actual """
        if not self._driver:
            raise ValueError("El navegador no está abierto. Por favor, abre el navegador antes de buscar un elemento en iframes.")
        
        iframes = self.encontrar_elementos(By.TAG_NAME, "iframe", tiene_que_estar)
        if iframes:
            for iframe in iframes:
                try:
                    self._driver.switch_to.frame(iframe)
                    elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda, tiene_que_estar)
                    if elemento:
                        return elemento
                    self._driver.switch_to.default_content()
                except Exception:
                    self._driver.switch_to.default_content()
                    continue
        return None
    
    def buscar_y_click_en_todos_los_iframes(self, metodo_busqueda, xpath_busqueda: str) -> bool:
        """
        Busca un elemento dentro de todos los iframes y hace click usando los métodos robustos de Chrome.
        Retorna True si encuentra y hace click exitosamente, False en caso contrario.
        """
        try:
            if not self._driver:
                self.mostrar("❌ Driver no disponible", True)
                return False
            
            # Obtener todos los iframes
            iframes = self.encontrar_elementos(By.TAG_NAME, "iframe", tiene_que_estar=False)
            if not iframes:
                self.mostrar("⚠️ No se encontraron iframes en la página")
                # Intentar buscar directamente sin iframe como fallback
                return self.click_elemento_directo(metodo_busqueda, xpath_busqueda)
            
            # self.mostrar(f"🔍 Buscando en {len(iframes)} iframe(s)")
            
            for i, iframe in enumerate(iframes):
                try:
                    # Cambiar al iframe
                    self._driver.switch_to.frame(iframe)
                    # self.mostrar(f"📂 Buscando en iframe {i + 1}")
                    
                    # Intentar usar el método click_elemento de Chrome dentro del iframe
                    if self.click_elemento_directo(metodo_busqueda, xpath_busqueda):
                        # self.mostrar(f"✅ Click exitoso en iframe {i + 1}")
                        self._driver.switch_to.default_content()
                        return True
                    
                    # Volver al contenido principal
                    self._driver.switch_to.default_content()
                    
                except Exception as iframe_error:
                    # Asegurar que volvemos al contenido principal si hay error
                    try:
                        self._driver.switch_to.default_content()
                    except:
                        pass
                    self.mostrar(f"⚠️ Error en iframe {i + 1}: {str(iframe_error)}")
                    continue
            
            return False
            
        except Exception as e:
            # Asegurar que volvemos al contenido principal
            try:
                if self._driver:
                    self._driver.switch_to.default_content()
            except:
                pass
            self.mostrar(f"❌ Error general en buscar_y_click_en_todos_los_iframes: {str(e)}", True)
            return False
    
    def click_elemento_directo(self, metodo_busqueda, xpath_busqueda: str) -> bool:
        """
        Hace click en un elemento usando los métodos robustos de Chrome.
        Este método maneja la espera, visibilidad y clickeabilidad automáticamente.
        """
        try:
            # Primero verificar si el elemento existe
            elemento = self.encontrar_elemento(metodo_busqueda, xpath_busqueda, tiene_que_estar=False)
            if not elemento:
                return False
            
            # Usar el método click_elemento de Chrome que maneja esperas y scrolling
            return self.click_elemento(metodo_busqueda, xpath_busqueda)
            
        except Exception as e:
            self.mostrar(f"⚠️ Error en click directo: {str(e)}")
            return False