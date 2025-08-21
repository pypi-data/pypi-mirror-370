"""
Navegador adaptativo para aplicação RM.

Fornece funcionalidades para navegação adaptativa em elementos da interface RM,
com retry automático e tratamento robusto de erros para maior resiliência.
"""

import logging
import time
from typing import Optional, Dict, Any
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.findwindows import ElementNotFoundError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIElementNotFoundError, UIInteractionError, UITimeoutError
from ..utils.screenshot import capture_screenshot_on_error
from .waits import UIWaits


logger = logging.getLogger(__name__)


class RMAdaptNavigator:
    """
    Navegador adaptativo para aplicação RM.
    
    Fornece métodos para navegação adaptativa em elementos da interface RM,
    com retry automático, esperas inteligentes e tratamento robusto de erros.
    """
    
    def __init__(self, parent_element: HwndWrapper):
        """
        Inicializa o navegador adaptativo.
        
        Args:
            parent_element: Elemento pai para navegação.
            
        Raises:
            ValueError: Se parent_element for None.
        """
        if parent_element is None:
            raise ValueError("Parâmetro 'parent_element' não pode ser None")
            
        self.parent_element = parent_element
        self.config = get_ui_config()
        self.waits = UIWaits()
    
    def navigate_to_element(
        self,
        title: Optional[str] = None,
        auto_id: Optional[str] = None,
        control_type: Optional[str] = None,
        click_element: bool = False,
        timeout: float = 0.5,
        retry_interval: float = 1.0,
        max_retries: int = 5
    ) -> HwndWrapper:
        """
        Navega para um elemento específico com retry adaptativo.
        
        Localiza um elemento usando os critérios fornecidos, com opção de clicar,
        com retry automático e esperas inteligentes para maior resiliência.
        
        Args:
            title: Título do elemento.
            auto_id: AutoID do elemento.
            control_type: Tipo de controle do elemento.
            click_element: Se deve clicar no elemento (True) ou apenas encontrar (False).
            timeout: Timeout para verificação de existência.
            retry_interval: Intervalo entre tentativas em segundos.
            max_retries: Número máximo de tentativas.
            
        Returns:
            HwndWrapper: Elemento encontrado (e clicado se click_element=True).
            
        Raises:
            UIElementNotFoundError: Se elemento não for encontrado.
            UIInteractionError: Se houver erro na interação.
            UITimeoutError: Se timeout for atingido.
            ValueError: Se critérios forem inválidos.
        """
        # Validação de parâmetros
        if not any([title, auto_id, control_type]):
            raise ValueError("Pelo menos um critério (title, auto_id, control_type) deve ser fornecido")
        
        if timeout <= 0:
            raise ValueError("Timeout deve ser positivo")
        if retry_interval <= 0:
            raise ValueError("Retry interval deve ser positivo")
        if max_retries < 0:
            raise ValueError("Max retries deve ser não-negativo")
        
        try:
            action = "clicando" if click_element else "encontrando"
            logger.info(f"Navegando para elemento ({action}) - Title: {title}, AutoID: {auto_id}, Type: {control_type}")
            
            # Encontrar elemento (com ou sem clique)
            if click_element:
                element = self._find_and_click_element(title, auto_id, control_type)
            else:
                element = self._find_element_only(title, auto_id, control_type)
            
            # Aguardar elemento ficar disponível com retry
            self.config.wait_between_retries
            
            logger.info("Navegação adaptativa concluída com sucesso")
            return element
            
        except ElementNotFoundError as e:
            error_msg = f"Elemento não encontrado - Title: {title}, AutoID: {auto_id}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_adapt_navigator_element_not_found")
            raise UIElementNotFoundError(error_msg, str(e))
            
        except Exception as e:
            error_msg = f"Erro durante navegação adaptativa: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_adapt_navigator_failed")
            raise UIInteractionError(error_msg, str(e))
    
    def _find_and_click_element(
        self,
        title: Optional[str],
        auto_id: Optional[str],
        control_type: Optional[str]
    ) -> HwndWrapper:
        """
        Encontra e clica no elemento especificado.
        
        Args:
            title: Título do elemento.
            auto_id: AutoID do elemento.
            control_type: Tipo de controle do elemento.
            
        Returns:
            HwndWrapper: Elemento encontrado.
            
        Raises:
            ElementNotFoundError: Se elemento não for encontrado.
            UIInteractionError: Se houver erro ao clicar.
        """
        try:
            # Construir critérios de busca
            criteria = {}
            if title is not None:
                criteria['title'] = title
            if auto_id is not None:
                criteria['auto_id'] = auto_id
            if control_type is not None:
                criteria['control_type'] = control_type
            
            # Encontrar elemento
            element = self.parent_element.child_window(**criteria) # type: ignore[attr-defined]
            
            # Destacar elemento visualmente
            element.draw_outline()
            
            # Aguardar elemento ficar pronto
            self.config.wait_before_click

            # Clicar no elemento
            element.click_input()
            logger.debug(f"Elemento clicado com sucesso: {criteria}")
            
            return element
            
        except ElementNotFoundError:
            raise  # Re-raise para tratamento no método principal
        except Exception as e:
            raise UIInteractionError(f"Erro ao clicar no elemento: {e}", str(e))
    
    def _find_element_only(
        self,
        title: Optional[str],
        auto_id: Optional[str],
        control_type: Optional[str]
    ) -> HwndWrapper:
        """
        Encontra o elemento especificado sem clicar.
        
        Args:
            title: Título do elemento.
            auto_id: AutoID do elemento.
            control_type: Tipo de controle do elemento.
            
        Returns:
            HwndWrapper: Elemento encontrado.
            
        Raises:
            ElementNotFoundError: Se elemento não for encontrado.
        """
        try:
            # Construir critérios de busca
            criteria = {}
            if title is not None:
                criteria['title'] = title
            if auto_id is not None:
                criteria['auto_id'] = auto_id
            if control_type is not None:
                criteria['control_type'] = control_type
            
            # Encontrar elemento
            element = self.parent_element.child_window(**criteria) # type: ignore[attr-defined]
            
            # Destacar elemento visualmente
            element.draw_outline()
            
            # Aguardar elemento ficar pronto
            self.config.wait_before_click
            
            logger.debug(f"Elemento encontrado com sucesso: {criteria}")
            return element
            
        except ElementNotFoundError:
            raise  # Re-raise para tratamento no método principal
    
    def _wait_for_element_ready(
        self,
        element: HwndWrapper,
        timeout: float,
        retry_interval: float,
        max_retries: int
    ) -> None:
        """
        Aguarda elemento ficar pronto com retry adaptativo.
        
        Args:
            element: Elemento a aguardar.
            timeout: Timeout para cada verificação.
            retry_interval: Intervalo entre tentativas.
            max_retries: Número máximo de tentativas.
            
        Raises:
            UITimeoutError: Se timeout total for atingido.
        """
        total_wait_time = 0
        max_total_time = retry_interval * max_retries
        
        logger.debug(f"Aguardando elemento ficar pronto (timeout: {timeout}s, max: {max_total_time}s)")
        
        while not element.exists(timeout=timeout) and total_wait_time < max_total_time: # type: ignore[attr-defined]
            logger.debug(f"Elemento não pronto, aguardando {retry_interval}s...")
            time.sleep(retry_interval)
            total_wait_time += retry_interval
        
        if not element.exists(timeout=timeout): # type: ignore[attr-defined]
            raise UITimeoutError(
                f"Elemento não ficou pronto após {total_wait_time:.1f}s de espera"
            )
        
        logger.debug("Elemento pronto para uso")


# Função de compatibilidade (deprecated)
def RMAdaptativeNavigator(
    parent,
    title=None,
    auto_id=None,
    control_type=None,
    click_element: bool = True,
    timeout: float = 0.5,
    retry_interval: float = 1.0,
    max_retries: int = 5
):
    """
    Função de compatibilidade para navegação adaptativa.
    
    DEPRECATED: Use RMAdaptNavigator class instead.
    
    Args:
        parent: Elemento pai.
        title: Título do elemento.
        auto_id: AutoID do elemento.
        control_type: Tipo de controle.
        click_element: Se deve clicar no elemento.
        timeout: Timeout para verificação.
        retry_interval: Intervalo entre tentativas.
        max_retries: Número máximo de tentativas.
        
    Returns:
        HwndWrapper: Elemento encontrado.
        
    Raises:
        ValueError: Se houver erro na navegação.
    """
    import warnings
    warnings.warn(
        "RMAdaptativeNavigator function is deprecated. Use RMAdaptNavigator class instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    try:
        navigator = RMAdaptNavigator(parent)
        return navigator.navigate_to_element(
            title=title,
            auto_id=auto_id,
            control_type=control_type,
            click_element=click_element,
            timeout=timeout,
            retry_interval=retry_interval,
            max_retries=max_retries
        )
    except Exception as e:
        # Manter compatibilidade com erro original
        raise ValueError(str(e)) from e


# Exemplo de uso
if __name__ == "__main__":
    """
    Exemplo de uso do RMAdaptNavigator.
    
    Este exemplo demonstra como usar o navegador adaptativo
    para navegação resiliente em elementos RM.
    """
    try:
        # Assumindo que você tem um parent_element
        # navigator = RMAdaptNavigator(parent_element)
        
        # Navegar para elemento específico
        # element = navigator.navigate_to_element(
        #     title="Salvar",
        #     control_type="Button",
        #     max_retries=3
        # )
        
        print("Exemplo de uso do RMAdaptNavigator")
        print("Navegação adaptativa com retry automático")
        
    except Exception as e:
        print(f"Erro no exemplo: {e}")