# glgrpa

`glgrpa` es una librería diseñada para automatizar tareas relacionadas con RPA (Robotic Process Automation) dentro del entorno del Grupo Los Grobo. Esta librería proporciona herramientas para interactuar con navegadores web, manejar archivos Excel, gestionar descargas y realizar operaciones específicas en aplicaciones como ARCA.

## Instalación

Puedes instalar la librería directamente desde PyPI (cuando esté publicada) utilizando pip:

```bash
pip install glgrpa
```

## Características

- **Automatización de Navegadores** : Basado en Selenium, permite interactuar con elementos web, realizar clics, ingresar texto, manejar ventanas y más.
- **Gestión de Descargas** : Facilita la organización y limpieza de carpetas de descargas personalizadas.
- **Manejo de Archivos Excel** : Permite leer archivos Excel y convertirlos en DataFrames de pandas.
- **Interacción con ARCA** : Automatiza tareas específicas en la plataforma ARCA, como el inicio de sesión, selección de relaciones y descarga de cartas de porte electrónicas.
- **Terminal y Logs** : Incluye herramientas para mostrar mensajes en la consola con colores y formatos para facilitar el seguimiento de la ejecución.

## Estructura del Proyecto

La librería está organizada en los siguientes módulos:

- **`src/Terminal`** : Proporciona herramientas para mostrar mensajes en la consola y gestionar tiempos de espera.
- **`src/Chrome`** : Contiene funcionalidades para interactuar con el navegador Chrome utilizando Selenium.
- **`src/Windows`** : Maneja operaciones relacionadas con el sistema de archivos en Windows, como mover archivos y crear estructuras de carpetas.
- **`src/Excel`** : Facilita la lectura de archivos Excel.
- **`src/ARCA`** : Incluye clases específicas para interactuar con la plataforma ARCA.

## Uso

### Ejemplo de Uso Básico

```python
from glgrpa.src.ARCA.Cartas_de_porte_electronicas.AplicativoCartasDePorteElectronicas import AplicativoCartaDePorteElectronica

# Inicializar la clase
app = AplicativoCartaDePorteElectronica(dev=True)

# Abrir navegador y navegar a ARCA
app.abrir_navegador()
app.navegar_inicio()

# Ingresar credenciales
app.ingresar_credenciales()

# Cambiar relación
app.cambiar_relacion("Nombre de la relación")

# Descargar cartas de porte
cpe_list = app.obtener_listado_cpe()
for cpe in cpe_list:
    app.descargar_carta_de_porte(cpe)
```

### Leer un Archivo Excel

```python
from glgrpa.src.Excel.Excel import Excel

# Leer un archivo Excel
excel = Excel("ruta_del_archivo.xlsx")
dataframe = excel.leer_excel("NombreHoja")
print(dataframe)
```

## Resolución de Rutas para Tareas Programadas

Al ejecutar aplicaciones empaquetadas (`.exe`) desde tareas programadas de Windows, es común que ocurra un problema de duplicación de rutas donde el directorio de trabajo actual no es el mismo que el directorio del ejecutable.

### Problema Común

```
❌ Error: No se encontró el archivo de variables de entorno:
C:\Trabajadores Virtuales\GLGRPA - CONTABILIDAD - RODOLFO\ap1_TipoCambioSAP\ap1_TipoCambioSAP\.env.production
```

### Solución

La librería `glgrpa` incluye métodos utilitarios para resolver este problema:

```python
import os
from glgrpa import ControlEjecucion
from dotenv import load_dotenv

# ✅ Forma correcta de cargar variables de entorno
ruta_env = ControlEjecucion.resolver_ruta_variables_entorno('.env.production')

if os.path.exists(ruta_env):
    load_dotenv(ruta_env)
    print(f"✅ Variables cargadas desde: {ruta_env}")
else:
    print(f"❌ No se encontró archivo: {ruta_env}")

# ✅ Para otros tipos de archivos de configuración
from glgrpa.Windows import Windows

ruta_config = Windows.resolver_ruta_archivo('config.ini')
ruta_datos = Windows.resolver_ruta_archivo('datos.json')
```

### Uso con ControlEjecucion

```python
from glgrpa import ControlEjecucion
import os
from dotenv import load_dotenv

@ControlEjecucion.decorador_ejecucion_controlada(
    intentos_maximos=3,
    permitir_multiples_ejecuciones_diarias=False,
    email_destinatarios=['admin@empresa.com'],
    smtp_server='smtp.outlook.com',
    smtp_port=587,
    smtp_username='robot@empresa.com',
    smtp_password='password'
)
def mi_proceso_rpa():
    # Cargar variables de entorno correctamente
    ruta_env = ControlEjecucion.resolver_ruta_variables_entorno()
    if os.path.exists(ruta_env):
        load_dotenv(ruta_env)

    # Tu lógica de automatización aquí
    pass

if __name__ == "__main__":
    mi_proceso_rpa()
```

### Configuración de Tareas Programadas

Para evitar problemas con tareas programadas, asegúrate de configurar:

1. **Directorio de inicio**: Configura que la tarea programada inicie en el directorio donde está el `.exe`
2. **Permisos**: Ejecutar con privilegios de usuario apropiados
3. **Sesión interactiva**: Para procesos RPA que requieren GUI, asegurar sesión de escritorio activa

## Automatización SAP Robusta

La librería incluye funcionalidades avanzadas para automatización SAP que se adaptan automáticamente a diferentes entornos de ejecución:

### Métodos Adaptativos para VMs

Las transacciones SAP (como `OB08`) implementan **métodos adaptativos** que funcionan tanto en entornos con GUI activo como en VMs sin sesión interactiva:

```python
from glgrpa.transacciones.OB08 import OB08

# Inicializar transacción
ob08 = OB08(base_url="...", usuario="...", clave="...", dev=True)

# Los métodos se adaptan automáticamente al entorno:
# - GUI activo: usa teclas de acceso rápido (Ctrl+S, Shift+F3, Escape)
# - GUI no activo: usa click directo Selenium (para VMs/tareas programadas)
ob08.guardar()                    # Ctrl+S preferido, 3 fallbacks Selenium
ob08.finalizar()                  # Shift+F3 preferido, 3 fallbacks Selenium
ob08.omitir()                     # Shift+F8 preferido, 3 fallbacks Selenium
ob08.cancelar_entradas_nuevas()   # Escape preferido, 3 fallbacks Selenium
ob08.cancelar_menu_inicial()      # Escape preferido, 3 fallbacks Selenium
```

### Detección y Manejo de Diálogos Modales

**Novedad en v0.0.97**: Sistema automático de detección e interacción con diálogos modales SAP:

```python
# Detectar automáticamente diálogos presentes
dialogo_info = ob08.detectar_dialogo_modal()

if dialogo_info['presente']:
    print(f"🔔 Diálogo detectado: {dialogo_info['tipo']}")
    print(f"Pregunta: {dialogo_info['texto_pregunta']}")
    print(f"Botones: {dialogo_info['botones']}")

    # Responder automáticamente
    if dialogo_info['tipo'] == 'cancelar_actualizacion':
        ob08.interactuar_dialogo_modal('si')  # Confirmar cancelación

    elif dialogo_info['tipo'] == 'fin_actualizacion':
        ob08.interactuar_dialogo_modal('si')     # Guardar cambios
        # ob08.interactuar_dialogo_modal('no')   # Descartar cambios
        # ob08.interactuar_dialogo_modal('cancelar')  # Cancelar diálogo

# Diálogos soportados:
# - "Cancelar actualización": ¿Realmente desea cancelar? (Sí/No)
# - "Fin actualización": ¿Grabar primero modificaciones? (Sí/No/Cancelar)
```

### Botones SAP Completos (v0.0.97)

Cobertura completa de botones críticos en transacciones SAP:

| Botón                   | Método                       | Tecla Preferida | Fallbacks Selenium   |
| ----------------------- | ---------------------------- | --------------- | -------------------- |
| **Guardar**             | `guardar()`                  | Ctrl+S          | ID, accesskey, texto |
| **Finalizar**           | `finalizar()`                | Shift+F3        | ID, accesskey, texto |
| **Omitir**              | `omitir()`                   | Shift+F8        | ID, accesskey, texto |
| **Cancelar (Entradas)** | `cancelar_entradas_nuevas()` | Escape          | ID, accesskey, texto |
| **Cancelar (Inicial)**  | `cancelar_menu_inicial()`    | Escape          | ID, accesskey, texto |

### Estrategias Múltiples de Interacción

Cada operación crítica implementa **múltiples estrategias de fallback**:

1. **Método preferido**: Teclas de acceso rápido (Ctrl+S, F5, etc.)
2. **Fallback 1**: Click directo en elementos HTML por ID
3. **Fallback 2**: Búsqueda por accesskey o atributos específicos
4. **Fallback 3**: Búsqueda por texto o título del elemento

```python
# Ejemplo: Flujo completo con manejo automático
try:
    # Procesar datos
    ob08.ingresar_tipo_de_cambio(df_divisas)

    # Manejar diálogos automáticamente si aparecen
    dialogo_info = ob08.detectar_dialogo_modal()
    if dialogo_info['presente']:
        ob08.interactuar_dialogo_modal('si')  # Guardar cambios

    # Finalizar exitosamente
    ob08.finalizar()

except Exception as e:
    print(f"❌ Error en proceso: {e}")

    # Limpieza automática con detección de contexto
    try:
        # Manejar diálogos primero
        dialogo_info = ob08.detectar_dialogo_modal()
        if dialogo_info['presente']:
            ob08.interactuar_dialogo_modal('no')  # Rechazar cambios

        # Cancelar según contexto actual
        if "Entradas nuevas" in ob08.driver.title:
            ob08.cancelar_entradas_nuevas()
        else:
            ob08.cancelar_menu_inicial()

    except Exception as cleanup_error:
        print(f"⚠️ Error en limpieza: {cleanup_error}")
```

### Debugging Avanzado

- **Screenshots automáticos** en caso de fallo con nombres descriptivos
- **Logging detallado** con emojis para fácil identificación
- **Información contextual** de elementos DOM encontrados/no encontrados
- **Estrategias de reintento** documentadas en logs
- **Detección automática** de diálogos modales con información completa

## Requisitos

Los requisitos de la librería están especificados en el archivo `requirements.txt`:

- `selenium`
- `pandas`
- `colorama`
- `openpyxl`
- `office365-rest-python-client`

## Autor

**Gabriel Bellome** < [gabriel.bellome@losgrobo.com](vscode-file://vscode-app/c:/Users/gabriel.bellome/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) >

## Licencia

Este proyecto está bajo una licencia privada y es propiedad del Grupo Los Grobo.
