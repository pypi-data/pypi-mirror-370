import os
import urllib
import datetime
import office365

from urllib.parse import unquote
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from office365.sharepoint.folders.folder import Folder
from office365.runtime.paths.resource_path import ResourcePath
from datetime import datetime
from .Terminal import Terminal

class Sharepoint(Terminal):
    """ Clase para interactuar con SharePoint """
    
    def __init__(self, dev: bool = False):
        super().__init__(dev=dev)
        
    def set_usuario(self, usuario: str|dict, clave: str|None = None) -> None:
        """ 
        Establece el usuario y la contraseña para la autenticación.
        Si se pasa un diccionario, se espera que contenga las claves 'nombre' y 'clave'.
        
        :param usuario: Nombre de usuario o diccionario con 'nombre' y 'clave'
        :param clave: Contraseña del usuario
        
        :raises ValueError: Si el diccionario no contiene las claves necesarias
        :raises TypeError: Si el tipo de usuario no es válido
        """
        
        if isinstance(usuario, dict):
            for clave, val in usuario.items():
                if clave == 'nombre':
                    self.nombre_usuario = val
                elif clave == 'clave':
                    self.clave_usuario = val
                else:
                    raise ValueError(f"El diccionario no contiene la clave '{clave}' esperada.")
        elif isinstance(usuario, str):
            if clave is None or clave == '':
                raise ValueError("La clave no puede ser ``None`` o vacía.")
            
            self.nombre_usuario = usuario
            self.clave_usuario = clave
        else:
            raise TypeError("El tipo de usuario no es válido. Debe ser un diccionario o una cadena.")
        
    def set_cliente(self, cliente: str|dict, clave: str|None = None) -> None:
        """ 
        Establece el nombre de un cliente y la contraseña para la autenticación.
        Si se pasa un diccionario, se espera que contenga las claves 'nombre' y 'clave'.
        
        :param cliente: Nombre de cliente o diccionario con 'nombre' y 'clave'
        :param clave: Contraseña del cliente
        
        :raises ValueError: Si el diccionario no contiene las claves necesarias
        :raises TypeError: Si el tipo de cliente no es válido
        """
        if isinstance(cliente, dict):
            for clave, val in cliente.items():
                if clave == 'nombre':
                    self.nombre_cliente = val
                elif clave == 'clave':
                    self.clave_cliente = val
                else:
                    raise ValueError(f"El diccionario no contiene la clave '{clave}' esperada.")
        elif isinstance(cliente, str):
            if clave is None or clave == '':
                raise ValueError("La clave no puede ser ``None`` o vacía.")
            
            self.nombre_cliente = cliente
            self.clave_cliente = clave
        else:
            raise TypeError("El tipo de cliente no es válido. Debe ser un diccionario o una cadena.")
        
    def set_url(self, url: str) -> None:
        """
        Establece la URL base del sitio de SharePoint.
        
        :param url: URL del sitio de SharePoint con formato 'https://nombre.sharepoint.com/sites/nombre'
        
        :raises ValueError: Si la URL no es válida o no contiene 'sharepoint.com'
        """
        if 'sharepoint.com' not in url:
            raise ValueError("La URL no es válida. Debe ser con formato 'https://nombre.sharepoint.com/sites/nombre'.")
        self.url = url
        
    def set_contexto(self, contexto: ClientContext|None) -> ClientContext:
        """ Establece el contexto de SharePoint """
        if contexto is None:
            raise ValueError("El contexto no puede ser ``None``.")
        if not isinstance(contexto, ClientContext):
            raise TypeError("El contexto debe ser una instancia de ClientContext.")
        
        self._contexto = contexto  
        return self._contexto
    
    def get_usuario(self, clave: str|None = None) -> dict|str:
        """ 
        Si no se proporciona clave, devuelve un diccionario con 'nombre' y 'clave'.
        
        :param clave: Clave del usuario (opcional)
        :return: Diccionario con 'nombre' y 'clave' o el valor de la clave solicitada
        
        :raises ValueError: Si la clave no es válida
        """
        if clave is None:
            return {'nombre': self.nombre_usuario, 'clave': self.clave_usuario}
        else:
            if clave == 'nombre':
                return self.nombre_usuario
            elif clave == 'clave':
                return self.clave_usuario
            else:
                raise ValueError(f"La clave '{clave}' no es válida. Debe ser 'nombre' o 'clave'.")
            
    def get_cliente(self, clave: str|None = None) -> dict|str:
        """ 
        Si no se proporciona clave, devuelve un diccionario con 'nombre' y 'clave'.
        
        :param clave: Clave del cliente (opcional)
        :return: Diccionario con 'nombre' y 'clave' o el valor de la clave solicitada
        
        :raises ValueError: Si la clave no es válida
        """
        if clave is None:
            return {'nombre': self.nombre_cliente, 'clave': self.clave_cliente}
        else:
            if clave == 'nombre':
                return self.nombre_cliente
            elif clave == 'clave':
                return self.clave_cliente
            else:
                raise ValueError(f"La clave '{clave}' no es válida. Debe ser 'nombre' o 'clave'.")
            
    def get_url(self) -> str:
        """
        Devuelve la URL del sitio de SharePoint.
        
        :raises ValueError: Si la URL no está establecida
        """
        if self.url is None:
            self.mostrar(f"La URL no está establecida", True)
            raise ValueError("La URL no está establecida.")
        
        return self.url
    
    def get_url_base(self, url: str|None = None) -> str:
        """
        Devuelve la URL base del sitio de SharePoint.
        
        Si no se proporciona una URL, utiliza la URL establecida en la instancia.
        
        :param url: URL del sitio de SharePoint (opcional)
        :return: URL base del sitio de SharePoint
        
        :raises ValueError: Si la URL no está establecida
        """
        if url is None: url = self.url
        
        if url is None:
            self.mostrar(f"La URL no está establecida", True)
            raise ValueError("La URL no está establecida.")
        
        if 'sharepoint.com' not in url:
            raise ValueError("La URL no es válida. Debe ser con formato 'https://nombre.sharepoint.com/sites/nombre'.")
        
        return url.split('/sites')[0]
    
    def get_url_sitio(self, url: str|None = None) -> str:
        """
        Devuelve la URL del sitio de SharePoint desde /sites.
        
        Si no se proporciona una URL, utiliza la URL establecida en la instancia.
        
        :param url: URL del sitio de SharePoint (opcional)
        :return: URL del sitio de SharePoint desde /sites
        
        :raises ValueError: Si la URL no está establecida
        """
        if url is None: url = self.url
        
        if url is None:
            self.mostrar(f"La URL no está establecida", True)
            raise ValueError("La URL no está establecida.")
        
        if 'sharepoint.com' not in url:
            raise ValueError("La URL no es válida. Debe ser con formato 'https://nombre.sharepoint.com/sites/nombre'.")
        
        if url.startswith('https://'):
            url = url.split("sharepoint.com")[1]
            url = unquote(url)
            url = url.replace("\\", '/')         
        
        return f"/sites{url.split('/sites')[1]}"
    
    def get_contexto(self) -> ClientContext:
        """
        Devuelve el contexto de SharePoint.
        
        :raises ValueError: Si el contexto no está definido
        """
        if self._contexto is None:
            self.mostrar(f"El contexto no está definido", True)
            raise ValueError("El contexto no está definido.")
        
        return self._contexto
    
    def obtener_tipo_login(self) -> str:
        """ 
        Devuelve el tipo de autenticación según los datos proporcionados.
        """
        if hasattr(self, 'nombre_cliente') and self.nombre_cliente and hasattr(self, 'clave_cliente') and self.clave_cliente:
            return 'client_credentials'
        elif hasattr(self, 'nombre_usuario') and self.nombre_usuario and hasattr(self, 'clave_usuario') and self.clave_usuario:
            return 'user_credentials'
        else:
            self.mostrar(f"El tipo de autenticación no está definido", True)
            raise AttributeError("El tipo de autenticación no está definido")
    
    def obtener_carpeta(self, url: str) -> Folder|None:
        """
        Devuelve la carpeta de SharePoint a partir de la URL proporcionada.
        
        :param url: URL de la carpeta en SharePoint en formato absoluto('https://nombre.sharepoint.com/sites/nombre/carpeta') o relativo ('/sites/nombre/carpeta')
        :return: Carpeta de SharePoint o ``None`` si no existe
        
        :raises ValueError: Si la URL no está definida
        """
        if url is None:
            raise ValueError("La URL debe estar definida.")
        
        contexto = self.get_contexto()
        
        try:
            carpeta = Folder(contexto, ResourcePath(url))
            contexto.load(carpeta).execute_query()
            return carpeta
        except Exception as e:
            return self.__obtener_carpeta_desde_contexto(url)  
        
    def __obtener_carpeta_desde_contexto(self, url: str) -> Folder|None:
        """  
        Devuelve la carpeta de SharePoint a partir de la URL proporcionada.
        
        Si la URL es absoluta, se obtiene la relativa.
        
        :param url: URL de la carpeta en SharePoint en formato absoluto('https://nombre.sharepoint.com/sites/nombre/carpeta') o relativo ('/sites/nombre/carpeta')
        :return: Carpeta de SharePoint o ``None`` si no existe
        """        
        contexto = self.get_contexto()
        
        try:
            ruta_relativa = self.get_url_sitio(url)
            carpeta = contexto.web.get_folder_by_server_relative_url(ruta_relativa)
            contexto.load(carpeta).execute_query()
            
            if carpeta.properties["Exists"]: 
                return carpeta
            else:
                self.mostrar(f"La carpeta no existe: {url}", True)
                return None
        except Exception as e:
            self.mostrar(f"Error al obtener la carpeta: {e}", True)
            raise e

    def obtener_archivo(self, url: str|None) -> File|None:
        """
        Devuelve el archivo de SharePoint a partir de la URL proporcionada.
        
        :param url: URL del archivo en SharePoint en formato absoluto('https://nombre.sharepoint.com/sites/nombre/carpeta/archivo') o relativo ('/sites/nombre/carpeta/archivo')
        :return: Archivo de SharePoint o ``None`` si no existe
        
        :raises ValueError: Si la URL no está definida
        """
        if url is None:
            raise ValueError("La URL debe estar definida.")
        
        contexto = self.get_contexto()
        
        try:
            archivo = File(contexto, ResourcePath(url))
            contexto.load(archivo).execute_query()
            return archivo
        except Exception as e:
            return self.__obtener_archivo_desde_contexto(url)
        
    def __obtener_archivo_desde_contexto(self, url: str) -> File|None:
        """  
        Devuelve el archivo de SharePoint a partir de la URL proporcionada.
        
        Si la URL es absoluta, se obtiene la relativa.
        
        :param url: URL del archivo en SharePoint en formato absoluto('https://nombre.sharepoint.com/sites/nombre/carpeta/archivo') o relativo ('/sites/nombre/carpeta/archivo')
        :return: Archivo de SharePoint o ``None`` si no existe
        """        
        contexto = self.get_contexto()
        
        try:
            ruta_relativa = self.get_url_sitio(url)
            archivo = contexto.web.get_file_by_server_relative_url(ruta_relativa)
            contexto.load(archivo).execute_query()
            
            if archivo.properties["Exists"]: 
                return archivo
            else:
                self.mostrar(f"El archivo no existe: {url}", True)
                return None
        except Exception as e:
            self.mostrar(f"Error al obtener el archivo: {e}", True)
            raise e

    def crear_contexto(self, url: str|None = None, tipo_login: str|None = None) -> ClientContext:
        """
        Crea un contexto de cliente para interactuar con SharePoint.
        
        :param str or None url: URL del sitio de SharePoint
        :param str or None tipo_login: Tipo de autenticación
        :return: Contexto de cliente de SharePoint
        
        :raises ValueError: Si la URL no está establecida o el tipo de autenticación no es válido
        """
        
        if url is None:
            url = self.get_url()
            if url is None:
                self.mostrar(f"La URL no está establecida", True)
                raise ValueError("La URL no está establecida.")
        
        if tipo_login is None:
            tipo_login = self.obtener_tipo_login()
        
        try:
            if tipo_login == 'client_credentials':
                cred = ClientCredential(self.nombre_cliente, self.clave_cliente)
                contexto = ClientContext(url).with_credentials(cred)
            elif tipo_login == 'user_credentials':
                contexto = ClientContext(url).with_user_credentials(self.nombre_usuario, self.clave_usuario)
            else:
                raise ValueError(f"El tipo de autenticación '{tipo_login}' no es válido.")
            
            self.set_contexto(contexto)
            return contexto
        except Exception as e:
            self.mostrar(f"Error al crear el contexto: {e}", True)
            raise e
        
    def verificar_contexto(self, contexto: ClientContext|None = None) -> bool:
        """
        Verifica si el contexto de SharePoint es válido.
        
        :param contexto: Contexto de cliente de SharePoint (opcional)
        :return: True si el contexto es válido, False en caso contrario
        
        :raises ValueError: Si el contexto no está definido
        """
        if contexto is None: contexto = self.get_contexto()
        
        try:
            if contexto is None:
                raise ValueError("El contexto no está definido.")
            
            contexto.web.get().execute_query()
            self.mostrar(f"Conexión exitosa a SharePoint: {contexto.web.properties['Title']}")
            
            return True
        except Exception as e:
            self.mostrar(f"Error al verificar el contexto: {e}", True)
            return False
        
    def verificar_archivo(self, url: str) -> bool:
        """
        Verifica si un archivo existe en SharePoint.
        
        :param url: URL del archivo en SharePoint
        :return: ``True`` si el archivo existe, ``False`` en caso contrario
        
        :raises ValueError: Si la URL no está definida
        """
        if url is None:
            raise ValueError("La URL debe estar definida.")
        
        contexto = self.get_contexto()
        
        if contexto is None:
            self.mostrar(f"El contexto no está definido", True)
            raise ValueError("El contexto no está definido.")
        
        try:
            file = File(contexto, ResourcePath(url))
            contexto.load(file, ["Exists"]).execute_query()
            return file.properties["Exists"]
        except Exception as e:
            self.mostrar(f"Error al verificar el archivo: {e}", True)
            return False
        
    def verificar_carpeta(self, url: str) -> bool:
        """
        Verifica si una carpeta existe en SharePoint.
        
        :param url: URL de la carpeta en SharePoint
        :return: ``True`` si la carpeta existe, ``False`` en caso contrario
        
        :raises ValueError: Si la URL no está definida
        """
        if url is None:
            raise ValueError("La URL debe estar definida.")
        
        try:
            carpeta = self.obtener_carpeta(url)
            if carpeta is None:
                self.mostrar(f"La carpeta no existe: {url}", True)
                return False
            
            return carpeta.properties["Exists"]
        except Exception as e:
            self.mostrar(f"Error al verificar la carpeta: {e}", True)
            return False
        
    def obtener_listado_completo_de_archivos(self, url: str) -> list|None:
        """
        Devuelve un listado completo de archivos en una carpeta de SharePoint o en subcarpetas.
        
        :param url: URL de la carpeta en SharePoint
        :return: Listado de archivos en la carpeta y en subcarpetas
        
        :raises ValueError: Si la URL no está definida
        """
        if url is None:
            raise ValueError("La URL debe estar definida.")
        
        contexto = self.get_contexto()
        
        archivos_encontrados = []
        
        try:
            carpeta = self.obtener_carpeta(url)
            if carpeta is None:
                self.mostrar(f"La carpeta no existe: {url}", True)
                return None
            
            archivos = carpeta.files
            contexto.load(archivos).execute_query()
            if archivos: # si hay archivos en la carpeta
                archivos_encontrados.extend([
                    archivo.properties["Name"] for archivo in archivos
                ])
            
            subcarpetas = carpeta.folders
            contexto.load(subcarpetas).execute_query()
            if subcarpetas: # si hay subcarpetas en la carpeta
                for subcarpeta in subcarpetas:
                    archivo_en_subcarpeta = self.obtener_listado_completo_de_archivos(subcarpeta.properties["Name"])
                    
                    if archivo_en_subcarpeta:
                        archivos_encontrados.extend(archivo_en_subcarpeta)
            
            return archivos_encontrados
        except Exception as e:
            self.mostrar(f"Error al obtener el listado de archivos: {e}", True)
            return []
        
    def crear_carpeta(self, url: str, nombre_carpeta: str = '') -> Folder|None:
        """
        Crea una carpeta en SharePoint.
        
        :param url: URL de la carpeta en SharePoint
        :param nombre_carpeta: Nombre de la nueva carpeta (opcional)
        :return: Carpeta creada
        
        :raises ValueError: Si la URL no está definida o el nombre de la carpeta no es válido
        """
        if url is None:
            raise ValueError("La URL debe estar definida.")
        
        contexto = self.get_contexto()
        
        try:
            direccion_carpeta = url + '/' + nombre_carpeta if nombre_carpeta != '' else url
            if self.verificar_carpeta(direccion_carpeta): 
                return self.obtener_carpeta(direccion_carpeta)
            return contexto.web.folders.add(direccion_carpeta).execute_query()
        
        except Exception as e:
            self.mostrar(f"Error al crear la carpeta: {e}", True)
            raise e
        
    def subir_archivo(self, url: str, archivo: str) -> File:
        """
        Sube un archivo a SharePoint.
        
        :param url: URL de la carpeta en SharePoint
        :param archivo: Ruta del archivo local a subir
        :return: Archivo subido
        
        :raises ValueError: Si la URL o el archivo no están definidos
        """
        if url is None:
            raise ValueError("La URL debe estar definida.")
        
        if archivo is None:
            raise ValueError("La ruta del archivo debe estar definida.")
        
        carpeta_destino = self.obtener_carpeta(url)
        if carpeta_destino is None:
            self.mostrar(f"La carpeta no existe: {url}", True)
            raise ValueError("La carpeta destino no existe.")
        
        try:
            with open(archivo, 'rb') as contenido:
                nombre_archivo = os.path.basename(archivo)            
                return carpeta_destino.upload_file(nombre_archivo, contenido).execute_query()
        except Exception as e:
            self.mostrar(f"Error al subir el archivo: {e}", True)
            raise e
        
    def descargar_archivo(self, url: str, destino: str) -> File:
        """
        Descarga un archivo de SharePoint.
        
        :param url: URL del archivo en SharePoint
        :param destino: Ruta local donde se guardará el archivo descargado
        :return: Archivo descargado
        
        :raises ValueError: Si la URL o el destino no están definidos
        """
        if url is None:
            raise ValueError("La URL debe estar definida.")
        
        if destino is None:
            raise ValueError("La ruta de destino debe estar definida.")
        
        archivo = self.obtener_archivo(url)
        if archivo is None:
            self.mostrar(f"El archivo no existe: {url}", True)
            raise ValueError("El archivo no existe.")
        
        try:
            with open(destino, 'wb') as contenido:
                return archivo.download(contenido).execute_query()
        except Exception as e:
            self.mostrar(f"Error al descargar el archivo: {e}", True)
            raise e
        
    def eliminar_archivo(self, url: str) -> bool:
        """
        Elimina un archivo de SharePoint.
        
        :param url: URL del archivo en SharePoint
        :return: ``True`` si el archivo fue eliminado, ``False`` en caso contrario
        
        :raises ValueError: Si la URL no está definida
        """
        if url is None:
            raise ValueError("La URL debe estar definida.")
                
        try:
            archivo = self.obtener_archivo(url)
            if archivo is None:
                self.mostrar(f"El archivo no existe: {url}", True)
                return False
            
            archivo.delete_object().execute_query()
            return True
        except Exception as e:
            self.mostrar(f"Error al eliminar el archivo: {e}", True)
            return False
        
    def eliminar_carpeta(self, url: str) -> bool:
        """
        Elimina una carpeta de SharePoint.
        
        :param url: URL de la carpeta en SharePoint
        :return: ``True`` si la carpeta fue eliminada, ``False`` en caso contrario
        
        :raises ValueError: Si la URL no está definida
        """
        if url is None:
            raise ValueError("La URL debe estar definida.")
                
        try:
            carpeta = self.obtener_carpeta(url)
            if carpeta is None:
                self.mostrar(f"La carpeta no existe: {url}", True)
                return False
            
            carpeta.delete_object().execute_query()
            return True
        except Exception as e:
            self.mostrar(f"Error al eliminar la carpeta: {e}", True)
            return False
        
    def copiar_archivo(self, url_origen: str, url_destino: str) -> bool:
        """
        Copia un archivo de SharePoint a otra ubicación en SharePoint.
        
        :param url_origen: URL del archivo de origen en SharePoint
        :param url_destino: URL de la carpeta de destino en SharePoint
        :return: ``True`` si el archivo fue copiado, ``False`` en caso contrario
        
        :raises ValueError: Si las URLs no están definidas
        """
        if url_origen is None:
            raise ValueError("La URL de origen debe estar definida.")
        
        if url_destino is None:
            raise ValueError("La URL de destino debe estar definida.")
                
        try:
            archivo = self.obtener_archivo(url_origen)
            if archivo is None:
                self.mostrar(f"El archivo no existe: {url_origen}", True)
                return False
            nombre_archivo = os.path.basename(url_origen)
            
            carpeta_destino = self.obtener_carpeta(url_destino)
            if carpeta_destino is None:
                self.mostrar(f"La carpeta de destino no existe: {url_destino}", True)
                return False
            
            archivo.copyto(
                carpeta_destino.properties["ServerRelativeUrl"] + '/' + nombre_archivo, 
                True # para sobrescribir el archivo si ya existe
            ).execute_query()
            return True
        
        except Exception as e:
            self.mostrar(f"Error al copiar el archivo: {e}", True)
            return False
        
    def mover_archivo(self, url_origen: str, url_destino: str) -> bool:
        """
        Mueve un archivo de SharePoint a otra ubicación en SharePoint.
        
        :param url_origen: URL del archivo de origen en SharePoint
        :param url_destino: URL de la carpeta de destino en SharePoint
        :return: ``True`` si el archivo fue movido, ``False`` en caso contrario
        
        :raises ValueError: Si las URLs no están definidas
        """
        if url_origen is None:
            raise ValueError("La URL de origen debe estar definida.")
        
        if url_destino is None:
            raise ValueError("La URL de destino debe estar definida.")
                
        try:
            archivo = self.obtener_archivo(url_origen)
            if archivo is None:
                self.mostrar(f"El archivo no existe: {url_origen}", True)
                return False
            nombre_archivo = os.path.basename(url_origen)
            
            carpeta_destino = self.obtener_carpeta(url_destino)
            if carpeta_destino is None:
                self.mostrar(f"La carpeta de destino no existe: {url_destino}", True)
                return False
            
            archivo.moveto(
                carpeta_destino.properties["ServerRelativeUrl"] + '/' + nombre_archivo,
                1 # para sobrescribir el archivo si ya existe
            ).execute_query()
            return True
        
        except Exception as e:
            self.mostrar(f"Error al mover el archivo: {e}", True)
            return False
        
    def crear_estructura_carpetas(self, url: str, estructura: list) -> bool:
        """
        Crea una estructura de carpetas en SharePoint.
        
        :param url: URL de la carpeta en SharePoint
        :param estructura: Lista de carpetas a crear (ejemplo: ['carpeta1', 'carpeta2/carpeta3'])
        :return: ``True`` si la estructura fue creada, ``False`` en caso contrario
        
        :raises ValueError: Si la URL o la estructura no están definidas
        """
        if url is None:
            raise ValueError("La URL debe estar definida.")
        
        if estructura is None or not isinstance(estructura, list):
            raise ValueError("La estructura debe ser una lista.")
        
        try:
            for carpeta in estructura:
                self.crear_carpeta(url, carpeta)
            
            return True
        except Exception as e:
            self.mostrar(f"Error al crear la estructura de carpetas: {e}", True)
            return False
        
    def crear_estructura_carpetas_con_fecha(self, url: str) -> bool:
        """
        Crea una estructura de carpetas en SharePoint con la fecha actual en formato [ruta/anio/mes/dia].
        
        :param url: URL de la carpeta en SharePoint
        :return: ``True`` si la estructura fue creada, ``False`` en caso contrario
        
        :raises ValueError: Si la URL o la estructura no están definidas
        """
        if url is None:
            raise ValueError("La URL debe estar definida.")
        
        fecha_actual = datetime.now()
        estructura = [
            f"{fecha_actual.year}", 
            f"{fecha_actual.month:02}",
            f"{fecha_actual.day:02}"
        ]
        
        return self.crear_estructura_carpetas(url, estructura)