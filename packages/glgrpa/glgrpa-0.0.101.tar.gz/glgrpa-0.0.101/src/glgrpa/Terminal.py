import sys
import time
from datetime import datetime, timedelta
from colorama import Fore, init, Style
from pathlib import Path
import inspect
from .Pyinstaller import obtener_ruta_recurso

class Terminal:
    # Variables de clase para el singleton del log
    _ruta_archivo_log = None
    _log_activo = False
    _carpeta_raiz = ""
    _ejecucion_iniciada = False

    def __init__(self, dev:bool=False):
        """
        Inicializa la clase Terminal, configura el modo desarrollador y el inicio de ejecución.
        
        :param dev: Si es True, activa el modo desarrollador (esperas más cortas).
        """
        self.dev = dev
        init()
        # Si no se setea carpeta_raiz, buscarla automáticamente
        if not Terminal._carpeta_raiz:
            Terminal._carpeta_raiz = self._buscar_carpeta_src()
        # Solo inicializa el log si aún no está inicializado
        if not Terminal._log_activo:
            Terminal._log_activo = self.__iniciar_log()
        self.log_activo = Terminal._log_activo
        if Terminal._log_activo:
            if not Terminal._ejecucion_iniciada:
                self.mostrar("Iniciando ejecución")
                Terminal._ejecucion_iniciada = True
            self.inicio_ejecucion()
        
    def _buscar_carpeta_src(self) -> str:
        # Busca la carpeta 'src' hacia arriba desde el archivo que crea la instancia
        frame = inspect.currentframe()
        while frame:
            filename = frame.f_globals.get('__file__', None)
            if filename:
                path = Path(filename).resolve()
                for parent in [path] + list(path.parents):
                    if parent.name == "src":
                        # Crear logs en el mismo nivel que src, no dentro de src
                        logs_dir = parent.parent / "logs"
                        logs_dir.mkdir(exist_ok=True)
                        return str(logs_dir)
                frame = frame.f_back
        # Si no encuentra 'src', usar la función obtener_ruta_recurso para obtener la ruta del ejecutable
        logs_dir = Path(obtener_ruta_recurso("logs"))
        logs_dir.mkdir(exist_ok=True)
        return str(logs_dir)

    def set_carpeta_raiz(self, carpeta_raiz:str) -> None:
        """
        Establece la carpeta raíz para el log.
        
        :param carpeta_raiz: Ruta de la carpeta raíz donde se guardará el log.
        """
        Terminal._carpeta_raiz = carpeta_raiz

    def get_carpeta_raiz(self) -> str:
        """
        Obtiene la carpeta raíz donde se guardará el log.
        
        :return: Ruta de la carpeta raíz.
        :rtype: str
        """
        return Terminal._carpeta_raiz

    def obtener_hora_actual(self, format:str) -> str: 
        """ 
        Obtiene la hora actual en el formato especificado.
        
        :param format: Formato de fecha y hora, por ejemplo "%Y-%m-%d %H:%M:%S".
        :return: Hora actual formateada como cadena.
        :rtype: str
        """
        fecha = datetime.now()
        return fecha.strftime(format)

    def mostrar(self, mensaje:str, isError: bool=False) -> None:
        """
        Muestra un mensaje en consola con color y lo guarda en el log.
        
        :param mensaje: Mensaje a mostrar.
        :param isError: Si es True, muestra el mensaje en rojo (error).
        """
        color_fecha = Fore.GREEN if not isError else Fore.RED
        print(color_fecha + f"[{self.obtener_hora_actual(r"%Y-%m-%d %H:%M:%S")}]" + Style.RESET_ALL + f"\t{mensaje}")
        self.__guardar_en_log(mensaje)
        
    def inicio_ejecucion(self) -> None:
        """
        Marca el inicio de la ejecución, inicia el log y muestra mensaje de inicio.
        """
        self.tiempo_inicio = self.obtener_hora_actual(r"%Y-%m-%d %H:%M:%S")
        # No reiniciar el log si ya está activo
        if not Terminal._log_activo:
            Terminal._log_activo = self.__iniciar_log()
        self.log_activo = Terminal._log_activo
        
    def fin_ejecucion(self) -> None:
        """
        Marca el fin de la ejecución y muestra mensaje de finalización.
        """
        self.tiempo_fin = self.obtener_hora_actual(r"%Y-%m-%d %H:%M:%S")
        self.mostrar("Ejecución finalizada")
        
    def demora(self, tiempoEspera:int=5) -> None:
        """
        Realiza una pausa en la ejecución.
        
        :param tiempoEspera: Tiempo de espera en segundos (por defecto 5, o 1 si está en modo dev).
        """
        if self.dev: tiempoEspera = 1
        time.sleep(tiempoEspera)
        
    def obtener_duracion_ejecucion(self) -> str:
        """
        Calcula la duración total de la ejecución.
        
        :return: Duración de la ejecución como cadena.
        :raises ValueError: Si la ejecución no ha sido iniciada correctamente.
        """
        if not hasattr(self, 'tiempo_inicio'):
            raise ValueError("La ejecución no ha sido iniciada correctamente.")
        
        if not hasattr(self, 'tiempo_fin'):
            self.tiempo_fin = self.obtener_hora_actual(r"%Y-%m-%d %H:%M:%S")
            
        self.duracion_ejecucion = datetime.strptime(self.tiempo_fin, r"%Y-%m-%d %H:%M:%S") - datetime.strptime(self.tiempo_inicio, r"%Y-%m-%d %H:%M:%S")
        
        return str(self.duracion_ejecucion)
    
    def __iniciar_log(self) -> bool:
        """
        Inicializa el archivo de log en la carpeta 'logs', creando la carpeta si no existe.
        """
        try:
            # Crear carpeta 'logs' en el mismo nivel que el ejecutable
            if hasattr(sys, '_MEIPASS'):
                base_path = Path(sys.executable).parent
            else:
                base_path = Path(__file__).parent.parent

            logs_dir = base_path / "logs"
            logs_dir.mkdir(exist_ok=True)

            fecha_actual = self.obtener_hora_actual(r"%Y%m%d")
            numero_log_diario = len(list(logs_dir.glob(f"{fecha_actual}*.txt"))) + 1
            Terminal._ruta_archivo_log = logs_dir / f"{fecha_actual}_{numero_log_diario}.txt"
            print(f"Ruta del log: {Terminal._ruta_archivo_log}")
            Terminal._ruta_archivo_log.touch(exist_ok=True)
            return True if Terminal._ruta_archivo_log.exists() else False
        
        except Exception as e:
            print(f"Error al iniciar el log: {e}")
            return False
        
    def __guardar_en_log(self, mensaje:str, reintentos:int = 0) -> None:
        """
        Guarda un mensaje en el archivo de log. Reintenta hasta 3 veces en caso de error.
        
        :param mensaje: Mensaje a guardar.
        :param reintentos: Número de intentos realizados (para control interno).
        """
        if not Terminal._log_activo:
            print("El archivo log no está activo, no se guardará el mensaje")
            return         
        
        if reintentos > 3:
            print("Error al guardar en el log después de varios intentos")
            return
        
        try:
            if Terminal._ruta_archivo_log is not None:
                with open(str(Terminal._ruta_archivo_log), 'a', encoding='utf-8') as log_file:
                    log_file.write(f"[{self.obtener_hora_actual(r'%Y-%m-%d %H:%M:%S')}] {mensaje}\n")
            else:
                print("La ruta del archivo log no está definida.")
        except Exception as e:
            print(f"Error al guardar en el log: {e}")
            self.__guardar_en_log(mensaje, reintentos + 1)
