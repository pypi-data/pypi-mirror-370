# src/Windows/Windows.py

import os
import platform
from datetime import datetime
import time
import subprocess
import psutil
from functools import wraps
from .Terminal import Terminal

class Windows(Terminal):
    def __init__(self, dev: bool = False):
        super().__init__(dev=dev)
        
        # Estado GUI para verificación eficiente
        self._gui_verificada = False
        self._ultimo_check_gui = None
        self._intentos_recuperacion_gui = 0
        
        # Determinar la carpeta de descargas personalizada según el sistema operativo
        if platform.system() == "Windows":
            self.carpeta_descargas_personalizada = os.path.join(os.environ.get("USERPROFILE", ""), "DescargaPersonalizada")
        else:
            self.carpeta_descargas_personalizada = os.path.join(os.environ.get("HOME", ""), "DescargaPersonalizada")
        
        # Crear la carpeta si no existe
        if not os.path.exists(self.carpeta_descargas_personalizada):
            os.makedirs(self.carpeta_descargas_personalizada, exist_ok=True)
        
        # Purga inicial de la carpeta
        self.purgar_carpeta_descargas_personalizada()

    @staticmethod
    def resolver_ruta_archivo(nombre_archivo: str, usar_directorio_script: bool = True) -> str:
        """
        Resuelve rutas de archivos correctamente cuando se ejecuta desde tareas programadas.
        
        Soluciona el problema común donde aplicaciones empaquetadas ejecutadas desde
        tareas programadas de Windows tienen un directorio de trabajo actual (cwd) 
        diferente al esperado. Puede usar el directorio del script ejecutable o el cwd.
        
        ---
        Se utiliza para resolver rutas de archivos .env, configuración y otros archivos
        que deben estar junto al ejecutable en aplicaciones empaquetadas distribuidas.
        
        ---
        ### Ejemplo
        ```python
        # Para archivo .env.production junto al ejecutable
        ruta_env = Windows.resolver_ruta_archivo('.env.production')
        
        # Para archivo en directorio actual (comportamiento original)
        archivo_estado = Windows.resolver_ruta_archivo('estado.json', usar_directorio_script=False)
        
        # Para verificar si archivo existe
        ruta_config = Windows.resolver_ruta_archivo('config.ini')
        if os.path.exists(ruta_config):
            print(f"📁 Archivo encontrado en: {ruta_config}")
        ```
        >>> "C:\\path\\to\\executable\\.env.production"  # Ruta absoluta resuelta
        
        ---
        ### Raises
        #### Exception
        - Si no se puede determinar la ruta del ejecutable actual
        - Si ocurre un error al resolver la ruta del archivo
        """
        try:
            if usar_directorio_script:
                # Obtener directorio del script/ejecutable actual
                import sys
                if getattr(sys, 'frozen', False):
                    # Aplicación empaquetada (exe)
                    directorio_base = os.path.dirname(sys.executable)
                else:
                    # Script Python normal
                    import inspect
                    frame = inspect.currentframe()
                    if frame and frame.f_back:
                        caller_file = frame.f_back.f_globals.get('__file__')
                        if caller_file:
                            directorio_base = os.path.dirname(os.path.abspath(caller_file))
                        else:
                            directorio_base = os.getcwd()
                    else:
                        directorio_base = os.getcwd()
                
                ruta_resuelta = os.path.join(directorio_base, nombre_archivo)
            else:
                # Usar directorio de trabajo actual (comportamiento original)
                ruta_resuelta = os.path.join(os.getcwd(), nombre_archivo)
            
            # Normalizar ruta para Windows
            ruta_resuelta = os.path.normpath(ruta_resuelta)
            
            return ruta_resuelta
            
        except Exception as e:
            # Fallback al directorio actual si hay error
            return os.path.join(os.getcwd(), nombre_archivo)

    # Excepción personalizada para GUI
    class GUINotAvailableError(Exception):
        """
        Excepción lanzada cuando GUI no está disponible para automatización.
        
        Se utiliza cuando operaciones que requieren interacción visual
        no pueden ejecutarse porque no hay sesión de escritorio activa.
        
        ---
        ### Ejemplo
        ```python
        try:
            self.enviar_tecla_ventana('F5')
        except GUINotAvailableError as e:
            self.mostrar(f"❌ Error GUI: {str(e)}", True)
        ```
        >>> None  # Maneja error cuando GUI no disponible
        
        ---
        ### Raises
        #### Exception
        - Hereda de Exception base para manejo estándar errores
        """
        pass

    @staticmethod
    def requiere_gui(func):
        """
        Decorador que garantiza GUI activa antes de ejecutar método.
        
        Verifica que haya una sesión de escritorio activa en Windows antes de ejecutar
        métodos que requieren interacción visual como envío de teclas, clicks o screenshots.
        Implementa cache de verificación para optimizar rendimiento y recuperación automática.
        
        ---
        Se utiliza dentro de métodos que requieren interacción con elementos visuales.
        Ejemplo de uso típico en clases que heredan de Windows para operaciones GUI.
        
        ---
        ### Ejemplo
        ```python
        @Windows.requiere_gui
        def enviar_tecla_ventana(self, tecla):
            # Método que necesita GUI para envío de teclas
            pyautogui.press(tecla)
            
        @Windows.requiere_gui  
        def tomar_screenshot(self, nombre_archivo=None):
            # Método que necesita GUI para captura de pantalla
            screenshot = pyautogui.screenshot()
        ```
        >>> None  # Ejecuta solo si GUI está disponible
        
        ---
        ### Raises
        #### GUINotAvailableError
        - Si no hay sesión de escritorio activa en Windows después de intentos recuperación
        - Si no se pueden detectar procesos críticos de GUI (explorer.exe, dwm.exe)
        - Si la verificación de GUI falla después de 3 intentos de recuperación automática
        
        #### Exception
        - Si ocurre un error inesperado durante la verificación o recuperación de GUI
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._verificar_sesion_gui_activa():
                raise Windows.GUINotAvailableError(
                    f"🖥️ GUI no disponible para ejecutar {func.__name__}. "
                    "Verifique que hay una sesión de escritorio activa en la VM. "
                    "Para solucionar: abrir RDP, configurar auto-login o verificar servicio GUI."
                )
            
            return func(self, *args, **kwargs)
        
        return wrapper

    def _verificar_sesion_gui_activa(self) -> bool:
        """
        Verifica si hay una sesión GUI activa en Windows.
        
        Comprueba la presencia de procesos críticos del escritorio Windows y
        valida que la sesión esté disponible para automatización RPA. Implementa
        cache temporal para optimizar verificaciones repetidas y recuperación automática.
        
        ---
        Se utiliza dentro del decorador `@requiere_gui` para validación automática.
        Realiza verificación inteligente con cache de 30 segundos para eficiencia.
        
        ---
        ### Ejemplo
        ```python
        if self._verificar_sesion_gui_activa():
            self.mostrar("✅ GUI disponible para automatización")
            self.tomar_screenshot("estado_gui")
        else:
            self.mostrar("❌ GUI no disponible", True)
            self._intentar_recuperacion_gui()
        ```
        >>> True  # Si GUI está activa y disponible
        
        ---
        ### Raises
        #### Exception
        - Si ocurre un error al verificar procesos del sistema
        - Si no se puede acceder a la información de sesiones Windows
        """
        try:
            # Cache de verificación para evitar checks excesivos (optimización performance)
            ahora = datetime.now()
            if (self._ultimo_check_gui and 
                (ahora - self._ultimo_check_gui).total_seconds() < 30 and
                self._gui_verificada):
                return True
            
            self.mostrar("🔍 Verificando disponibilidad de GUI...")
            
            # Verificar procesos críticos de GUI Windows
            procesos_gui_criticos = [
                'explorer.exe',  # Windows Explorer - crítico para escritorio
                'dwm.exe',       # Desktop Window Manager - crítico para ventanas
                'winlogon.exe'   # Windows Logon - crítico para sesión usuario
            ]
            
            # Obtener lista de procesos activos
            procesos_activos = {p.name().lower() for p in psutil.process_iter(['name'])}
            
            # Verificar que todos los procesos críticos estén presentes
            procesos_encontrados = []
            for proceso in procesos_gui_criticos:
                if proceso.lower() in procesos_activos:
                    procesos_encontrados.append(proceso)
            
            # Verificación adicional: sesión interactiva Windows
            gui_disponible = len(procesos_encontrados) >= 2
            
            if gui_disponible:
                # Verificación adicional: display disponible
                try:
                    resultado_display = subprocess.run(
                        ['powershell', '-Command', 'Get-WmiObject -Class Win32_VideoController | Select-Object Name'],
                        capture_output=True, text=True, timeout=10
                    )
                    display_activo = "Name" in resultado_display.stdout
                except:
                    display_activo = True  # Asumir disponible si no se puede verificar
                
                gui_disponible = gui_disponible and display_activo
            
            # Actualizar estado de cache
            self._ultimo_check_gui = ahora
            self._gui_verificada = gui_disponible
            
            if gui_disponible:
                self.mostrar(f"✅ GUI activa - Procesos detectados: {', '.join(procesos_encontrados)}")
                self._intentos_recuperacion_gui = 0  # Reset contador intentos
            else:
                self.mostrar(f"❌ GUI no disponible - Solo detectados: {', '.join(procesos_encontrados)}", True)
                
                # Intentar recuperación automática si es posible
                if self._intentos_recuperacion_gui < 3:
                    self.mostrar("🔄 Intentando recuperación automática de GUI...", True)
                    if self._intentar_recuperacion_gui():
                        return self._verificar_sesion_gui_activa()  # Re-verificar después de recuperación
                    self._intentos_recuperacion_gui += 1
            
            return gui_disponible
            
        except Exception as e:
            self.mostrar(f"❌ Error verificando GUI: {str(e)}", True)
            # En caso de error, asumir GUI no disponible por seguridad
            self._gui_verificada = False
            return False

    def _intentar_recuperacion_gui(self) -> bool:
        """
        Intenta recuperar sesión GUI automáticamente.
        
        Implementa estrategias de recuperación automática cuando GUI no está disponible.
        Incluye reinicio de explorer.exe, activación de sesión y notificación de estado.
        
        ---
        Se utiliza dentro de `_verificar_sesion_gui_activa` cuando GUI no está disponible.
        Implementa múltiples estrategias de recuperación con logging detallado de intentos.
        
        ---
        ### Ejemplo
        ```python
        if not self._verificar_sesion_gui_activa():
            if self._intentar_recuperacion_gui():
                self.mostrar("🔄 GUI recuperada exitosamente")
            else:
                self.mostrar("❌ No se pudo recuperar GUI automáticamente", True)
        ```
        >>> True  # Si logra recuperar GUI exitosamente
        
        ---
        ### Raises
        #### Exception
        - Si ocurre error durante estrategias de recuperación
        - Si no se pueden ejecutar comandos de sistema para recuperación
        """
        try:
            self.mostrar("🛠️ Ejecutando estrategias de recuperación GUI...")
            
            # Estrategia 1: Reiniciar Windows Explorer
            try:
                self.mostrar("🔄 Estrategia 1: Reiniciando Windows Explorer...")
                subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], 
                             capture_output=True, check=False)
                time.sleep(2)
                subprocess.run(['explorer.exe'], shell=True, check=False)
                time.sleep(5)
                self.mostrar("✅ Windows Explorer reiniciado")
            except Exception as e:
                self.mostrar(f"❌ Falló reinicio Explorer: {str(e)}", True)
            
            # Estrategia 2: Activar sesión con SendKeys simulado
            try:
                self.mostrar("🔄 Estrategia 2: Activando sesión con simulación teclas...")
                subprocess.run([
                    'powershell', '-Command', 
                    'Add-Type -AssemblyName System.Windows.Forms; '
                    '[System.Windows.Forms.SendKeys]::SendWait("{F15}")'
                ], capture_output=True, timeout=10)
                time.sleep(2)
                self.mostrar("✅ Señal de activación enviada")
            except Exception as e:
                self.mostrar(f"❌ Falló activación sesión: {str(e)}", True)
            
            # Estrategia 3: Verificar y activar servicios críticos GUI
            try:
                self.mostrar("🔄 Estrategia 3: Verificando servicios críticos...")
                servicios_criticos = ['UxSms', 'Themes', 'AudioSrv']
                for servicio in servicios_criticos:
                    resultado = subprocess.run(
                        ['sc', 'query', servicio], 
                        capture_output=True, text=True
                    )
                    if 'STOPPED' in resultado.stdout:
                        subprocess.run(['sc', 'start', servicio], 
                                     capture_output=True, check=False)
                        self.mostrar(f"🔄 Servicio {servicio} iniciado")
                
                self.mostrar("✅ Servicios críticos verificados")
            except Exception as e:
                self.mostrar(f"❌ Error verificando servicios: {str(e)}", True)
            
            # Esperar estabilización del sistema
            self.mostrar("⏳ Esperando estabilización del sistema...")
            time.sleep(3)
            
            self.mostrar("🔍 Recuperación completada, re-verificando estado...")
            return True
            
        except Exception as e:
            self.mostrar(f"❌ Error durante recuperación GUI: {str(e)}", True)
            return False

    def forzar_sesion_gui_activa(self) -> bool:
        """
        Fuerza activación de sesión GUI con estrategias avanzadas.
        
        Método público para forzar GUI cuando se detecta que no está disponible.
        Implementa estrategias más agresivas que la recuperación automática,
        incluyendo configuración de auto-login y tareas programadas.
        
        ---
        Se utiliza cuando se necesita garantizar GUI activa antes de procesos críticos RPA.
        Método más completo que recuperación automática, diseñado para configuración inicial.
        
        ---
        ### Ejemplo
        ```python
        if not self._verificar_sesion_gui_activa():
            self.mostrar("🚨 GUI no disponible, forzando activación...")
            if self.forzar_sesion_gui_activa():
                self.mostrar("✅ Sesión GUI forzada exitosamente")
            else:
                raise Exception("No se pudo establecer sesión GUI")
        ```
        >>> True  # Si logra establecer sesión GUI
        
        ---
        ### Raises
        #### Exception
        - Si todas las estrategias de forzado fallan
        - Si no tiene permisos administrativos para configuraciones críticas
        #### PermissionError
        - Si no puede modificar configuraciones del sistema
        """
        try:
            self.mostrar("🚨 Iniciando forzado de sesión GUI activa...")
            
            # Primero intentar recuperación estándar
            if self._intentar_recuperacion_gui():
                if self._verificar_sesion_gui_activa():
                    self.mostrar("✅ GUI recuperada con estrategias estándar")
                    return True
            
            # Estrategias avanzadas de forzado
            self.mostrar("🔧 Aplicando estrategias avanzadas de forzado...")
            
            # Estrategia avanzada 1: Crear y ejecutar tarea GUI keepalive
            try:
                self.mostrar("🔄 Creando tarea programada GUI keepalive...")
                
                comando_keepalive = (
                    'Add-Type -AssemblyName System.Windows.Forms; '
                    'while($true) { '
                    'try { [System.Windows.Forms.SendKeys]::SendWait("{F15}"); } '
                    'catch { } '
                    'Start-Sleep 300 '
                    '}'
                )
                
                # Crear tarea programada que mantenga GUI activa
                subprocess.run([
                    'schtasks', '/create', '/tn', 'GLGRPA_GUI_KeepAlive',
                    '/tr', f'powershell.exe -WindowStyle Hidden -Command "{comando_keepalive}"',
                    '/sc', 'onlogon', '/rl', 'highest', '/f'
                ], capture_output=True, check=False)
                
                # Ejecutar tarea inmediatamente
                subprocess.run([
                    'schtasks', '/run', '/tn', 'GLGRPA_GUI_KeepAlive'
                ], capture_output=True, check=False)
                
                self.mostrar("✅ Tarea GUI keepalive configurada")
                
            except Exception as e:
                self.mostrar(f"❌ Error configurando tarea keepalive: {str(e)}", True)
            
            # Estrategia avanzada 2: Verificar/configurar auto-login
            try:
                self.mostrar("🔄 Verificando configuración auto-login...")
                
                # Verificar si auto-login está habilitado
                resultado = subprocess.run([
                    'reg', 'query', 
                    'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon',
                    '/v', 'AutoAdminLogon'
                ], capture_output=True, text=True)
                
                if 'AutoAdminLogon' not in resultado.stdout or '0x1' not in resultado.stdout:
                    self.mostrar("⚠️ Auto-login no configurado. Para configurarlo manualmente:", True)
                    self.mostrar("💡 1. Ejecutar como admin: netplwiz", True)
                    self.mostrar("💡 2. Desmarcar 'Los usuarios deben escribir su nombre...'", True)
                    self.mostrar("💡 3. O usar configurador automático con credenciales", True)
                else:
                    self.mostrar("✅ Auto-login ya configurado")
                    
            except Exception as e:
                self.mostrar(f"❌ Error verificando auto-login: {str(e)}", True)
            
            # Esperar estabilización completa
            self.mostrar("⏳ Esperando estabilización completa del sistema...")
            time.sleep(5)
            
            # Verificación final
            gui_final = self._verificar_sesion_gui_activa()
            
            if gui_final:
                self.mostrar("🎉 ¡Sesión GUI forzada exitosamente!")
                self.mostrar("📋 Configuraciones aplicadas para mantener GUI persistente")
                return True
            else:
                self.mostrar("❌ No se pudo forzar GUI después de todas las estrategias", True)
                self.mostrar("💡 Soluciones manuales recomendadas:", True)
                self.mostrar("   • Abrir conexión RDP y mantenerla activa", True)
                self.mostrar("   • Configurar auto-login en Windows", True)
                self.mostrar("   • Verificar que VM tenga display/monitor virtual", True)
                return False
                
        except Exception as e:
            self.mostrar(f"❌ Error crítico forzando GUI: {str(e)}", True)
            return False
        
    def purgar_carpeta_descargas_personalizada(self):
        """ Purga la carpeta de descargas """
        
        # Obtener los archivos de la carpeta de descargas 
        archivos = [f for f in os.listdir(self.carpeta_descargas_personalizada)]
        
        # Eliminar los archivos
        for archivo in archivos:
            os.remove(os.path.join(self.carpeta_descargas_personalizada, archivo))

    def crear_carpeta_si_no_existe(self, carpeta: str) -> bool:
        """ Crea la carpeta de descargas si no existe """
        try:
            if not os.path.exists(carpeta):
                os.makedirs(carpeta)
            
            return True
        except Exception as e:
            return False
        
    def buscar_ultimo_archivo(self, ruta:str, extension: str) -> str:
        """ Busca el último archivo de una extensión específica en la carpeta de descargas """
        
        # Obtener los archivos de la carpeta de descargas
        archivos = [f for f in os.listdir(ruta) if f.endswith(extension)]
        
        # Si no se encontraron archivos, se lanza una excepción
        if not archivos:
            raise FileNotFoundError(f"No se encontraron archivos {extension} en la carpeta de descargas.")
        
        # Ordenar los archivos por fecha de modificación
        archivos.sort(key=lambda f: os.path.getmtime(os.path.join(ruta, f)), reverse=True)
        return os.path.join(ruta, archivos[0])
        
    def mover_archivo(self, ruta_archivo: str, ruta_destino: str) -> str| bool:
        """ Mueve un archivo a una carpeta destino """

        self.mostrar(f"Moviendo archivo {ruta_archivo} a {ruta_destino}")
        
        # Crear las carpetas si no existen
        if not self.crear_carpeta_si_no_existe(ruta_destino):
            self.mostrar(f"No se pudo crear la carpeta {ruta_destino}", True)
            return False

        # Obtener el nombre del archivo
        nombre_archivo = os.path.basename(ruta_archivo)
        nueva_ruta = os.path.join(ruta_destino, nombre_archivo)
        time.sleep(3)
        
        # Verificar si el archivo ya existe en la carpeta destino
        if os.path.exists(nueva_ruta):
            self.mostrar(f"El archivo {nombre_archivo} ya existe en la carpeta {ruta_destino}", True)
            return nueva_ruta
        
        # Mover el archivo
        try:
            os.rename(ruta_archivo, nueva_ruta)
        except Exception as e:
            self.mostrar(f"No se pudo mover el archivo {ruta_archivo} a la carpeta {ruta_destino}", True)
            self.mostrar(f"Error: {e}", True)
            return False
            
        return nueva_ruta
    
    def armar_estructura_de_carpetas(self, ruta: str) -> str| bool:
        r""" Arma la estructura de carpetas en la ruta indicada [ruta\anio\mes\dia]. Devuelve la ruta destino """
        try:
            # Obtener la fecha actual
            fecha_actual = datetime.now()
            anio = fecha_actual.strftime("%Y")
            mes = fecha_actual.strftime("%m")
            dia = fecha_actual.strftime("%d")
            
            # Crear la estructura de carpetas
            ruta_destino = os.path.join(ruta, anio, mes, dia)
            
            return ruta_destino
        except Exception as e:
            self.mostrar(f"No se pudo crear la estructura de carpetas en la ruta {ruta}")
            return False
        
    def copiar_al_portapapeles(self, texto: str) -> bool:
        """ Copia el texto al portapapeles """
        try:
            import pyperclip
            pyperclip.copy(texto)
            self.mostrar(f"📃 Texto copiado al portapapeles:\n{texto}")
            return True
        except ImportError:
            self.mostrar("❌ No se pudo importar la librería 'pyperclip'. Asegúrate de tenerla instalada.", True)
            return False
        except Exception as e:
            self.mostrar(f"❌ Error desconocido al copiar al portapapeles: {e}", True)
            return False
    
    @requiere_gui
    def tomar_screenshot(self, nombre_archivo: str | None = None) -> str:
        """ Toma un screenshot de la pantalla completa y lo guarda en la carpeta logs """
        try:
            import pyautogui
            
            # Generar nombre del archivo si no se proporciona
            if not nombre_archivo:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"screenshot_{timestamp}.png"
            
            # Asegurar que tenga extensión .png
            if not nombre_archivo.endswith('.png'):
                nombre_archivo += '.png'
            
            # Crear ruta en carpeta logs
            carpeta_logs = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
            if not os.path.exists(carpeta_logs):
                os.makedirs(carpeta_logs, exist_ok=True)
            
            ruta_screenshot = os.path.join(carpeta_logs, nombre_archivo)
            
            # Tomar screenshot
            screenshot = pyautogui.screenshot()
            screenshot.save(ruta_screenshot)
            
            self.mostrar(f"📸 Screenshot guardado en: {ruta_screenshot}")
            return ruta_screenshot
            
        except ImportError as e:
            if "pyscreeze" in str(e) or "Pillow" in str(e):
                self.mostrar("⚠️ Screenshot no disponible: falta dependencia Pillow/pyscreeze", True)
                self.mostrar("💡 Para habilitar screenshots, instalar: pip install Pillow", True)
            else:
                self.mostrar(f"❌ No se pudo importar pyautogui: {e}", True)
            return ""
        except Exception as e:
            if "pyscreeze" in str(e) or "Pillow" in str(e):
                self.mostrar("⚠️ Screenshot fallido: Pillow no compatible con esta versión de Python", True)
                self.mostrar("💡 Instalar versión compatible: pip install 'Pillow>=10.0.0'", True)
            else:
                self.mostrar(f"❌ Error al tomar screenshot: {e}", True)
            return ""

    @requiere_gui
    def enviar_tecla_ventana(self, *teclas) -> bool:
        """
        Envía combinaciones de teclas a la ventana activa.
        
        Permite enviar teclas individuales o combinaciones (Ctrl+C, Alt+Tab, etc.)
        usando pyautogui. Requiere GUI activa para funcionar correctamente.
        
        ---
        Se utiliza dentro de automatizaciones que requieren simulación de teclas.
        Método protegido por decorador @requiere_gui para garantizar funcionamiento.
        
        ---
        ### Ejemplo
        ```python
        # Tecla individual
        self.enviar_tecla_ventana('F5')
        
        # Combinación de teclas
        self.enviar_tecla_ventana('ctrl', 'c')
        self.enviar_tecla_ventana('alt', 'tab')
        self.enviar_tecla_ventana('shift', 'f3')
        ```
        >>> True  # Si las teclas se envían exitosamente
        
        ---
        ### Raises
        #### ImportError
        - Si pyautogui no está disponible o instalado
        #### Exception
        - Si ocurre error durante envío de teclas
        #### GUINotAvailableError
        - Si GUI no está activa (manejado por decorador)
        """
        try:
            import pyautogui
            
            if len(teclas) == 1:
                # Tecla individual
                pyautogui.press(teclas[0])
                self.mostrar(f"⌨️ Tecla enviada: {teclas[0]}")
            else:
                # Combinación de teclas
                pyautogui.hotkey(*teclas)
                self.mostrar(f"⌨️ Combinación enviada: {'+'.join(teclas)}")
            
            return True
            
        except ImportError:
            self.mostrar("❌ No se pudo importar pyautogui para envío de teclas", True)
            return False
        except Exception as e:
            self.mostrar(f"❌ Error enviando teclas: {str(e)}", True)
            return False

    @requiere_gui  
    def pegar_portapapeles_en_ventana_activa(self) -> bool:
        """
        Pega el contenido del portapapeles en la ventana activa.
        
        Utiliza la combinación Ctrl+V para pegar contenido del portapapeles
        en la ventana que tiene el foco actualmente.
        
        ---
        Se utiliza dentro de automatizaciones para pegar datos copiados previamente.
        Complementa el método `copiar_al_portapapeles` para flujo completo copiar/pegar.
        
        ---
        ### Ejemplo
        ```python
        # Flujo completo copiar/pegar
        datos = "información a pegar"
        self.copiar_al_portapapeles(datos)
        time.sleep(1)  # Esperar que se copie
        self.pegar_portapapeles_en_ventana_activa()
        ```
        >>> True  # Si el pegado es exitoso
        
        ---
        ### Raises
        #### ImportError
        - Si pyautogui no está disponible
        #### Exception  
        - Si ocurre error durante el pegado
        #### GUINotAvailableError
        - Si GUI no está activa (manejado por decorador)
        """
        try:
            import pyautogui
            
            pyautogui.hotkey('ctrl', 'v')
            self.mostrar("📋 Contenido pegado desde portapapeles")
            return True
            
        except ImportError:
            self.mostrar("❌ No se pudo importar pyautogui para pegar", True)
            return False
        except Exception as e:
            self.mostrar(f"❌ Error pegando desde portapapeles: {str(e)}", True)
            return False

    def verificar_estado_gui(self) -> dict:
        """
        Obtiene información detallada del estado actual de GUI.
        
        Retorna diccionario con información completa sobre el estado de la GUI,
        procesos activos, servicios y configuración de sesión para diagnóstico.
        
        ---
        Se utiliza dentro de diagnóstico y debugging cuando hay problemas con GUI.
        Método útil para generar reportes de estado del sistema.
        
        ---
        ### Ejemplo
        ```python
        estado = self.verificar_estado_gui()
        self.mostrar(f"GUI activa: {estado['gui_activa']}")
        self.mostrar(f"Procesos detectados: {estado['procesos_gui']}")
        ```
        >>> {"gui_activa": True, "procesos_gui": ["explorer.exe", "dwm.exe"], ...}
        
        ---
        ### Raises
        #### Exception
        - Si ocurre error accediendo información del sistema
        """
        try:
            self.mostrar("🔍 Analizando estado completo de GUI...")
            
            # Verificar procesos GUI
            procesos_gui = []
            procesos_criticos = ['explorer.exe', 'dwm.exe', 'winlogon.exe']
            procesos_activos = {p.name().lower() for p in psutil.process_iter(['name'])}
            
            for proceso in procesos_criticos:
                if proceso.lower() in procesos_activos:
                    procesos_gui.append(proceso)
            
            # Verificar servicios críticos
            servicios_estado = {}
            servicios_criticos = ['UxSms', 'Themes', 'AudioSrv']
            
            for servicio in servicios_criticos:
                try:
                    resultado = subprocess.run(
                        ['sc', 'query', servicio], 
                        capture_output=True, text=True
                    )
                    servicios_estado[servicio] = 'RUNNING' if 'RUNNING' in resultado.stdout else 'STOPPED'
                except:
                    servicios_estado[servicio] = 'UNKNOWN'
            
            # Verificar display
            display_disponible = False
            try:
                resultado_display = subprocess.run(
                    ['powershell', '-Command', 'Get-WmiObject -Class Win32_VideoController | Select-Object Name'],
                    capture_output=True, text=True, timeout=5
                )
                display_disponible = "Name" in resultado_display.stdout
            except:
                display_disponible = False
            
            # Forzar nueva verificación
            self._ultimo_check_gui = None
            gui_activa = self._verificar_sesion_gui_activa()
            
            estado = {
                'gui_activa': gui_activa,
                'procesos_gui': procesos_gui,
                'servicios_estado': servicios_estado,
                'display_disponible': display_disponible,
                'ultimo_check': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'intentos_recuperacion': self._intentos_recuperacion_gui
            }
            
            # Mostrar resumen
            self.mostrar("📊 Estado GUI completo:")
            self.mostrar(f"   • GUI Activa: {'✅' if gui_activa else '❌'} {gui_activa}")
            self.mostrar(f"   • Procesos GUI: {', '.join(procesos_gui) if procesos_gui else 'Ninguno'}")
            self.mostrar(f"   • Display: {'✅' if display_disponible else '❌'} {display_disponible}")
            self.mostrar(f"   • Servicios activos: {sum(1 for s in servicios_estado.values() if s == 'RUNNING')}/{len(servicios_criticos)}")
            
            return estado
            
        except Exception as e:
            self.mostrar(f"❌ Error verificando estado GUI: {str(e)}", True)
            return {
                'gui_activa': False,
                'error': str(e),
                'ultimo_check': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }