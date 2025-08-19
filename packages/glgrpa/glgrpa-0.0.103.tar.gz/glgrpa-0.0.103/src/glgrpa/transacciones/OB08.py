import os
import time
from ..SAP import SAP
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver

import pandas as pd

class OB08(SAP):
    titulo_pagina_inicio = 'Modificar vista "Tipos de cambio para la conversión": Resumen'
    
    ELEMENTOS_PAGINA_INICIO_OB08 = {
        'iframe': '',
        'button_entradas_nuevas_por_titulo': '//div[@title="Entradas nuevas (F5)"]',
        'button_entradas_nuevas_por_span': '//span[contains(text(), "ntradas nuevas")]',
        'button_entradas_nuevas_por_accesskey': '//div[@accesskey="E"]',
        # Elementos para botón Cancelar (menu inicial)
        'button_cancelar_inicial_id': '//div[contains(@id, "btn[12]") and contains(@title, "Cancelar")]',
        'button_cancelar_inicial_accesskey': '//div[@accesskey="C" and contains(@title, "Cancelar")]',
        'button_cancelar_inicial_accesskey_alt': '//*[@accesskey="C"]',
        'button_cancelar_inicial_titulo': '//*[@title="Cancelar (Escape)" or contains(@title, "Cancelar")]',
        'button_cancelar_inicial_texto': '//span[contains(text(), "ancelar")]'
    }

    ELEMENTOS_ENTRADAS_NUEVAS = {
        'iframe': '/html/body/div[3]/div/div/div/div/main/div/section/div/div/div[2]/div[3]/iframe',
        'input_FullXPath': '/html/body/table/tbody/tr/td/div/form/div/div[4]/div/div[1]/table/tbody[1]/tr[2]/td[2]/div/div[2]/table/tbody/tr[1]/td[1]/div/span/input',
        'input_XPath': '//*[@id="M0:46:1[1,1]_c"]',
        'input_guardar_id': '//div[contains(@id, "btn[11]") and contains(@title, "Guardar")]',
        'input_guardar_accesskey': '//div[@accesskey="G" and contains(@title, "Guardar")]',
        'input_guardar_accesskey_alt' : '//*[@accesskey="G"]',
        'input_guardar_titulo': '//*[@title="Guardar (Ctrl+S)" or contains(@title, "Guardar")]',
        'input_guardar_texto': '//span[contains(text(), "uardar")]',
        # Elementos para botón Finalizar
        'button_finalizar_id': '//div[contains(@id, "btn[15]") and contains(@title, "Finalizar")]',
        'button_finalizar_accesskey': '//div[@accesskey="F" and contains(@title, "Finalizar")]',
        'button_finalizar_accesskey_alt': '//*[@accesskey="F"]',
        'button_finalizar_titulo': '//*[@title="Finalizar (Mayús+F3)" or contains(@title, "Finalizar")]',
        'button_finalizar_texto': '//span[contains(text(), "inalizar")]',
        # Elementos para botón Omitir
        'button_omitir_id': '//div[contains(@id, "btn[20]") and contains(@title, "Omitir")]',
        'button_omitir_accesskey': '//div[@accesskey="O" and contains(@title, "Omitir")]',
        'button_omitir_accesskey_alt': '//*[@accesskey="O"]',
        'button_omitir_titulo': '//*[@title="Omitir (Mayús+F8)" or contains(@title, "Omitir")]',
        'button_omitir_texto': '//span[contains(text(), "mitir")]',
        # Elementos para botón Cancelar (menu Entradas Nuevas)
        'button_cancelar_entradas_id': '//div[contains(@id, "btn[12]") and contains(@title, "Cancelar")]',
        'button_cancelar_entradas_accesskey': '//div[@accesskey="C" and contains(@title, "Cancelar")]',
        'button_cancelar_entradas_accesskey_alt': '//*[@accesskey="C"]',
        'button_cancelar_entradas_titulo': '//*[@title="Cancelar (Escape)" or contains(@title, "Cancelar")]',
        'button_cancelar_entradas_texto': '//span[contains(text(), "ancelar")]'
    }

    # Elementos para cuadros de diálogo modales
    ELEMENTOS_DIALOGOS_MODALES = {
        # Cuadro de diálogo: Cancelar Actualización
        'dialogo_cancelar_actualizacion': {
            'container': '//div[@role="dialog"]//span[contains(text(), "Cancelar actualización")]',
            'titulo': 'Cancelar actualización',
            'texto_principal': 'Se perderán las entradas',
            'texto_pregunta': '¿Realmente desea cancelar?',
            'boton_si_id': '//div[contains(@id, "SPOP-OPTION1") or contains(@id, "btnSPOP-OPTION1")]',
            'boton_si_accesskey': '//div[@accesskey="S" and contains(text(), "Sí")]',
            'boton_si_texto': '//span[contains(text(), "Sí")]',
            'boton_no_id': '//div[contains(@id, "SPOP-OPTION2") or contains(@id, "btnSPOP-OPTION2")]',
            'boton_no_accesskey': '//div[@accesskey="N" and contains(text(), "No")]',
            'boton_no_texto': '//span[contains(text(), "No")]'
        },
        # Cuadro de diálogo: Fin Actualización
        'dialogo_fin_actualizacion': {
            'container': '//div[@role="dialog"]//span[contains(text(), "Fin actualización")]',
            'titulo': 'Fin actualización',
            'texto_principal': 'Se han modificado datos.',
            'texto_pregunta': '¿Grabar primero modificaciones?',
            'boton_si_id': '//div[contains(@id, "SPOP-OPTION1") or contains(@id, "btnSPOP-OPTION1")]',
            'boton_si_accesskey': '//div[@accesskey="S" and contains(text(), "Sí")]',
            'boton_si_texto': '//span[contains(text(), "Sí")]',
            'boton_no_id': '//div[contains(@id, "SPOP-OPTION2") or contains(@id, "btnSPOP-OPTION2")]',
            'boton_no_accesskey': '//div[@accesskey="N" and contains(text(), "No")]',
            'boton_no_texto': '//span[contains(text(), "No")]',
            'boton_cancelar_id': '//div[contains(@id, "SPOP-OPTION_CAN") or contains(@id, "btnSPOP-OPTION_CAN")]',
            'boton_cancelar_accesskey': '//div[@accesskey="C" and contains(text(), "Cancelar")]',
            'boton_cancelar_texto': '//span[contains(text(), "Cancelar")]'
        }
    }
    
    def __init__(self, base_url: str, usuario: str, clave: str, usuario_microsoft: str = '', clave_microsoft: str = '', driver: WebDriver|None = None, dev:bool = False):
        super().__init__(
            base_url=base_url, 
            usuario=usuario,
            clave=clave,
            usuario_microsoft=usuario_microsoft,
            clave_microsoft=clave_microsoft,
            driver=driver, 
            dev=dev
        )
        self.driver = driver
    
    # Métodos de navegación y finalización de transacción
    def finalizar(self) -> None:
        """
        Finaliza la transacción OB08 con estrategias múltiples.
        
        Implementa múltiples estrategias para garantizar que la finalización funcione
        tanto en entornos con GUI activo como en VMs sin sesión interactiva:
        
        1. Shift+F3 (método preferido cuando GUI está activo)
        2. Click directo en el botón "Finalizar" via Selenium
        3. Click por accesskey (F) via Selenium
        4. Click por título via Selenium
        
        ---
        Se utiliza al final de procesos en OB08 para cerrar la transacción correctamente.
        Implementa verificación de GUI y fallback automático a métodos Selenium.
        
        ---
        ### Ejemplo
        ```python
        # Al finalizar proceso en SAP
        ob08.finalizar()
        
        # La transacción se cierra automáticamente
        # usando la estrategia más apropiada para el entorno
        ```
        >>> None  # Si la finalización se ejecuta correctamente
        
        ---
        ### Raises
        #### Exception
        - Si no se puede finalizar con ninguna de las estrategias disponibles
        - Si el elemento de finalización no se encuentra en ningún iframe
        """
        self.mostrar("🏁 Finalizando transacción OB08")
        
        # Estrategia 1: Click directo en botón Finalizar por ID (método preferido)
        if self._click_finalizar_por_id():
            self.mostrar("✅ Finalización exitosa via click directo en botón")
            self.demora()
            return
            
        # Estrategia 2: Click por accesskey "F"
        if self._click_finalizar_por_accesskey():
            self.mostrar("✅ Finalización exitosa via accesskey")
            self.demora()
            return
            
        # Estrategia 3: Click por título "Finalizar (Mayús+F3)"
        if self._click_finalizar_por_titulo():
            self.mostrar("✅ Finalización exitosa via título")
            self.demora()
            return
        
        # Estrategia 4: Shift+F3 (fallback para casos específicos)
        try:
            if self._verificar_sesion_gui_activa():
                self.mostrar("⌨️ Usando Shift+F3 como fallback")
                self.enviar_tecla_ventana('SHIFT', 'F3')
                self.demora()
                return
        except Exception as e:
            self.mostrar(f"⚠️ Shift+F3 falló: {str(e)}", True)
            
        # Si todas las estrategias fallan
        self.mostrar("❌ No se pudo finalizar con ninguna estrategia", True)
        
        # Tomar screenshot para debugging
        try:
            self.tomar_screenshot("error_finalizar_ob08")
            self.mostrar("📸 Screenshot guardado: error_finalizar_ob08.png")
        except Exception:
            pass
            
        raise Exception(
            "FALLO CRÍTICO: No se pudo finalizar transacción OB08. "
            "Todas las estrategias fallaron: Shift+F3, click directo, accesskey, título. "
            "Posibles causas: 1) Interfaz SAP cambió, 2) Elemento no disponible, "
            "3) Problema de permisos, 4) Sesión SAP expirada."
        )

    def _click_finalizar_por_id(self) -> bool:
        """
        Intenta hacer click en el botón Finalizar por su ID específico.
        
        Busca el elemento con ID que contiene "btn[15]" y datos de finalización.
        Utiliza búsqueda en todos los iframes para manejar la estructura de SAP.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_finalizar_id']):
                self.mostrar("✅ Click exitoso en botón Finalizar por ID")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por ID: {str(e)}", True)
            return False

    def _click_finalizar_por_accesskey(self) -> bool:
        """
        Intenta hacer click en el botón Finalizar por su accesskey "F".
        
        Busca elementos con accesskey="F" que contengan texto relacionado con finalizar.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_finalizar_accesskey']):
                self.mostrar("✅ Click exitoso en botón Finalizar por accesskey")
                return True

            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_finalizar_accesskey_alt']):
                self.mostrar("✅ Click exitoso en elemento con accesskey F")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por accesskey: {str(e)}", True)
            return False

    def _click_finalizar_por_titulo(self) -> bool:
        """
        Intenta hacer click en el botón Finalizar por su título.
        
        Busca elementos que contengan "Finalizar" en su título o texto.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_finalizar_titulo']):
                self.mostrar("✅ Click exitoso en botón Finalizar por título")
                return True

            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_finalizar_texto']):
                self.mostrar("✅ Click exitoso en texto Finalizar")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por título: {str(e)}", True)
            return False
    
    # Métodos para botón Omitir
    def omitir(self) -> None:
        """
        Omite la operación actual en OB08 con estrategias múltiples.
        
        Implementa múltiples estrategias para garantizar que la operación funcione
        tanto en entornos con GUI activo como en VMs sin sesión interactiva:
        
        1. Shift+F8 (método preferido cuando GUI está activo)
        2. Click directo en el botón "Omitir" via Selenium
        3. Click por accesskey (O) via Selenium
        4. Click por título via Selenium
        
        ---
        Se utiliza para omitir entradas específicas durante el procesamiento en OB08.
        Implementa verificación de GUI y fallback automático a métodos Selenium.
        
        ---
        ### Ejemplo
        ```python
        # Para omitir una entrada específica
        ob08.omitir()
        
        # La operación se omite automáticamente
        # usando la estrategia más apropiada para el entorno
        ```
        >>> None  # Si la operación se ejecuta correctamente
        
        ---
        ### Raises
        #### Exception
        - Si no se puede omitir con ninguna de las estrategias disponibles
        - Si el elemento de omisión no se encuentra en ningún iframe
        """
        self.mostrar("⏭️ Omitiendo operación en OB08")
        
        # Estrategia 1: Click directo en botón Omitir por ID (método preferido)
        if self._click_omitir_por_id():
            self.mostrar("✅ Omisión exitosa via click directo en botón")
            self.demora()
            return
            
        # Estrategia 2: Click por accesskey "O"
        if self._click_omitir_por_accesskey():
            self.mostrar("✅ Omisión exitosa via accesskey")
            self.demora()
            return
            
        # Estrategia 3: Click por título "Omitir (Mayús+F8)"
        if self._click_omitir_por_titulo():
            self.mostrar("✅ Omisión exitosa via título")
            self.demora()
            return
        
        # Estrategia 4: Shift+F8 (fallback para casos específicos)
        try:
            if self._verificar_sesion_gui_activa():
                self.mostrar("⌨️ Usando Shift+F8 como fallback")
                self.enviar_tecla_ventana('SHIFT', 'F8')
                self.demora()
                return
        except Exception as e:
            self.mostrar(f"⚠️ Shift+F8 falló: {str(e)}", True)
            
        # Si todas las estrategias fallan
        self.mostrar("❌ No se pudo omitir con ninguna estrategia", True)
        
        # Tomar screenshot para debugging
        try:
            self.tomar_screenshot("error_omitir_ob08")
            self.mostrar("📸 Screenshot guardado: error_omitir_ob08.png")
        except Exception:
            pass
            
        raise Exception(
            "FALLO CRÍTICO: No se pudo omitir operación en OB08. "
            "Todas las estrategias fallaron: Shift+F8, click directo, accesskey, título. "
            "Posibles causas: 1) Interfaz SAP cambió, 2) Elemento no disponible, "
            "3) Problema de permisos, 4) Sesión SAP expirada."
        )

    def _click_omitir_por_id(self) -> bool:
        """
        Intenta hacer click en el botón Omitir por su ID específico.
        
        Busca el elemento con ID que contiene "btn[20]" y datos de omisión.
        Utiliza búsqueda en todos los iframes para manejar la estructura de SAP.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_omitir_id']):
                self.mostrar("✅ Click exitoso en botón Omitir por ID")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por ID: {str(e)}", True)
            return False

    def _click_omitir_por_accesskey(self) -> bool:
        """
        Intenta hacer click en el botón Omitir por su accesskey "O".
        
        Busca elementos con accesskey="O" que contengan texto relacionado con omitir.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_omitir_accesskey']):
                self.mostrar("✅ Click exitoso en botón Omitir por accesskey")
                return True

            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_omitir_accesskey_alt']):
                self.mostrar("✅ Click exitoso en elemento con accesskey O")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por accesskey: {str(e)}", True)
            return False

    def _click_omitir_por_titulo(self) -> bool:
        """
        Intenta hacer click en el botón Omitir por su título.
        
        Busca elementos que contengan "Omitir" en su título o texto.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_omitir_titulo']):
                self.mostrar("✅ Click exitoso en botón Omitir por título")
                return True

            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_omitir_texto']):
                self.mostrar("✅ Click exitoso en texto Omitir")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por título: {str(e)}", True)
            return False
    
    # Métodos para botón Cancelar
    def cancelar_entradas_nuevas(self) -> None:
        """
        Cancela las operaciones en el menú de Entradas Nuevas con estrategias múltiples.
        
        Implementa múltiples estrategias para garantizar que la cancelación funcione
        tanto en entornos con GUI activo como en VMs sin sesión interactiva:
        
        1. Escape (método preferido cuando GUI está activo)
        2. Click directo en el botón "Cancelar" via Selenium
        3. Click por accesskey (C) via Selenium
        4. Click por título via Selenium
        
        ---
        Se utiliza para cancelar operaciones en el menú de entradas nuevas en OB08.
        Implementa verificación de GUI y fallback automático a métodos Selenium.
        
        ---
        ### Ejemplo
        ```python
        # Para cancelar desde entradas nuevas
        ob08.cancelar_entradas_nuevas()
        
        # La cancelación se ejecuta automáticamente
        # usando la estrategia más apropiada para el entorno
        ```
        >>> None  # Si la cancelación se ejecuta correctamente
        
        ---
        ### Raises
        #### Exception
        - Si no se puede cancelar con ninguna de las estrategias disponibles
        - Si el elemento de cancelación no se encuentra en ningún iframe
        """
        self.mostrar("❌ Cancelando operaciones en Entradas Nuevas")
        
        # Estrategia 1: Click directo en botón Cancelar por ID (método preferido)
        if self._click_cancelar_entradas_por_id():
            self.mostrar("✅ Cancelación exitosa via click directo en botón")
            self.demora()
            return
            
        # Estrategia 2: Click por accesskey "C"
        if self._click_cancelar_entradas_por_accesskey():
            self.mostrar("✅ Cancelación exitosa via accesskey")
            self.demora()
            return
            
        # Estrategia 3: Click por título "Cancelar (Escape)"
        if self._click_cancelar_entradas_por_titulo():
            self.mostrar("✅ Cancelación exitosa via título")
            self.demora()
            return
        
        # Estrategia 4: Escape (fallback para casos específicos)
        try:
            if self._verificar_sesion_gui_activa():
                self.mostrar("⌨️ Usando Escape como fallback")
                self.enviar_tecla_ventana('ESCAPE')
                self.demora()
                return
        except Exception as e:
            self.mostrar(f"⚠️ Escape falló: {str(e)}", True)
            
        # Si todas las estrategias fallan
        self.mostrar("❌ No se pudo cancelar con ninguna estrategia", True)
        
        # Tomar screenshot para debugging
        try:
            self.tomar_screenshot("error_cancelar_entradas_ob08")
            self.mostrar("📸 Screenshot guardado: error_cancelar_entradas_ob08.png")
        except Exception:
            pass
            
        raise Exception(
            "FALLO CRÍTICO: No se pudo cancelar en menú Entradas Nuevas de OB08. "
            "Todas las estrategias fallaron: Escape, click directo, accesskey, título. "
            "Posibles causas: 1) Interfaz SAP cambió, 2) Elemento no disponible, "
            "3) Problema de permisos, 4) Sesión SAP expirada."
        )

    def _click_cancelar_entradas_por_id(self) -> bool:
        """
        Intenta hacer click en el botón Cancelar por su ID específico (entradas nuevas).
        
        Busca el elemento con ID que contiene "btn[12]" y datos de cancelación.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_cancelar_entradas_id']):
                self.mostrar("✅ Click exitoso en botón Cancelar por ID")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por ID: {str(e)}", True)
            return False

    def _click_cancelar_entradas_por_accesskey(self) -> bool:
        """
        Intenta hacer click en el botón Cancelar por su accesskey "C" (entradas nuevas).
        
        Busca elementos con accesskey="C" que contengan texto relacionado con cancelar.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_cancelar_entradas_accesskey']):
                self.mostrar("✅ Click exitoso en botón Cancelar por accesskey")
                return True

            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_cancelar_entradas_accesskey_alt']):
                self.mostrar("✅ Click exitoso en elemento con accesskey C")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por accesskey: {str(e)}", True)
            return False

    def _click_cancelar_entradas_por_titulo(self) -> bool:
        """
        Intenta hacer click en el botón Cancelar por su título (entradas nuevas).
        
        Busca elementos que contengan "Cancelar" en su título o texto.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_cancelar_entradas_titulo']):
                self.mostrar("✅ Click exitoso en botón Cancelar por título")
                return True

            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_cancelar_entradas_texto']):
                self.mostrar("✅ Click exitoso en texto Cancelar")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por título: {str(e)}", True)
            return False

    def cancelar_menu_inicial(self) -> None:
        """
        Cancela las operaciones en el menú inicial de la transacción con estrategias múltiples.
        
        Implementa múltiples estrategias para garantizar que la cancelación funcione
        tanto en entornos con GUI activo como en VMs sin sesión interactiva:
        
        1. Escape (método preferido cuando GUI está activo)
        2. Click directo en el botón "Cancelar" via Selenium
        3. Click por accesskey (C) via Selenium
        4. Click por título via Selenium
        
        ---
        Se utiliza para cancelar operaciones en el menú inicial de la transacción OB08.
        Implementa verificación de GUI y fallback automático a métodos Selenium.
        
        ---
        ### Ejemplo
        ```python
        # Para cancelar desde el menú inicial
        ob08.cancelar_menu_inicial()
        
        # La cancelación se ejecuta automáticamente
        # usando la estrategia más apropiada para el entorno
        ```
        >>> None  # Si la cancelación se ejecuta correctamente
        
        ---
        ### Raises
        #### Exception
        - Si no se puede cancelar con ninguna de las estrategias disponibles
        - Si el elemento de cancelación no se encuentra en ningún iframe
        """
        self.mostrar("❌ Cancelando desde menú inicial de OB08")
        
        # Estrategia 1: Click directo en botón Cancelar por ID (método preferido)
        if self._click_cancelar_inicial_por_id():
            self.mostrar("✅ Cancelación exitosa via click directo en botón")
            self.demora()
            return
            
        # Estrategia 2: Click por accesskey "C"
        if self._click_cancelar_inicial_por_accesskey():
            self.mostrar("✅ Cancelación exitosa via accesskey")
            self.demora()
            return
            
        # Estrategia 3: Click por título "Cancelar (Escape)"
        if self._click_cancelar_inicial_por_titulo():
            self.mostrar("✅ Cancelación exitosa via título")
            self.demora()
            return
        
        # Estrategia 4: Escape (fallback para casos específicos)
        try:
            if self._verificar_sesion_gui_activa():
                self.mostrar("⌨️ Usando Escape como fallback")
                self.enviar_tecla_ventana('ESCAPE')
                self.demora()
                return
        except Exception as e:
            self.mostrar(f"⚠️ Escape falló: {str(e)}", True)
            
        # Si todas las estrategias fallan
        self.mostrar("❌ No se pudo cancelar con ninguna estrategia", True)
        
        # Tomar screenshot para debugging
        try:
            self.tomar_screenshot("error_cancelar_inicial_ob08")
            self.mostrar("📸 Screenshot guardado: error_cancelar_inicial_ob08.png")
        except Exception:
            pass
            
        raise Exception(
            "FALLO CRÍTICO: No se pudo cancelar en menú inicial de OB08. "
            "Todas las estrategias fallaron: Escape, click directo, accesskey, título. "
            "Posibles causas: 1) Interfaz SAP cambió, 2) Elemento no disponible, "
            "3) Problema de permisos, 4) Sesión SAP expirada."
        )

    def _click_cancelar_inicial_por_id(self) -> bool:
        """
        Intenta hacer click en el botón Cancelar por su ID específico (menú inicial).
        
        Busca el elemento con ID que contiene "btn[12]" y datos de cancelación.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_PAGINA_INICIO_OB08['button_cancelar_inicial_id']):
                self.mostrar("✅ Click exitoso en botón Cancelar por ID")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por ID: {str(e)}", True)
            return False

    def _click_cancelar_inicial_por_accesskey(self) -> bool:
        """
        Intenta hacer click en el botón Cancelar por su accesskey "C" (menú inicial).
        
        Busca elementos con accesskey="C" que contengan texto relacionado con cancelar.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_PAGINA_INICIO_OB08['button_cancelar_inicial_accesskey']):
                self.mostrar("✅ Click exitoso en botón Cancelar por accesskey")
                return True

            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_PAGINA_INICIO_OB08['button_cancelar_inicial_accesskey_alt']):
                self.mostrar("✅ Click exitoso en elemento con accesskey C")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por accesskey: {str(e)}", True)
            return False

    def _click_cancelar_inicial_por_titulo(self) -> bool:
        """
        Intenta hacer click en el botón Cancelar por su título (menú inicial).
        
        Busca elementos que contengan "Cancelar" en su título o texto.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_PAGINA_INICIO_OB08['button_cancelar_inicial_titulo']):
                self.mostrar("✅ Click exitoso en botón Cancelar por título")
                return True

            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_PAGINA_INICIO_OB08['button_cancelar_inicial_texto']):
                self.mostrar("✅ Click exitoso en texto Cancelar")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por título: {str(e)}", True)
            return False
    
    def guardar(self) -> None:
        """
        Guarda los cambios realizados en la transacción OB08 con estrategias múltiples.
        
        Implementa múltiples estrategias para garantizar que el guardado funcione
        tanto en entornos con GUI activo como en VMs sin sesión interactiva:
        
        1. Ctrl+S (método preferido cuando GUI está activo)
        2. Click directo en el botón "Guardar" via Selenium
        3. Click por accesskey (G) via Selenium
        4. Click por título via Selenium
        
        ---
        Se utiliza dentro del método `ingresar_tipo_de_cambio()` después de pegar datos.
        Implementa verificación de GUI y fallback automático a métodos Selenium.
        
        ---
        ### Ejemplo
        ```python
        # Después de pegar datos en SAP
        ob08.guardar()
        
        # Verificar resultado con alerta
        alerta = ob08._alerta_transaccion()
        if alerta == "Los datos han sido grabados":
            print("✅ Guardado exitoso")
        ```
        >>> None  # Si el guardado se ejecuta correctamente
        
        ---
        ### Raises
        #### Exception
        - Si no se puede guardar con ninguna de las estrategias disponibles
        - Si el elemento de guardado no se encuentra en ningún iframe
        """
        self.mostrar("💾 Guardando cambios en la transacción OB08")
        
        # Estrategia 1: Click directo en botón Guardar por ID (método preferido)
        if self._click_guardar_por_id():
            self.mostrar("✅ Guardado exitoso via click directo en botón")
            self.demora()
            return
            
        # Estrategia 2: Click por accesskey "G"
        if self._click_guardar_por_accesskey():
            self.mostrar("✅ Guardado exitoso via accesskey")
            self.demora()
            return
            
        # Estrategia 3: Click por título "Guardar (Ctrl+S)"
        if self._click_guardar_por_titulo():
            self.mostrar("✅ Guardado exitoso via título")
            self.demora()
            return
        
        # Estrategia 4: Ctrl+S (fallback para casos específicos)
        try:
            if self._verificar_sesion_gui_activa():
                self.mostrar("⌨️ Usando Ctrl+S como fallback")
                self.enviar_tecla_ventana('CTRL', 'S')
                self.demora()
                return
        except Exception as e:
            self.mostrar(f"⚠️ Ctrl+S falló: {str(e)}", True)
            
        # Si todas las estrategias fallan
        self.mostrar("❌ No se pudo guardar con ninguna estrategia", True)
        
        # Tomar screenshot para debugging
        try:
            self.tomar_screenshot("error_guardar_ob08")
            self.mostrar("📸 Screenshot guardado: error_guardar_ob08.png")
        except Exception:
            pass
            
        raise Exception(
            "FALLO CRÍTICO: No se pudo guardar en transacción OB08. "
            "Todas las estrategias fallaron: Ctrl+S, click directo, accesskey, título. "
            "Posibles causas: 1) Interfaz SAP cambió, 2) Elemento no disponible, "
            "3) Problema de permisos, 4) Sesión SAP expirada."
        )

    def _click_guardar_por_id(self) -> bool:
        """
        Intenta hacer click en el botón Guardar por su ID específico.
        
        Busca el elemento con ID que contiene "btn[11]" y datos de guardado.
        Utiliza búsqueda en todos los iframes para manejar la estructura de SAP.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['input_guardar_id']):
                self.mostrar("✅ Click exitoso en botón Guardar por ID")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por ID: {str(e)}", True)
            return False

    def _click_guardar_por_accesskey(self) -> bool:
        """
        Intenta hacer click en el botón Guardar por su accesskey "G".
        
        Busca elementos con accesskey="G" que contengan texto relacionado con guardar.
        """
        try:
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['input_guardar_accesskey']):
                self.mostrar("✅ Click exitoso en botón Guardar por accesskey")
                return True

            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['input_guardar_accesskey_alt']):
                self.mostrar("✅ Click exitoso en elemento con accesskey G")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por accesskey: {str(e)}", True)
            return False

    def _click_guardar_por_titulo(self) -> bool:
        """
        Intenta hacer click en el botón Guardar por su título.
        
        Busca elementos que contengan "Guardar" en su título o texto.
        """
        try:
            
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['input_guardar_titulo']):
                self.mostrar("✅ Click exitoso en botón Guardar por título")
                return True

            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['input_guardar_texto']):
                self.mostrar("✅ Click exitoso en texto Guardar")
                return True
                
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error en click por título: {str(e)}", True)
            return False
        
    def entradas_nuevas(self) -> bool:
        """
        Accede a la página de entradas nuevas con múltiples estrategias de reintento.
        
        Retorna True si se accede correctamente, False si falla.
        Si falla después de varios intentos, lanza una excepción crítica.
        
        ---
        Esta función implementa un enfoque robusto para acceder a la página de "Entradas nuevas" en OB08.
        Utiliza múltiples estrategias de reintento para manejar posibles fallos de navegación.
        Estrategias:
        1. Click directo en el elemento HTML (ideal para máquinas virtuales).
        2. Presionar F5 simple.
        3. Presionar F5 con una demora extendida.
        4. Doble F5.
        5. Presionar Enter seguido de F5.
        6. Click en el elemento + F5 como último recurso.
        
        Si todas las estrategias fallan, toma un screenshot de debugging y lanza una excepción crítica.
        
        ---
        ### Ejemplo
        ```python
        try:
            ob08.entradas_nuevas()
        except Exception as e:
            print(f"Error al acceder a entradas nuevas: {str(e)}")
        ```    
        >>> True  # Si se accede correctamente a la página de entradas nuevas
            
        ---
        ### Raises
        #### Exceptions
        - Exception: Si no se puede acceder a la página de entradas nuevas después de varios intentos.
        """
        if not self.driver:
            raise Exception("Driver no inicializado. Asegúrate de pasar un WebDriver válido al crear la instancia de OB08.")        
        
        nuevo_titulo_pagina = 'Entradas nuevas: Resumen de entradas añadidas'
        max_intentos = 3
        
        if self.driver.title != self.titulo_pagina_inicio:
            self.mostrar("❌ No se está en la página principal de OB08", True)
            raise Exception(f"Error crítico: No se está en la página principal de OB08. Título actual: '{self.driver.title}'. Se esperaba: '{self.titulo_pagina_inicio}'")
            
        for intento in range(max_intentos):
            
            # Estrategias múltiples para acceder al submenú
            if intento == 0:
                # Estrategia 1: Click directo en el elemento HTML (ideal para máquinas virtuales)
                if not self._click_entradas_nuevas_elemento(): continue
            elif intento == 1:
                # Estrategia 2: F5 simple
                self.enviar_tecla_ventana('F5')
            elif intento == 2:
                # Estrategia 3: F5 con demora adicional
                self.demora(2)
                self.enviar_tecla_ventana('F5')
            elif intento == 3:
                # Estrategia 4: Doble F5
                self.enviar_tecla_ventana('F5')
                self.demora(1)
                self.enviar_tecla_ventana('F5')
            
            # Esperar y verificar el cambio de página
            reintentos_titulo = 0
            titulo_actual = self.driver.title
            
            while titulo_actual != nuevo_titulo_pagina and reintentos_titulo < 4:
                self.demora(1)
                reintentos_titulo += 1
                titulo_actual = self.driver.title
                
            if titulo_actual == nuevo_titulo_pagina:
                self.mostrar("✅ Acceso exitoso a entradas nuevas")
                return True
                
            self.mostrar(f"❌ Intento {intento + 1} fallido. Título actual: '{titulo_actual}'")
            
            # Pequeña demora antes del siguiente intento
            if intento < max_intentos - 1:
                self.demora(2)
                
        # Intentar screenshot con manejo silencioso para entornos de producción
        try:
            self.tomar_screenshot()
        except Exception:
            # Error silencioso - screenshot no es crítico para la funcionalidad
            self.mostrar("⚠️ Screenshot no disponible en este entorno", True)
            
        self.mostrar("❌ No se pudo acceder a la página de entradas nuevas después de múltiples intentos", True)
        self.mostrar(f"🔍 Título actual final: '{self.driver.title}'", True)
        self.mostrar(f"🎯 Título esperado: '{nuevo_titulo_pagina}'", True)
        
        # CRÍTICO: Lanzar excepción para que el orquestador se entere del error
        error_msg = (
            f"FALLO CRÍTICO: No se pudo acceder al menú 'Entradas nuevas' en transacción OB08 "
            f"después de {max_intentos} intentos. "
            f"Todas las estrategias fallaron: Click directo, F5 simple, F5 extendido, doble F5, Enter+F5, TAB+F5. "
            f"Posibles causas: "
            f"1) SAP no responde correctamente, "
            f"2) Interfaz de SAP cambió, "
            f"3) Problema de permisos de usuario, "
            f"4) Sesión SAP expirada."
        )
        
        raise Exception(error_msg)
    
    def _click_entradas_nuevas_elemento(self) -> bool:
        """ 
        Busca y hace click en el elemento 'Entradas nuevas' por múltiples métodos.
        Ideal para entornos de máquinas virtuales donde las teclas pueden no funcionar.
        Utiliza los métodos de Chrome para manejar correctamente los iframes de SAP.
        """
        try:
            
            # Método 1: Buscar por title dentro de iframes
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_PAGINA_INICIO_OB08['button_entradas_nuevas_por_titulo']):
                self.mostrar("✅ Click exitoso por title")
                return True
            
            # Método 2: Buscar por texto del span dentro de iframes
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_entradas_nuevas_por_span']):
                self.mostrar("✅ Click exitoso por texto")
                return True
            
            # Método 3: Buscar por accesskey="E"
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['button_entradas_nuevas_por_accesskey']):
                self.mostrar("✅ Click exitoso por accesskey")
                return True
                
            self.mostrar("❌ No se pudo encontrar el elemento 'Entradas nuevas' en ningún iframe")
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error al buscar elemento 'Entradas nuevas': {str(e)}", True)
            return False
    
    # Métodos de formato de datos
    def formato_fecha_cotizacion(self, formato: str = '%d/%m/%Y') -> str:
        """ Siempre es la fecha de ayer. Para el formato de entrada se debe usar '%d%m%Y' """
        fecha = datetime.now() - timedelta(days=1)
        return fecha.strftime(formato)
    
    def formato_divisa(self, valor_divisa: float|str) -> str:
        """ Formatea la divisa para que sea compatible con SAP. """
        if isinstance(valor_divisa, str):
            valor_divisa = valor_divisa.replace('.', '').replace(',', '.')
            valor_divisa = float(valor_divisa)
            
        return f"{valor_divisa:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def formato_tipo_cotizacion(self, tipo: str) -> str:
        """ Formatea el tipo de cotización para que sea compatible con SAP """
        if tipo.lower() == 'compra':
            return 'G'
        elif tipo.lower() == 'venta':
            return 'B'
        else:
            raise ValueError("Tipo de cotización no válido. Debe ser 'compra' o 'venta'.")
    
    def formato_moneda(self, moneda: str) -> str:
        """ Formatea la moneda para que sea compatible con SAP """
        mapeo = {
            'Dolar U.S.A': 'USD',
            'Euro': 'EUR',
            'Dolar Australia': 'AUD',
            'Dolar Canadá': 'CAD',
            'Dolar Nueva Zelanda': 'NZD',
            'Libra Esterlina': 'GBP',
            'YENES': 'JPY',
            'Real Brasileño': 'BRL',
            'Peso Chileno': 'CLP',
            'Yuan': 'CNY',
            # Agrega más monedas según sea necesario
        }
        return mapeo.get(moneda, moneda.upper())
    
    # Métodos de entradas de datos
    def ingresar_tipo_de_cambio(self, df_divisas: pd.DataFrame) -> bool:
        """ 
        Ingresa una nueva cotización en la tabla especificada usando una estrategia robusta de pegado.
        
        Implementa 3 estrategias de pegado para entornos con GUI oculto:
        1. pywinauto (método original) - para entornos estándar
        2. Selenium con Ctrl+V - para casos donde pywinauto falla
        3. Pegado directo al elemento - para máximas garantías en VMs
        
        Args:
            df_divisas (pd.DataFrame): DataFrame con datos de divisas del BNA
        
        Raises:
            Error: Si no se puede acceder al menú 'Entradas nuevas'
            ValueError: Si ya existe una entrada con la misma clave.
            ValueError: Si no se puede ingresar el tipo de cambio en general.
            
        Returns:
            bool: True si el tipo de cambio se ingresó correctamente
        """
        self.mostrar("🔄 Preparando datos para SAP")
        df_divisas = self.__armar_tabla_para_sap(df_divisas)
        tabla = self.__convertir_tabla_sap_a_string(df_divisas)
        
        self.copiar_al_portapapeles(tabla)
        
        # Estrategia robusta de pegado con múltiples métodos
        if not self._pegar_datos_con_estrategia_robusta(tabla):
            self.mostrar("❌ No se pudo pegar los datos con ninguna estrategia", True)
            raise ValueError("Falló el pegado de datos en SAP")
        
        self.guardar()
        
        alerta = self._alerta_transaccion()
        if alerta == "Los datos han sido grabados":
            self.mostrar("✅ Tipo de cambio ingresado correctamente")
            self.finalizar()
            return True
        elif alerta == 'Ya existe una entrada con la misma clave':
            self.mostrar("😣 "+alerta, True)
            # Omitir
            # Cancelar
            # Cancelar
            # Fin Actualización > No
            self.enviar_tecla_ventana('ESC')
            self.enviar_tecla_ventana('SHIFT', 'TAB')
            self.enviar_tecla_ventana('ENTER')
            self.enviar_tecla_ventana('SHIFT', 'F3')
            raise ValueError(f"Ya existe una entrada con la misma clave: {alerta}")
            
        else:
            self.mostrar("❌ "+alerta, True)
            # Cancelar Entradas nuevas
            # Cancelar actualización
            # Cancelar Entradas nuevas
            # Cancelar OB08
            self.enviar_tecla_ventana('ESC')
            self.enviar_tecla_ventana('SHIFT', 'TAB')
            self.enviar_tecla_ventana('ENTER')
            self.enviar_tecla_ventana('ESC')
            self.enviar_tecla_ventana('ESC')
            self.enviar_tecla_ventana('ESC')
            self.enviar_tecla_ventana('ESC')
            
        raise ValueError(f"No se pudo ingresar el tipo de cambio. {alerta}")

    def __armar_tabla_para_sap(self, df_divisas: pd.DataFrame) -> pd.DataFrame:
        """ 
        Convierte una tabla de divisas entregada por el BNA en una tabla de divisas permitida por SAP. 
        
        El DataFrame de entrada debe tener las columnas: ``fecha``  ``compra`` ``venta``
        y las filas deben contener los valores de las divisas a ingresar.
        
        Ejemplo:
        ----
        
        | 24-06-2025  | compra  | venta   |
        |-------------|---------|---------|
        | Dolar USA   | 100.00  | 105.00  |
        | Euro        | 101.00  | 106.00  |

        Salida:
        ----
        | T... | Válido de | Cotiz.ind. | X | Factor (de) | De  | = | Cotiz.di. | X | Factor (a) | A   |
        |------|-----------|------------|---|-------------|-----|---|-----------|---|------------|-----|
        | B    | 24062025  |            |   |             | USD |   | 100,0000  |   |            | ARS |
        | G    | 24062025  |            |   |             | USD |   | 105,0000  |   |            | ARS |
        | B    | 24062025  |            |   |             | EUR |   | 101,0000  |   |            | ARS |
        | G    | 24062025  |            |   |             | EUR |   | 106,0000  |   |            | ARS |
        """
        self.mostrar("🔄 Armando tabla para SAP")
        
        # Copia el DataFrame para evitar modificar el original
        df = df_divisas.copy()
        
        # Renombrar las columnas del DataFrame
        df = df.rename(
            columns={
            df.columns[0]: 'moneda', 
            df.columns[1]: 'compra', 
            df.columns[2]: 'venta'
            }
        )
        
        # Transformar el DataFrame a formato largo (melt)
        df_melt = df.melt(
            id_vars=['moneda'], 
            value_vars=['compra', 'venta'],
            var_name='TCot - Tipo de Cotización', 
            value_name='T/C Cotizado directamente'
        )
        df_melt['TCot - Tipo de Cotización'] = df_melt['TCot - Tipo de Cotización'].apply(self.formato_tipo_cotizacion)
        df_melt['T/C Cotizado directamente'] = df_melt['T/C Cotizado directamente'].apply(self.formato_divisa)
        
        # Agregar columnas adicionales
        df_melt['Válido de'] = self.formato_fecha_cotizacion('%d%m%Y')
        df_melt['Moneda procedencia'] = df_melt['moneda'].apply(self.formato_moneda)
        df_melt['Moneda de destino'] = 'ARS'
        # Columnas adicionales para SAP, no se usan
        df_melt['T/C cotizado indirectamente'] = None
        df_melt['X'] = None
        df_melt['Factor (de)'] = None
        df_melt['='] = None
        df_melt['XX'] = None
        df_melt['Factor (a)'] = None
        
        # Seleccionar columnas para SAP
        columnas_sap = [
            'TCot - Tipo de Cotización', 
            'Válido de', 
            'T/C cotizado indirectamente', 
            'X', 
            'Factor (de)', 
            'Moneda procedencia', 
            '=', 
            'T/C Cotizado directamente',
            'XX', 
            'Factor (a)',
            'Moneda de destino', 
        ]
        df_sap = df_melt[columnas_sap]

        # Duplicar filas donde el tipo de cotización es 'B' y cambiar a 'M'
        mask_b = df_sap['TCot - Tipo de Cotización'] == 'B'
        df_b = df_sap[mask_b].copy()
        df_b['TCot - Tipo de Cotización'] = 'M'
        
        # Concatenar el DataFrame original con los duplicados
        df_sap = pd.concat([df_sap, df_b], ignore_index=True)
        df_sap = df_sap.sort_values(by=['Moneda procedencia', 'TCot - Tipo de Cotización']).reset_index(drop=True)

        return df_sap
    
    def __convertir_tabla_sap_a_string(self, df_divisas: pd.DataFrame) -> str:
        """ 
        Convierte la tabla de SAP a un formato de texto plano. 
        
        El separador es tabulador y el terminador de línea es salto de línea.
        """
        self.mostrar("📄 Convirtiendo tabla SAP a string")
        tabla_str = df_divisas.to_csv(sep='\t', index=False, header=False, lineterminator='\t\t')
        return tabla_str

    def _pegar_datos_con_estrategia_robusta(self, tabla: str) -> bool:
        """
        Implementa una estrategia robusta de pegado de datos con 3 métodos:
        1. Selenium con Ctrl+V
        2. Pegado directo al elemento específico de SAP
        3. pywinauto (método original)
        
        ---
        ### Ejemplo
        ```python
        if not ob08._pegar_datos_con_estrategia_robusta(tabla):
            print("No se pudo pegar los datos con ninguna estrategia")
        ```
        ---
        ### Exception
        Si todas las estrategias fallan, toma un screenshot de debugging y lanza una excepción.
        
        """
        self.mostrar("🎯 Iniciando estrategia robusta de pegado")
        
        # Estrategia 1: Pegado directo al elemento específico
        try:
            if self._pegar_directo_elemento_sap(tabla):
                self.mostrar("✅ Estrategia 1 exitosa: Pegado directo")
                return True
        except Exception as e:
            self.mostrar(f"❌ Estrategia 1 falló: {str(e)}", True)

        # Estrategia 2: Pegado por ctrl+v
        try:
            self.pegar_portapapeles_en_ventana_activa()
            if self._verificar_pegado_exitoso():
                self.mostrar("✅ Estrategia 2 exitosa: Pegado por ctrl+v")
                return True
        except Exception as e:
            self.mostrar(f"❌ Estrategia 2 falló: {str(e)}", True)

        # Si todas las estrategias fallaron, tomar screenshot para debugging
        self._tomar_screenshot_debug_pegado()
        
        self.mostrar("❌ Todas las estrategias de pegado fallaron", True)
        return False
    
    def _enfocar_tabla_sap(self) -> bool:
        """
        Hace click en la tabla de SAP para asegurar que tiene el foco.
        Utiliza los métodos robustos de Chrome para manejar iframes.
        
        Returns:
            bool: True si el click fue exitoso, False en caso contrario
        """
        try:
            elemento_input_xpath = '/html/body/table/tbody/tr/td/div/form/div/div[4]/div/div[1]/table/tbody[1]/tr[2]/td[2]/div/div[2]/table/tbody/tr[1]/td[1]/div/span/input'
            
            # Usar el método de Chrome para buscar y hacer click en todos los iframes
            if self.buscar_y_click_en_todos_los_iframes(By.XPATH, elemento_input_xpath):
                self.mostrar("🎯 Click realizado en tabla SAP")
                return True
            
            self.mostrar("❌ No se pudo hacer click en la tabla SAP")
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error al hacer click en tabla SAP: {str(e)}", True)
            return False
    
    def _pegar_directo_elemento_sap(self, tabla: str) -> bool:
        """
        Pega los datos directamente en el elemento específico de SAP.
        Utiliza los métodos de Chrome para manejar iframes y pegado de texto.
        
        Args:
            tabla (str): Los datos a pegar
            
        Returns:
            bool: True si el pegado fue exitoso, False en caso contrario
        """
        
        if not self.driver:
            raise Exception("Driver no inicializado. Asegúrate de pasar un WebDriver válido al crear la instancia de OB08.")

        try:
            # Estrategia 1: Intentar pegar tabla el elemento por XPath relativo
            input_element = self.buscar_elemento_en_iframes_sin_cerrar(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['input_XPath'], tiene_que_estar=False)
            if input_element:
                input_element.clear()
                input_element.send_keys(tabla)

                self.mostrar("📝 Datos pegados directamente en elemento SAP")
                # Volver al contenido principal usando método de Chrome
                try:
                    self.obtener_driver().switch_to.default_content()
                except:
                    pass
                return True
        except Exception as e:
            self.mostrar(f"❌ Error al pegar en elemento: {str(e)}", True)
            # Volver al contenido principal usando método de Chrome
            try:
                self.obtener_driver().switch_to.default_content()
            except:
                pass
            
        try:
            # Estrategia 2: Intentar pegar tabla el elemento por Full XPath
            input_element = self.buscar_elemento_en_iframes_sin_cerrar(By.XPATH, self.ELEMENTOS_ENTRADAS_NUEVAS['input_FullXPath'], tiene_que_estar=False)
            if input_element:
                input_element.clear()
                input_element.send_keys(tabla)
                self.mostrar("📝 Datos pegados directamente en elemento SAP por Full XPath")
                # Volver al contenido principal usando método de Chrome
                try:
                    self.obtener_driver().switch_to.default_content()
                except:
                    pass
                return True
            else:
                self.mostrar("❌ No se pudo pegar la tabla, porque no se encontró el iframe ni el input alternativo", True)
                # Volver al contenido principal usando método de Chrome
                try:
                    self.obtener_driver().switch_to.default_content()
                except:
                    pass
            
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error al pegar directo en elemento: {str(e)}", True)
            # Volver al contenido principal usando método de Chrome
            try:
                self.obtener_driver().switch_to.default_content()
            except:
                pass
            return False
    
    def _tomar_screenshot_debug_pegado(self) -> None:
        """
        Toma un screenshot para debugging cuando fallan todas las estrategias de pegado.
        Utiliza el método tomar_screenshot de Windows.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.tomar_screenshot(f"error_pegado_fallido_{timestamp}")
            self.mostrar(f"� Screenshot guardado: error_pegado_fallido_{timestamp}.png")
        except Exception as e:
            self.mostrar(f"❌ Error al tomar screenshot: {str(e)}", True)
    
    def _verificar_pegado_exitoso(self) -> bool:
        """
        Verifica si el pegado fue exitoso buscando contenido en la tabla de SAP.
        Utiliza los métodos de Chrome para manejar iframes correctamente.
        
        Returns:
            bool: True si hay contenido pegado, False en caso contrario
        """
        try:
            # Esperar un momento para que los datos se procesen
            time.sleep(0.5)
            
            # Configurar selectores para el iframe y elemento input
            elementos_xpath = {
                'iframe': '/html/body/div[3]/div/div/div/div/main/div/section/div/div/div[2]/div[3]/iframe',
                'input': '/html/body/table/tbody/tr/td/div/form/div/div[4]/div/div[1]/table/tbody[1]/tr[2]/td[2]/div/div[2]/table/tbody/tr[1]/td[1]/div/span/input',
                'input_alternativo': '//*[@id="M0:46:1[1,1]_c"]'
            }
            
            # Obtener el driver usando el método de Chrome
            driver = self.obtener_driver()
            
            # Cambiar al iframe usando método de Chrome
            iframe = self.encontrar_elemento(By.XPATH, elementos_xpath['iframe'], tiene_que_estar=False)
            if iframe:
                self.obtener_driver().switch_to.frame(iframe)
                
                # Buscar el elemento input
                input_element = self.encontrar_elemento(By.XPATH, elementos_xpath['input'], tiene_que_estar=False)
                if input_element:
                    # Verificar si hay contenido en el input
                    valor = input_element.get_attribute('value')
                    self.obtener_driver().switch_to.default_content()  # Volver al contenido principal
                    
                    if valor and valor.strip():
                        self.mostrar(f"🔍 Contenido detectado en input: {valor[:50]}...")
                        return True
                    else:
                        self.mostrar("🔍 No se detectó contenido en el input")
                        return False
                    
                else:
                    # Intentar con el input alternativo
                    input_element = self.encontrar_elemento(By.XPATH, elementos_xpath['input_alternativo'], tiene_que_estar=False)
                    if input_element:
                        valor = input_element.get_attribute('value')
                        self.obtener_driver().switch_to.default_content()
                
                self.obtener_driver().switch_to.default_content()  # Volver al contenido principal
            
            return False
            
        except Exception as e:
            # Asegurar que volvamos al contenido principal en caso de error
            try:
                self.obtener_driver().switch_to.default_content()
            except:
                pass
            self.mostrar(f"❌ Error al verificar pegado: {str(e)}", True)
            return False

    
    # Métodos de alerta de transacción
    def _alerta_transaccion(self) -> str:
        """ Obtiene el texto de la alerta de transacción """
        self.mostrar("🔍 Obteniendo alerta de transacción")
        span_alerta, texto_alerta = self.buscar_elemento_en_iframes(By.CLASS_NAME, 'lsMessageBar')
        
        if span_alerta and texto_alerta:
            self.mostrar(f"✅ Alerta encontrada")
            return texto_alerta.strip().split('\n')[0]
        
        self.mostrar("❌ No se encontró alerta de transacción", True)
        return ""
    
    # Métodos para detectar y manejar cuadros de diálogo modales
    def detectar_dialogo_modal(self) -> dict:
        """
        Detecta si hay un cuadro de diálogo modal presente en la pantalla.
        
        Busca específicamente los diálogos de "Cancelar actualización" y "Fin actualización"
        que pueden aparecer durante las operaciones en OB08.
        
        ---
        Se utiliza para detectar automáticamente la presencia de diálogos modales
        y extraer información sobre los botones disponibles para interactuar.
        
        ---
        ### Ejemplo
        ```python
        # Detectar si hay algún diálogo modal
        dialogo_info = ob08.detectar_dialogo_modal()
        
        if dialogo_info['presente']:
            print(f"Diálogo detectado: {dialogo_info['tipo']}")
            print(f"Botones disponibles: {dialogo_info['botones']}")
        ```
        >>> {
        >>>     'presente': True,
        >>>     'tipo': 'cancelar_actualizacion',
        >>>     'titulo': 'Cancelar actualización',
        >>>     'texto_principal': 'Se perderán las entradas',
        >>>     'texto_pregunta': '¿Realmente desea cancelar?',
        >>>     'botones': ['si', 'no']
        >>> }
        
        ---
        ### Returns
        #### dict
        - presente (bool): Si hay un diálogo modal presente
        - tipo (str): Tipo de diálogo ('cancelar_actualizacion', 'fin_actualizacion', o None)
        - titulo (str): Título del diálogo
        - texto_principal (str): Texto principal del diálogo
        - texto_pregunta (str): Pregunta del diálogo
        - botones (list): Lista de botones disponibles
        """
        self.mostrar("🔍 Detectando cuadros de diálogo modales")
        
        resultado = {
            'presente': False,
            'tipo': None,
            'titulo': '',
            'texto_principal': '',
            'texto_pregunta': '',
            'botones': []
        }
        
        try:
            # Buscar diálogo de "Cancelar actualización"
            dialogo_cancelar = self._detectar_dialogo_cancelar_actualizacion()
            if dialogo_cancelar['presente']:
                resultado.update(dialogo_cancelar)
                self.mostrar(f"✅ Diálogo detectado: {resultado['tipo']}")
                return resultado
            
            # Buscar diálogo de "Fin actualización"
            dialogo_fin = self._detectar_dialogo_fin_actualizacion()
            if dialogo_fin['presente']:
                resultado.update(dialogo_fin)
                self.mostrar(f"✅ Diálogo detectado: {resultado['tipo']}")
                return resultado
            
            self.mostrar("ℹ️ No se detectaron diálogos modales")
            return resultado
            
        except Exception as e:
            self.mostrar(f"❌ Error al detectar diálogos: {str(e)}", True)
            return resultado

    def _detectar_dialogo_cancelar_actualizacion(self) -> dict:
        """
        Detecta específicamente el diálogo de "Cancelar actualización".
        
        Busca el contenedor del diálogo y extrae información sobre los botones disponibles.
        """
        try:
            dialogo_config = self.ELEMENTOS_DIALOGOS_MODALES['dialogo_cancelar_actualizacion']
            
            # Buscar el contenedor del diálogo usando métodos de Chrome
            container_found = False
            
            # Obtener todos los iframes usando método de Chrome
            iframes = self.encontrar_elementos(By.TAG_NAME, "iframe", tiene_que_estar=False)
            if iframes:
                for iframe in iframes:
                    try:
                        self.obtener_driver().switch_to.frame(iframe)
                        container = self.encontrar_elemento(By.XPATH, dialogo_config['container'], tiene_que_estar=False)
                        if container:
                            container_found = True
                            break
                    except:
                        continue
                    finally:
                        self.obtener_driver().switch_to.default_content()
            
            if not container_found:
                # Buscar en el documento principal usando método de Chrome
                container = self.encontrar_elemento(By.XPATH, dialogo_config['container'], tiene_que_estar=False)
                if container:
                    container_found = True
            
            if container_found:
                # Verificar botones disponibles
                botones_disponibles = []
                
                # Verificar botón Sí
                if self._verificar_boton_dialogo(dialogo_config['boton_si_id'], dialogo_config['boton_si_accesskey'], dialogo_config['boton_si_texto']):
                    botones_disponibles.append('si')
                
                # Verificar botón No
                if self._verificar_boton_dialogo(dialogo_config['boton_no_id'], dialogo_config['boton_no_accesskey'], dialogo_config['boton_no_texto']):
                    botones_disponibles.append('no')
                
                return {
                    'presente': True,
                    'tipo': 'cancelar_actualizacion',
                    'titulo': dialogo_config['titulo'],
                    'texto_principal': dialogo_config['texto_principal'],
                    'texto_pregunta': dialogo_config['texto_pregunta'],
                    'botones': botones_disponibles
                }
            
            return {'presente': False}
            
        except Exception as e:
            self.mostrar(f"❌ Error al detectar diálogo cancelar actualización: {str(e)}", True)
            return {'presente': False}

    def _detectar_dialogo_fin_actualizacion(self) -> dict:
        """
        Detecta específicamente el diálogo de "Fin actualización".
        
        Busca el contenedor del diálogo y extrae información sobre los botones disponibles.
        """
        try:
            dialogo_config = self.ELEMENTOS_DIALOGOS_MODALES['dialogo_fin_actualizacion']
            
            # Buscar el contenedor del diálogo usando métodos de Chrome
            container_found = False
            
            # Obtener todos los iframes usando método de Chrome
            iframes = self.encontrar_elementos(By.TAG_NAME, "iframe", tiene_que_estar=False)
            if iframes:
                for iframe in iframes:
                    try:
                        self.obtener_driver().switch_to.frame(iframe)
                        container = self.encontrar_elemento(By.XPATH, dialogo_config['container'], tiene_que_estar=False)
                        if container:
                            container_found = True
                            break
                    except:
                        continue
                    finally:
                        self.obtener_driver().switch_to.default_content()
            
            if not container_found:
                # Buscar en el documento principal usando método de Chrome
                container = self.encontrar_elemento(By.XPATH, dialogo_config['container'], tiene_que_estar=False)
                if container:
                    container_found = True
            
            if container_found:
                # Verificar botones disponibles
                botones_disponibles = []
                
                # Verificar botón Sí
                if self._verificar_boton_dialogo(dialogo_config['boton_si_id'], dialogo_config['boton_si_accesskey'], dialogo_config['boton_si_texto']):
                    botones_disponibles.append('si')
                
                # Verificar botón No
                if self._verificar_boton_dialogo(dialogo_config['boton_no_id'], dialogo_config['boton_no_accesskey'], dialogo_config['boton_no_texto']):
                    botones_disponibles.append('no')
                
                # Verificar botón Cancelar (específico de fin actualización)
                if self._verificar_boton_dialogo(dialogo_config['boton_cancelar_id'], dialogo_config['boton_cancelar_accesskey'], dialogo_config['boton_cancelar_texto']):
                    botones_disponibles.append('cancelar')
                
                return {
                    'presente': True,
                    'tipo': 'fin_actualizacion',
                    'titulo': dialogo_config['titulo'],
                    'texto_principal': dialogo_config['texto_principal'],
                    'texto_pregunta': dialogo_config['texto_pregunta'],
                    'botones': botones_disponibles
                }
            
            return {'presente': False}
            
        except Exception as e:
            self.mostrar(f"❌ Error al detectar diálogo fin actualización: {str(e)}", True)
            return {'presente': False}

    def _verificar_boton_dialogo(self, xpath_id: str, xpath_accesskey: str, xpath_texto: str) -> bool:
        """
        Verifica si un botón específico del diálogo está presente y accesible.
        
        Utiliza múltiples estrategias para localizar el botón.
        """
        try:
            # Estrategia 1: Buscar por ID
            if self._buscar_elemento_dialogo(xpath_id):
                return True
            
            # Estrategia 2: Buscar por accesskey
            if self._buscar_elemento_dialogo(xpath_accesskey):
                return True
            
            # Estrategia 3: Buscar por texto
            if self._buscar_elemento_dialogo(xpath_texto):
                return True
            
            return False
            
        except Exception:
            return False

    def _buscar_elemento_dialogo(self, xpath: str) -> bool:
        """
        Busca un elemento específico del diálogo en todos los contextos disponibles.
        """
        try:
            # Buscar en el documento principal usando método de Chrome
            elemento = self.encontrar_elemento(By.XPATH, xpath, tiene_que_estar=False)
            if elemento and elemento.is_displayed():
                return True
            
            # Buscar en todos los iframes usando métodos de Chrome
            iframes = self.encontrar_elementos(By.TAG_NAME, "iframe", tiene_que_estar=False)
            if iframes:
                for iframe in iframes:
                    try:
                        self.obtener_driver().switch_to.frame(iframe)
                        elemento = self.encontrar_elemento(By.XPATH, xpath, tiene_que_estar=False)
                        if elemento and elemento.is_displayed():
                            return True
                    except:
                        continue
                    finally:
                        self.obtener_driver().switch_to.default_content()
            
            return False
            
        except Exception:
            return False

    def interactuar_dialogo_modal(self, accion: str) -> bool:
        """
        Interactúa con un cuadro de diálogo modal presente.
        
        Permite hacer click en los botones disponibles del diálogo detectado.
        
        ---
        Se utiliza para responder automáticamente a los diálogos modales
        que aparecen durante las operaciones en OB08.
        
        ---
        ### Ejemplo
        ```python
        # Detectar diálogo y responder "Sí"
        dialogo_info = ob08.detectar_dialogo_modal()
        if dialogo_info['presente']:
            exito = ob08.interactuar_dialogo_modal('si')
            if exito:
                print("✅ Diálogo respondido exitosamente")
        ```
        
        ---
        ### Parameters
        #### accion : str
        - 'si': Hacer click en el botón "Sí"
        - 'no': Hacer click en el botón "No"  
        - 'cancelar': Hacer click en el botón "Cancelar" (solo en fin_actualizacion)
        
        ### Returns
        #### bool
        - True si la interacción fue exitosa
        - False si falló o el botón no está disponible
        
        ---
        ### Raises
        #### ValueError
        - Si la acción especificada no es válida
        #### Exception
        - Si ocurre un error durante la interacción
        """
        if accion not in ['si', 'no', 'cancelar']:
            raise ValueError(f"Acción inválida: {accion}. Debe ser 'si', 'no' o 'cancelar'")
        
        self.mostrar(f"🎯 Interactuando con diálogo modal: {accion}")
        
        try:
            # Detectar qué diálogo está presente
            dialogo_info = self.detectar_dialogo_modal()
            
            if not dialogo_info['presente']:
                self.mostrar("❌ No se detectó ningún diálogo modal", True)
                return False
            
            if accion not in dialogo_info['botones']:
                self.mostrar(f"❌ Botón '{accion}' no disponible en diálogo {dialogo_info['tipo']}", True)
                return False
            
            # Obtener configuración del diálogo
            dialogo_config = self.ELEMENTOS_DIALOGOS_MODALES[f"dialogo_{dialogo_info['tipo']}"]
            
            # Determinar qué botón hacer click según la acción
            if accion == 'si':
                xpaths = [dialogo_config['boton_si_id'], dialogo_config['boton_si_accesskey'], dialogo_config['boton_si_texto']]
            elif accion == 'no':
                xpaths = [dialogo_config['boton_no_id'], dialogo_config['boton_no_accesskey'], dialogo_config['boton_no_texto']]
            elif accion == 'cancelar':
                if 'boton_cancelar_id' in dialogo_config:
                    xpaths = [dialogo_config['boton_cancelar_id'], dialogo_config['boton_cancelar_accesskey'], dialogo_config['boton_cancelar_texto']]
                else:
                    self.mostrar(f"❌ Botón cancelar no disponible en diálogo {dialogo_info['tipo']}", True)
                    return False
            
            # Intentar hacer click en el botón
            for xpath in xpaths:
                if self._click_boton_dialogo(xpath):
                    self.mostrar(f"✅ Click exitoso en botón '{accion}' del diálogo")
                    self.demora()
                    return True
            
            self.mostrar(f"❌ No se pudo hacer click en botón '{accion}'", True)
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error al interactuar con diálogo: {str(e)}", True)
            return False

    def _click_boton_dialogo(self, xpath: str) -> bool:
        """
        Hace click en un botón específico del diálogo modal.
        
        Busca el botón en todos los contextos disponibles y hace click si lo encuentra.
        """
        try:
            # Intentar en el documento principal usando método de Chrome
            elemento = self.encontrar_elemento(By.XPATH, xpath, tiene_que_estar=False)
            if elemento and elemento.is_displayed() and elemento.is_enabled():
                elemento.click()
                return True
            
            # Intentar en todos los iframes usando métodos de Chrome
            iframes = self.encontrar_elementos(By.TAG_NAME, "iframe", tiene_que_estar=False)
            if iframes:
                for iframe in iframes:
                    try:
                        self.obtener_driver().switch_to.frame(iframe)
                        elemento = self.encontrar_elemento(By.XPATH, xpath, tiene_que_estar=False)
                        if elemento and elemento.is_displayed() and elemento.is_enabled():
                            elemento.click()
                            return True
                    except:
                        continue
                    finally:
                        self.obtener_driver().switch_to.default_content()
            
            return False
            
        except Exception as e:
            self.mostrar(f"❌ Error al hacer click en botón diálogo: {str(e)}", True)
            return False
    
# TEST
if __name__ == "__main__":
    # Ejemplo de uso
    ob08 = OB08(
        #base_url='https://saplgdqa.losgrobo.com:44302/sap/bc/ui5_ui5/ui2/ushell/shells/abap', 
        base_url='https://saplg.losgrobo.com/sap/bc/ui2/flp?sap-client=300&sap-language=ES#Shell-home', 
        usuario_microsoft='prdusr@losgrobo.com',
        clave_microsoft='F87V<:?$lCkF1Cbx_d',
        usuario='PRDUSR',
        clave='Inicio.2025',
        driver=None, 
        dev=False
        )
    
    # DataFrame de ejemplo
    # data = {
    #     '24-06-2025': ['Dolar U.S.A', 'Euro'],
    #     'compra': [100.00, 101.00],
    #     'venta': [105.00, 106.00]
    # }
    data = {
        '24-06-2025': ['Yuan'],
        'compra': [100.00],
        'venta': [105.00]
    }
    df_divisas = pd.DataFrame(data)
    
    ob08.ingreso_a_sap()
    ob08.ir_a_transaccion('OB08')
    ob08.entradas_nuevas()
    
    # Ingresar tipo de cambio
    ob08.ingresar_tipo_de_cambio(df_divisas) 
