# src/glgrpa/ControlEjecucion.py

import json
import os
import inspect
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from functools import wraps
from .Windows import Windows
from .Terminal import Terminal
from .Email import Email

class ControlEjecucion(Windows, Terminal):
    """
    Clase para el control de estado y reintentos de ejecución siguiendo el patrón
    de herencia múltiple de glgrpa. Proporciona funcionalidad para:
    - Gestión de estado de ejecución con archivo JSON
    - Control de reintentos automáticos
    - Notificaciones por email en caso de éxito/fallo
    - Logging detallado con emojis siguiendo las convenciones del proyecto
    """
    
    # Cache de configuración para evitar múltiples instanciaciones
    _configuracion_cache: Optional[Dict[str, Any]] = None
    _instancia_principal: Optional['ControlEjecucion'] = None
    
    def __init__(self, 
                 intentos_maximos: int = 3,
                 permitir_multiples_ejecuciones_diarias: bool = False,
                 dev: bool = False,
                 email_destinatarios: Optional[list] = None,
                 nombre_script: Optional[str] = None,
                 # Parámetros SMTP para Email
                 smtp_server: Optional[str] = None,
                 smtp_port: Optional[int] = None,
                 smtp_username: Optional[str] = None,
                 smtp_password: Optional[str] = None,
                 nombre_trabajador_virtual: Optional[str] = None,
                 nombre_aprendizaje: Optional[str] = None,
                 # Nuevo parámetro para reutilizar configuración
                 reutilizar_configuracion: bool = True,
                 # Callbacks personalizados para mensajes de email
                 callback_mensaje_exito: Optional[Callable] = None,
                 callback_mensaje_error: Optional[Callable] = None):
        """
        Inicializa el control de ejecución.
        
        :param intentos_maximos: Número máximo de reintentos por ejecución (default: 3)
        :param permitir_multiples_ejecuciones_diarias: Si permite múltiples ejecuciones por día
        :param dev: Modo desarrollo (delays más cortos, logging verboso)
        :param email_destinatarios: Lista de emails para notificaciones
        :param nombre_script: Nombre del script para logs y emails (se detecta automáticamente si no se especifica)
        :param smtp_server: Servidor SMTP para envío de emails
        :param smtp_port: Puerto SMTP
        :param smtp_username: Usuario SMTP
        :param smtp_password: Contraseña SMTP
        :param nombre_trabajador_virtual: Nombre del trabajador virtual para emails
        :param nombre_aprendizaje: Nombre del aprendizaje para emails
        :param reutilizar_configuracion: Si debe reutilizar configuración de instancia anterior (default: True)
        :param callback_mensaje_exito: Función callback que genera mensaje personalizado de éxito (recibe resultado de función principal)
        :param callback_mensaje_error: Función callback que genera mensaje personalizado de error (recibe excepción)
        """
        super().__init__(dev=dev)
        
        # Intentar reutilizar configuración si está disponible y se solicita
        if reutilizar_configuracion and ControlEjecucion._configuracion_cache:
            self._cargar_configuracion_cache()
        else:
            # Configuración nueva - guardar parámetros proporcionados
            self._guardar_configuracion_parametros(
                intentos_maximos, permitir_multiples_ejecuciones_diarias,
                email_destinatarios, nombre_script, smtp_server, smtp_port,
                smtp_username, smtp_password, nombre_trabajador_virtual, nombre_aprendizaje
            )
        
        # Guardar callbacks personalizados
        self.callback_mensaje_exito = callback_mensaje_exito
        self.callback_mensaje_error = callback_mensaje_error
        
        # Detectar nombre del script automáticamente si no se especifica
        if self.nombre_script is None:
            try:
                frame = inspect.currentframe()
                if frame and frame.f_back:
                    caller_frame = frame.f_back  
                    caller_filename = caller_frame.f_globals.get('__file__', 'script_desconocido')
                    self.nombre_script = Path(caller_filename).stem
                else:
                    self.nombre_script = 'script_desconocido'
            except Exception:
                self.nombre_script = 'script_desconocido'
            
        # Ruta del archivo de estado usando resolución correcta para tareas programadas
        self.archivo_estado = self.resolver_ruta_archivo("estado_ejecucion.json", usar_directorio_script=True)
        
        # Configurar email handler
        self._configurar_email_handler()
        
        # Guardar como instancia principal si es la primera
        if ControlEjecucion._instancia_principal is None:
            ControlEjecucion._instancia_principal = self

    def _guardar_configuracion_parametros(self, intentos_maximos, permitir_multiples_ejecuciones_diarias,
                                         email_destinatarios, nombre_script, smtp_server, smtp_port,
                                         smtp_username, smtp_password, nombre_trabajador_virtual, nombre_aprendizaje):
        """Guarda la configuración de parámetros en atributos de instancia y cache global."""
        self.intentos_maximos = intentos_maximos
        self.permitir_multiples_ejecuciones_diarias = permitir_multiples_ejecuciones_diarias
        self.email_destinatarios = email_destinatarios or []
        self.nombre_script = nombre_script
        
        # Guardar configuración en cache global para reutilización
        ControlEjecucion._configuracion_cache = {
            'intentos_maximos': intentos_maximos,
            'permitir_multiples_ejecuciones_diarias': permitir_multiples_ejecuciones_diarias,
            'email_destinatarios': email_destinatarios or [],
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'smtp_username': smtp_username,
            'smtp_password': smtp_password,
            'nombre_trabajador_virtual': nombre_trabajador_virtual,
            'nombre_aprendizaje': nombre_aprendizaje
        }

    def _cargar_configuracion_cache(self):
        """Carga la configuración desde el cache global."""
        if ControlEjecucion._configuracion_cache:
            cache = ControlEjecucion._configuracion_cache
            self.intentos_maximos = cache.get('intentos_maximos', 3)
            self.permitir_multiples_ejecuciones_diarias = cache.get('permitir_multiples_ejecuciones_diarias', False)
            self.email_destinatarios = cache.get('email_destinatarios', [])
            self.nombre_script = cache.get('nombre_script')
            self.mostrar("🔄 Reutilizando configuración de instancia anterior")
        else:
            # Valores por defecto si no hay cache
            self.intentos_maximos = 3
            self.permitir_multiples_ejecuciones_diarias = False
            self.email_destinatarios = []
            self.nombre_script = None

    def _configurar_email_handler(self):
        """Configura el handler de email usando la configuración actual."""
        self.email_handler = None
        
        if self.email_destinatarios:
            self.mostrar(f"🔍 Configurando emails para: {', '.join(self.email_destinatarios)}")
            
            # Obtener configuración SMTP del cache si está disponible
            cache = ControlEjecucion._configuracion_cache or {}
            smtp_server = cache.get('smtp_server')
            smtp_port = cache.get('smtp_port')
            smtp_username = cache.get('smtp_username')
            smtp_password = cache.get('smtp_password')
            nombre_trabajador_virtual = cache.get('nombre_trabajador_virtual')
            nombre_aprendizaje = cache.get('nombre_aprendizaje')
            
            if smtp_server and smtp_port and smtp_username and smtp_password:
                self.mostrar(f"🔍 Parámetros SMTP: servidor={smtp_server}, puerto={smtp_port}, usuario={smtp_username}")
                try:
                    self.email_handler = Email(
                        smtp_server=smtp_server,
                        smtp_port=smtp_port,
                        smtp_username=smtp_username,
                        smtp_password=smtp_password,
                        nombre_trabajador_virtual=nombre_trabajador_virtual or self.nombre_script or 'trabajador_virtual',
                        nombre_aprendizaje=nombre_aprendizaje or self.nombre_script or 'aprendizaje',
                        dev=self.dev
                    )
                    self.mostrar("📧 Sistema de notificaciones por email configurado")
                except Exception as e:
                    self.mostrar(f"❌ No se pudo configurar el sistema de email: {str(e)}", True)
                    self.email_handler = None
            else:
                missing_params = []
                if not smtp_server: missing_params.append("smtp_server")
                if not smtp_port: missing_params.append("smtp_port") 
                if not smtp_username: missing_params.append("smtp_username")
                if not smtp_password: missing_params.append("smtp_password")
                self.mostrar(f"⚠️  Emails configurados pero faltan parámetros SMTP: {', '.join(missing_params)}. Notificaciones deshabilitadas.", True)
        else:
            self.mostrar("🔍 No hay destinatarios de email configurados - notificaciones deshabilitadas")

    @staticmethod
    def resolver_ruta_variables_entorno(nombre_archivo_env: str = '.env.production') -> str:
        """
        Resuelve correctamente la ruta del archivo de variables de entorno.
        
        Método estático específico para resolver rutas de archivos .env cuando se ejecuta
        desde tareas programadas de Windows. Evita el problema de duplicación de rutas
        que ocurre cuando el directorio de trabajo actual no es el directorio del ejecutable.
        
        ### Ejemplo
        ```python
        from glgrpa import ControlEjecucion
        
        # Resolver ruta del archivo .env.production
        ruta_env = ControlEjecucion.resolver_ruta_variables_entorno()
        
        # Verificar si existe antes de cargar
        if os.path.exists(ruta_env):
            from dotenv import load_dotenv
            load_dotenv(ruta_env)
            print(f"✅ Variables cargadas desde: {ruta_env}")
        else:
            print(f"❌ No se encontró archivo: {ruta_env}")
        
        # Para otros archivos .env
        ruta_env_dev = ControlEjecucion.resolver_ruta_variables_entorno('.env.development')
        ```
        >>> "C:\\path\\to\\executable\\.env.production"  # Ruta resuelta correctamente
        
        :param nombre_archivo_env: Nombre del archivo de variables de entorno (default: '.env.production')
        :return: Ruta absoluta resuelta del archivo de variables de entorno
        
        ### Raises
        #### Exception
        - Si no se puede determinar la ruta del ejecutable actual
        """
        return Windows.resolver_ruta_archivo(nombre_archivo_env, usar_directorio_script=True)

    def leer_estado_ejecucion(self) -> Dict[str, Any]:
        """
        Lee el estado de ejecución desde el archivo JSON.
        
        :return: Diccionario con el estado de ejecución
        """
        estado_default = {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "exitoso": False,
            "intentos_diarios": 0,
            "intentos_maximos": self.intentos_maximos,
            "intentos_realizados": 0,
            "ultimo_error": None,
            "timestamp": datetime.now().isoformat(),
            "nombre_script": self.nombre_script
        }
        
        try:
            if os.path.exists(self.archivo_estado):
                with open(self.archivo_estado, 'r', encoding='utf-8') as f:
                    estado = json.load(f)
                    self.mostrar(f"📄 Estado de ejecución leído: {estado['fecha']} - Intentos: {estado['intentos_realizados']}/{estado['intentos_maximos']}")
                    return estado
            else:
                self.mostrar("📄 No existe archivo de estado previo, creando nuevo estado")
                return estado_default
        except Exception as e:
            self.mostrar(f"❌ Error al leer estado de ejecución: {str(e)}", True)
            return estado_default

    def guardar_estado_ejecucion(self, estado: Dict[str, Any]) -> bool:
        """
        Guarda el estado de ejecución en el archivo JSON.
        
        :param estado: Diccionario con el estado a guardar
        :return: True si se guardó correctamente, False en caso contrario
        """
        try:
            estado["timestamp"] = datetime.now().isoformat()
            with open(self.archivo_estado, 'w', encoding='utf-8') as f:
                json.dump(estado, f, indent=2, ensure_ascii=False)
            self.mostrar(f"💾 Estado guardado: exitoso={estado['exitoso']}, intentos={estado['intentos_realizados']}")
            return True
        except Exception as e:
            self.mostrar(f"❌ Error al guardar estado: {str(e)}", True)
            return False

    def validar_puede_ejecutar(self, estado: Dict[str, Any]) -> tuple[bool, str]:
        """
        Valida si el script puede ejecutarse basado en el estado actual.
        
        :param estado: Estado actual de ejecución
        :return: Tupla (puede_ejecutar, razon)
        """
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        # Si es un día diferente, resetear contadores
        if estado["fecha"] != fecha_actual:
            self.mostrar(f"📅 Nueva fecha detectada: {fecha_actual}, reseteando contadores")
            estado.update({
                "fecha": fecha_actual,
                "intentos_diarios": 0,
                "intentos_realizados": 0,
                "exitoso": False,
                "ultimo_error": None
            })
            return True, "Nueva fecha - ejecución permitida"
        
        # Si ya fue exitoso hoy y no permite múltiples ejecuciones
        if estado["exitoso"] and not self.permitir_multiples_ejecuciones_diarias:
            return False, f"Script ya ejecutado exitosamente hoy ({estado['fecha']})"
        
        # Si se alcanzó el límite de intentos diarios
        if estado["intentos_realizados"] >= self.intentos_maximos:
            return False, f"Límite de intentos diarios alcanzado ({estado['intentos_realizados']}/{self.intentos_maximos})"
        
        return True, "Ejecución permitida"

    def enviar_notificacion_email(self, exitoso: bool, error_msg: Optional[str] = None, 
                                intentos_realizados: int = 0, resultado_funcion: Optional[Any] = None) -> bool:
        """
        Envía notificación por email del resultado de la ejecución usando los métodos
        estandarizados de la clase Email (enviar_email_exito/enviar_email_error).
        
        :param exitoso: Si la ejecución fue exitosa
        :param error_msg: Mensaje de error si aplicable
        :param intentos_realizados: Número de intentos realizados
        :param resultado_funcion: Resultado de la función principal (para callbacks personalizados)
        :return: True si se envió correctamente
        """
        # Logging detallado para debugging
        self.mostrar(f"🔍 Intentando enviar email: exitoso={exitoso}, email_handler={'✅' if self.email_handler else '❌'}, destinatarios={'✅' if self.email_destinatarios else '❌'}")
        
        if not self.email_handler:
            self.mostrar("⚠️  Email handler no configurado - no se enviará notificación")
            return False
            
        if not self.email_destinatarios:
            self.mostrar("⚠️  No hay destinatarios configurados - no se enviará notificación")
            return False
            
        try:
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            
            if exitoso:
                self.mostrar(f"📧 Enviando email de éxito a: {', '.join(self.email_destinatarios)}")
                
                # Usar callback personalizado si está disponible
                if self.callback_mensaje_exito:
                    try:
                        mensaje_personalizado = self.callback_mensaje_exito(resultado_funcion)
                        self.mostrar("🎯 Usando mensaje personalizado para email de éxito")
                        
                        # Usar método estandarizado con mensaje personalizado
                        resultado = self.email_handler.enviar_email_exito(
                            destinatarios=self.email_destinatarios,
                            titulo=mensaje_personalizado.get('titulo', f"Ejecución Exitosa - {self.nombre_script}"),
                            subtitulo=mensaje_personalizado.get('subtitulo', "El script de automatización se ejecutó correctamente"),
                            mensaje=mensaje_personalizado.get('mensaje', f"Script: {self.nombre_script}\nIntentos realizados: {intentos_realizados}/{self.intentos_maximos}\nEstado: Completado correctamente\nFecha: {fecha_actual}"),
                            fecha=fecha_actual,
                            duracion="00:00:00"  # Puede implementarse cálculo de duración si se necesita
                        )
                    except Exception as callback_error:
                        self.mostrar(f"⚠️  Error en callback personalizado de éxito: {str(callback_error)}, usando mensaje estándar")
                        # Fallback al mensaje estándar
                        resultado = self.email_handler.enviar_email_exito(
                            destinatarios=self.email_destinatarios,
                            titulo=f"Ejecución Exitosa - {self.nombre_script}",
                            subtitulo="El script de automatización se ejecutó correctamente",
                            mensaje=f"Script: {self.nombre_script}\nIntentos realizados: {intentos_realizados}/{self.intentos_maximos}\nEstado: Completado correctamente\nFecha: {fecha_actual}",
                            fecha=fecha_actual,
                            duracion="00:00:00"
                        )
                else:
                    # Usar método estandarizado para emails de éxito
                    resultado = self.email_handler.enviar_email_exito(
                        destinatarios=self.email_destinatarios,
                        titulo=f"Ejecución Exitosa - {self.nombre_script}",
                        subtitulo="El script de automatización se ejecutó correctamente",
                        mensaje=f"Script: {self.nombre_script}\nIntentos realizados: {intentos_realizados}/{self.intentos_maximos}\nEstado: Completado correctamente\nFecha: {fecha_actual}",
                        fecha=fecha_actual,
                        duracion="00:00:00"  # Puede implementarse cálculo de duración si se necesita
                    )
            else:
                self.mostrar(f"📧 Enviando email de error a: {', '.join(self.email_destinatarios)}")
                
                # Usar callback personalizado si está disponible
                if self.callback_mensaje_error:
                    try:
                        # El callback de error recibe la excepción original si está disponible
                        excepcion_original = Exception(error_msg) if error_msg else None
                        mensaje_personalizado = self.callback_mensaje_error(excepcion_original)
                        self.mostrar("🎯 Usando mensaje personalizado para email de error")
                        
                        # Usar método estandarizado con mensaje personalizado
                        resultado = self.email_handler.enviar_email_error(
                            destinatarios=self.email_destinatarios,
                            titulo=mensaje_personalizado.get('titulo', f"❌ Ejecución Fallida - {self.nombre_script}"),
                            subtitulo=mensaje_personalizado.get('subtitulo', f"El script falló tras {intentos_realizados} intentos"),
                            mensaje=mensaje_personalizado.get('mensaje', f"Script: {self.nombre_script}\nIntentos realizados: {intentos_realizados}/{self.intentos_maximos}\nÚltimo error: {error_msg or 'Error no especificado'}\nEstado: Límite de reintentos alcanzado\nFecha: {fecha_actual}"),
                            fecha=fecha_actual,
                            duracion="00:00:00"
                        )
                    except Exception as callback_error:
                        self.mostrar(f"⚠️  Error en callback personalizado de error: {str(callback_error)}, usando mensaje estándar")
                        # Fallback al mensaje estándar
                        resultado = self.email_handler.enviar_email_error(
                            destinatarios=self.email_destinatarios,
                            titulo=f"❌ Ejecución Fallida - {self.nombre_script}",
                            subtitulo=f"El script falló tras {intentos_realizados} intentos",
                            mensaje=f"Script: {self.nombre_script}\nIntentos realizados: {intentos_realizados}/{self.intentos_maximos}\nÚltimo error: {error_msg or 'Error no especificado'}\nEstado: Límite de reintentos alcanzado\nFecha: {fecha_actual}",
                            fecha=fecha_actual,
                            duracion="00:00:00"
                        )
                else:
                    # Usar método estandarizado para emails de error
                    resultado = self.email_handler.enviar_email_error(
                        destinatarios=self.email_destinatarios,
                        titulo=f"❌ Ejecución Fallida - {self.nombre_script}",
                        subtitulo=f"El script falló tras {intentos_realizados} intentos",
                        mensaje=f"Script: {self.nombre_script}\nIntentos realizados: {intentos_realizados}/{self.intentos_maximos}\nÚltimo error: {error_msg or 'Error no especificado'}\nEstado: Límite de reintentos alcanzado\nFecha: {fecha_actual}",
                        fecha=fecha_actual,
                        duracion="00:00:00"
                    )
            
            if resultado:
                self.mostrar(f"📧 Email de notificación enviado exitosamente: {'✅ Éxito' if exitoso else '❌ Fallo'}")
            else:
                self.mostrar(f"❌ Falló el envío del email de notificación: {'✅ Éxito' if exitoso else '❌ Fallo'}")
                
            return resultado
            
        except Exception as e:
            self.mostrar(f"❌ Error al enviar email de notificación: {str(e)}", True)
            return False

    def ejecutar_con_control_estado(self, funcion_principal: Callable, *args, **kwargs) -> bool:
        """
        Ejecuta una función con control de estado. Cada ejecución es independiente
        y controlada por tareas programadas de Windows (ej: 7:00, 7:30, 8:00).
        
        :param funcion_principal: Función a ejecutar
        :param args: Argumentos posicionales para la función
        :param kwargs: Argumentos con nombre para la función
        :return: True si la ejecución fue exitosa
        """
        self.mostrar(f"🚀 Iniciando control de ejecución para: {self.nombre_script}")
        
        # Leer estado actual
        estado = self.leer_estado_ejecucion()
        
        # Validar si puede ejecutar
        puede_ejecutar, razon = self.validar_puede_ejecutar(estado)
        if not puede_ejecutar:
            self.mostrar(f"🚫 Ejecución bloqueada: {razon}")
            return False
        
        self.mostrar(f"✅ Validación passed: {razon}")
        
        # Incrementar contador de intentos
        intento_actual = estado["intentos_realizados"] + 1
        self.mostrar(f"🔄 Ejecución {intento_actual}/{self.intentos_maximos}")
        
        try:
            # Actualizar estado antes del intento
            estado["intentos_realizados"] = intento_actual
            estado["intentos_diarios"] = intento_actual
            self.guardar_estado_ejecucion(estado)
            
            # Ejecutar función principal
            resultado = funcion_principal(*args, **kwargs)
            
            if resultado:
                # Ejecución exitosa
                estado["exitoso"] = True
                estado["ultimo_error"] = None
                self.guardar_estado_ejecucion(estado)
                
                self.mostrar(f"✅ Ejecución exitosa en intento {intento_actual}")
                
                # Enviar email de éxito pasando el resultado para callbacks personalizados
                self.enviar_notificacion_email(
                    exitoso=True, 
                    intentos_realizados=intento_actual,
                    resultado_funcion=resultado
                )
                
                return True
            else:
                # Función retornó False
                error_msg = f"Función principal retornó False en intento {intento_actual}"
                estado["ultimo_error"] = error_msg
                self.mostrar(f"⚠️  {error_msg}")
                
                # Guardar estado del fallo
                self.guardar_estado_ejecucion(estado)
                
                # Si alcanzó el máximo de intentos, enviar email de fallo final
                if intento_actual >= self.intentos_maximos:
                    self.mostrar(f"❌ Límite de intentos alcanzado ({intento_actual}/{self.intentos_maximos})")
                    self.enviar_notificacion_email(
                        exitoso=False,
                        error_msg=error_msg,
                        intentos_realizados=intento_actual
                    )
                else:
                    self.mostrar(f"⏳ Esperando próxima ejecución programada. Intentos restantes: {self.intentos_maximos - intento_actual}")
                
                return False
                
        except Exception as e:
            # Error durante la ejecución
            error_msg = f"Error en intento {intento_actual}: {str(e)}"
            estado["ultimo_error"] = error_msg
            self.mostrar(f"❌ {error_msg}", True)
            
            # Tomar screenshot para debugging si está disponible
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_nombre = f"error_{self.nombre_script}_intento_{intento_actual}_{timestamp}"
                self.tomar_screenshot(screenshot_nombre)
                self.mostrar(f"📸 Screenshot guardado: {screenshot_nombre}.png")
            except Exception as screenshot_error:
                self.mostrar(f"⚠️  No se pudo tomar screenshot: {str(screenshot_error)}")
            
            # Guardar estado después del error
            self.guardar_estado_ejecucion(estado)
            
            # Si alcanzó el máximo de intentos, enviar email de fallo final
            if intento_actual >= self.intentos_maximos:
                self.mostrar(f"❌ Límite de intentos alcanzado ({intento_actual}/{self.intentos_maximos})")
                self.enviar_notificacion_email(
                    exitoso=False,
                    error_msg=error_msg,
                    intentos_realizados=intento_actual
                )
            else:
                self.mostrar(f"⏳ Esperando próxima ejecución programada. Intentos restantes: {self.intentos_maximos - intento_actual}")
            
            return False

    def decorador_ejecucion_controlada_instancia(self, 
                                     intentos_maximos: Optional[int] = None,
                                     permitir_multiples_ejecuciones_diarias: Optional[bool] = None,
                                     email_destinatarios: Optional[list] = None):
        """
        Decorador de instancia para aplicar control de ejecución a cualquier función.
        
        Nota: Para uso en scripts de producción, se recomienda usar el decorador estático
        ControlEjecucion.decorador_ejecucion_controlada() que incluye configuración completa.
        
        :param intentos_maximos: Override del número máximo de intentos
        :param permitir_multiples_ejecuciones_diarias: Override de múltiples ejecuciones diarias
        :param email_destinatarios: Override de destinatarios de email
        :return: Decorador
        """
        def decorador(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Usar valores override si se proporcionan, sino usar configuración actual
                _intentos_maximos = intentos_maximos or self.intentos_maximos
                _permitir_multiples = permitir_multiples_ejecuciones_diarias if permitir_multiples_ejecuciones_diarias is not None else self.permitir_multiples_ejecuciones_diarias
                _email_destinatarios = email_destinatarios or self.email_destinatarios
                
                # Reutilizar la instancia actual si tiene la misma configuración
                if (_intentos_maximos == self.intentos_maximos and 
                    _permitir_multiples == self.permitir_multiples_ejecuciones_diarias and
                    _email_destinatarios == self.email_destinatarios):
                    
                    self.mostrar("🔄 Reutilizando instancia actual de ControlEjecucion")
                    # Actualizar nombre del script para el contexto actual
                    nombre_script_anterior = self.nombre_script
                    self.nombre_script = func.__name__
                    
                    try:
                        return self.ejecutar_con_control_estado(func, *args, **kwargs)
                    finally:
                        # Restaurar nombre del script original
                        self.nombre_script = nombre_script_anterior
                else:
                    # Crear nueva instancia solo si la configuración es diferente
                    self.mostrar("🆕 Creando nueva instancia con configuración diferente")
                    control = ControlEjecucion(
                        intentos_maximos=_intentos_maximos,
                        permitir_multiples_ejecuciones_diarias=_permitir_multiples,
                        dev=self.dev,
                        email_destinatarios=_email_destinatarios,
                        nombre_script=func.__name__,
                        reutilizar_configuracion=True  # Reutilizar configuración SMTP
                    )
                    
                    return control.ejecutar_con_control_estado(func, *args, **kwargs)
                
            return wrapper
        return decorador

    @staticmethod
    def decorador_ejecucion_controlada(intentos_maximos: int = 3,
                                     permitir_multiples_ejecuciones_diarias: bool = False,
                                     email_destinatarios: Optional[list] = None,
                                     nombre_script: Optional[str] = None,
                                     smtp_server: Optional[str] = None,
                                     smtp_port: Optional[int] = None,
                                     smtp_username: Optional[str] = None,
                                     smtp_password: Optional[str] = None,
                                     nombre_trabajador_virtual: Optional[str] = None,
                                     nombre_aprendizaje: Optional[str] = None,
                                     dev: bool = False,
                                     callback_mensaje_exito: Optional[Callable] = None,
                                     callback_mensaje_error: Optional[Callable] = None):
        """
        Decorador estático para aplicar control de ejecución a cualquier función.
        
        Este es el decorador principal que se debe usar en scripts de producción.
        Permite configurar completamente el control de ejecución sin necesidad de 
        crear una instancia previa de ControlEjecucion.
        
        ### Ejemplo
        ```python
        from glgrpa import ControlEjecucion
        
        @ControlEjecucion.decorador_ejecucion_controlada(
            intentos_maximos=3,
            permitir_multiples_ejecuciones_diarias=False,
            email_destinatarios=['admin@empresa.com'],
            smtp_server='smtp.outlook.com',
            smtp_port=587,
            smtp_username='robot@empresa.com',
            smtp_password='password',
            nombre_trabajador_virtual='Robot SAP',
            nombre_aprendizaje='Cotizaciones BNA'
        )
        def mi_proceso_rpa():
            # Lógica de automatización
            return True  # Retornar True si exitoso, False si falló
        ```
        
        :param intentos_maximos: Número máximo de reintentos por día (default: 3)
        :param permitir_multiples_ejecuciones_diarias: Si permite múltiples ejecuciones exitosas por día
        :param email_destinatarios: Lista de emails para notificaciones
        :param nombre_script: Nombre del script para logs (se detecta automáticamente si no se especifica)
        :param smtp_server: Servidor SMTP para envío de emails
        :param smtp_port: Puerto SMTP
        :param smtp_username: Usuario SMTP
        :param smtp_password: Contraseña SMTP
        :param nombre_trabajador_virtual: Nombre del trabajador virtual para emails
        :param nombre_aprendizaje: Nombre del aprendizaje para emails
        :param dev: Modo desarrollo (timeouts más cortos, logging verboso)
        :param callback_mensaje_exito: Función callback que genera mensaje personalizado de éxito
        :param callback_mensaje_error: Función callback que genera mensaje personalizado de error
        :return: Función decorada con control de ejecución
        
        ### Raises
        #### ValueError
        - Si email_destinatarios está configurado pero faltan parámetros SMTP
        #### Exception
        - Si ocurre un error durante la configuración del control de ejecución
        """
        def decorador(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Validar configuración de email
                if email_destinatarios and not all([smtp_server, smtp_port, smtp_username, smtp_password]):
                    raise ValueError("Si se configuran email_destinatarios, también se deben proporcionar todos los parámetros SMTP")
                
                # Detectar nombre del script si no se especifica
                _nombre_script = nombre_script
                if _nombre_script is None:
                    _nombre_script = func.__name__
                
                # Crear instancia de ControlEjecucion con toda la configuración
                control = ControlEjecucion(
                    intentos_maximos=intentos_maximos,
                    permitir_multiples_ejecuciones_diarias=permitir_multiples_ejecuciones_diarias,
                    dev=dev,
                    email_destinatarios=email_destinatarios,
                    nombre_script=_nombre_script,
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    smtp_username=smtp_username,
                    smtp_password=smtp_password,
                    nombre_trabajador_virtual=nombre_trabajador_virtual,
                    nombre_aprendizaje=nombre_aprendizaje,
                    callback_mensaje_exito=callback_mensaje_exito,
                    callback_mensaje_error=callback_mensaje_error
                )
                
                # Ejecutar función con control de estado
                return control.ejecutar_con_control_estado(func, *args, **kwargs)
                
            return wrapper
        return decorador
