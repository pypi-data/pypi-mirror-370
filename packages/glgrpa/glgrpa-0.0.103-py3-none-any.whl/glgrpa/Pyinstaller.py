def obtener_ruta_recurso(ruta_recurso: str) -> str:
    """
    Devuelve la ruta absoluta de un recurso, considerando si el script está empaquetado con PyInstaller o no.
    Busca la raíz del repositorio (donde está .git) si no está empaquetado.

    :param ruta_recurso: Ruta del recurso (puede ser absoluta o relativa).
    :return: Ruta absoluta del recurso.
    """
    import os
    import sys

    # Verifica si el script está empaquetado con PyInstaller
    if os.path.isabs(ruta_recurso):
        return ruta_recurso
    
    if hasattr(sys, '_MEIPASS'):
        base_path = os.path.dirname(sys.executable)
    else:
        # Buscar la raíz del repositorio subiendo carpetas hasta encontrar .git
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while True:
            if os.path.isdir(os.path.join(current_dir, '.git')):
                base_path = current_dir
                break
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                # Llegó a la raíz del sistema, usar el directorio actual
                base_path = current_dir
                break
            current_dir = parent_dir

    return os.path.join(base_path, ruta_recurso)