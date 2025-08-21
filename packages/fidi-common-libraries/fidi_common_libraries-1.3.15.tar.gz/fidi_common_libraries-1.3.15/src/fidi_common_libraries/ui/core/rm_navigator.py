"""
Navegador para aplicação TOTVS RM.

Fornece funcionalidades para navegação automática na interface do sistema RM,
incluindo navegação por abas, barras de ferramentas e botões.
"""

import logging
from typing import Tuple, Dict, Any, Optional
from pywinauto import Application
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.findwindows import ElementNotFoundError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIElementNotFoundError, UIInteractionError
from ..utils.screenshot import capture_screenshot_on_error
from .waits import UIWaits


logger = logging.getLogger(__name__)


class RMNavigator:
    """
    Navegador para aplicação TOTVS RM.
    
    Fornece métodos para navegação automática na interface do sistema RM,
    incluindo navegação por abas, barras de ferramentas e botões.
    """
    
    def __init__(self, app: Application, main_window: HwndWrapper):
        """
        Inicializa o navegador RM.
        
        Args:
            app: Instância da aplicação pywinauto.
            main_window: Janela principal da aplicação RM.
            
        Raises:
            ValueError: Se app ou main_window forem None.
        """
        if app is None:
            raise ValueError("Parâmetro 'app' não pode ser None")
        if main_window is None:
            raise ValueError("Parâmetro 'main_window' não pode ser None")
            
        self.app = app
        self.main_window = main_window
        self.config = get_ui_config()
        self.waits = UIWaits()

    def navigate_to_element(
        self,
        tab_item_criteria: Dict[str, Any],
        toolbar_criteria: Dict[str, Any],
        button_criteria: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Navega até um elemento específico na aplicação TOTVS RM.
        
        Executa navegação sequencial: aba -> barra de ferramentas -> botão.
        Utiliza estrutura padrão do RM: mdiRibbonControl -> Ribbon Tabs -> Lower Ribbon.

        Args:
            tab_item_criteria: Critérios para encontrar a aba do sistema RM.
                             Ex: {"title": "Encargos", "control_type": "TabItem"}
            toolbar_criteria: Critérios para encontrar o grupo/toolbar na aba.
                            Ex: {"title": "Contabilização", "control_type": "ToolBar"}
            button_criteria: Critérios para encontrar o botão no grupo.
                           Ex: {"title": "Geração dos Encargos", "control_type": "Button"}
                           
        Returns:
            Tuple[bool, Optional[str]]: 
                - (True, texto_do_botao) se navegação bem-sucedida
                - (False, None) se falhar
                
        Raises:
            UIElementNotFoundError: Se algum elemento não for encontrado.
            UIInteractionError: Se houver erro na interação com elementos.
            ValueError: Se critérios forem inválidos.
        """
        # Validação de parâmetros
        if not tab_item_criteria or not isinstance(tab_item_criteria, dict):
            raise ValueError("tab_item_criteria deve ser um dicionário não vazio")
        if not toolbar_criteria or not isinstance(toolbar_criteria, dict):
            raise ValueError("toolbar_criteria deve ser um dicionário não vazio")
        if not button_criteria or not isinstance(button_criteria, dict):
            raise ValueError("button_criteria deve ser um dicionário não vazio")
        
        try:
            logger.info("Iniciando navegação no sistema RM")
            
            # 1. Encontrar e clicar na aba (tab item)
            ribbon_control = self._get_ribbon_control()
            ribbon_tabs = self._get_ribbon_tabs(ribbon_control)
            
            tab_item = self._find_and_click_tab(ribbon_tabs, tab_item_criteria)
            logger.info(f"Aba selecionada: {tab_item.window_text()}")
            
            # 2. Encontrar toolbar no Lower Ribbon
            lower_ribbon = self._get_lower_ribbon(ribbon_control)
            tab_title = tab_item.window_text()
            toolbar = self._find_toolbar(lower_ribbon, toolbar_criteria, tab_title)
            logger.info(f"Toolbar encontrada: {toolbar.window_text()}")
            
            # 3. Encontrar e clicar no botão
            button = self._find_and_click_button(toolbar, button_criteria)
            button_text = button.window_text()
            logger.info(f"Botão clicado: {button_text}")
            
            logger.info("Navegação concluída com sucesso")
            return True, button_text
            
        except ElementNotFoundError as e:
            error_msg = f"Elemento não encontrado durante navegação: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_navigation_element_not_found")
            return False, None
            
        except Exception as e:
            error_msg = f"Erro durante navegação no sistema RM: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_navigation_failed")
            return False, None
    
    def _get_ribbon_control(self) -> HwndWrapper:
        """
        Obtém o controle ribbon principal.
        
        Returns:
            HwndWrapper: Controle ribbon principal.
            
        Raises:
            UIElementNotFoundError: Se o controle não for encontrado.
        """
        try:
            ribbon_control = self.main_window.child_window(
                auto_id="mdiRibbonControl", 
                control_type="Pane"
            )
            self.waits.wait_for_element_ready(ribbon_control)
            return ribbon_control
        except ElementNotFoundError as e:
            raise UIElementNotFoundError("Controle ribbon não encontrado", str(e))
    
    def _get_ribbon_tabs(self, ribbon_control: HwndWrapper) -> HwndWrapper:
        """
        Obtém o controle de abas do ribbon.
        
        Args:
            ribbon_control: Controle ribbon principal.
            
        Returns:
            HwndWrapper: Controle de abas.
            
        Raises:
            UIElementNotFoundError: Se o controle não for encontrado.
        """
        try:
            ribbon_tabs = ribbon_control.child_window(
                title="Ribbon Tabs",
                control_type="Tab"
            )
            self.waits.wait_for_element_ready(ribbon_tabs)
            return ribbon_tabs
        except ElementNotFoundError as e:
            raise UIElementNotFoundError("Ribbon Tabs não encontrado", str(e))
    
    def _get_lower_ribbon(self, ribbon_control: HwndWrapper) -> HwndWrapper:
        """
        Obtém o Lower Ribbon onde ficam as toolbars.
        
        Args:
            ribbon_control: Controle ribbon principal.
            
        Returns:
            HwndWrapper: Lower Ribbon.
            
        Raises:
            UIElementNotFoundError: Se o controle não for encontrado.
        """
        try:
            lower_ribbon = ribbon_control.child_window(
                title="Lower Ribbon",
                control_type="Pane"
            )
            self.waits.wait_for_element_ready(lower_ribbon)
            return lower_ribbon
        except ElementNotFoundError as e:
            raise UIElementNotFoundError("Lower Ribbon não encontrado", str(e))
    
    def _find_and_click_tab(
        self, 
        ribbon_tabs: HwndWrapper, 
        criteria: Dict[str, Any]
    ) -> HwndWrapper:
        """
        Encontra e clica em uma aba.
        
        Args:
            ribbon_tabs: Controle de abas.
            criteria: Critérios para encontrar a aba.
            
        Returns:
            HwndWrapper: Aba encontrada.
            
        Raises:
            UIElementNotFoundError: Se a aba não for encontrada.
            UIInteractionError: Se houver erro ao clicar.
        """
        try:
            tab_item = ribbon_tabs.child_window(**criteria)
            self.waits.wait_for_element_ready(tab_item)
            tab_item.draw_outline()
            tab_item.click_input()
            return tab_item
        except ElementNotFoundError as e:
            raise UIElementNotFoundError(f"Aba não encontrada com critérios {criteria}", str(e))
        except Exception as e:
            raise UIInteractionError(f"Erro ao clicar na aba", str(e))
    
    def _find_toolbar(
        self, 
        lower_ribbon: HwndWrapper, 
        criteria: Dict[str, Any],
        tab_title: str
    ) -> HwndWrapper:
        """
        Encontra uma toolbar no Lower Ribbon.
        
        Navega pela estrutura: Lower Ribbon -> Pane(tab_title) -> Toolbar
        
        Args:
            lower_ribbon: Lower Ribbon.
            criteria: Critérios para encontrar a toolbar.
            tab_title: Título da aba para encontrar o Pane intermediário.
            
        Returns:
            HwndWrapper: Toolbar encontrada.
            
        Raises:
            UIElementNotFoundError: Se a toolbar não for encontrada.
        """
        try:
            # Primeiro encontra o Pane intermediário com o título da aba
            tab_pane = lower_ribbon.child_window(
                title=tab_title,
                control_type="Pane"
            )
            self.waits.wait_for_element_ready(tab_pane)
            logger.debug(f"Pane da aba encontrado: {tab_pane.window_text()}")
            
            # Depois encontra a toolbar dentro do Pane
            toolbar = tab_pane.child_window(**criteria)
            self.waits.wait_for_element_ready(toolbar)
            toolbar.draw_outline()
            return toolbar
        except ElementNotFoundError as e:
            raise UIElementNotFoundError(f"Toolbar não encontrada com critérios {criteria} na aba '{tab_title}'", str(e))
    
    def _find_and_click_button(
        self, 
        toolbar: HwndWrapper, 
        criteria: Dict[str, Any]
    ) -> HwndWrapper:
        """
        Encontra e clica em um botão na toolbar.
        
        Args:
            toolbar: Toolbar onde buscar o botão.
            criteria: Critérios para encontrar o botão.
            
        Returns:
            HwndWrapper: Botão encontrado.
            
        Raises:
            UIElementNotFoundError: Se o botão não for encontrado.
            UIInteractionError: Se houver erro ao clicar.
        """
        try:
            button = toolbar.child_window(**criteria)
            self.waits.wait_for_element_ready(button)
            button.draw_outline()
            button.click_input()
            return button
        except ElementNotFoundError as e:
            raise UIElementNotFoundError(f"Botão não encontrado com critérios {criteria}", str(e))
        except Exception as e:
            raise UIInteractionError(f"Erro ao clicar no botão", str(e))


# Exemplo de uso
if __name__ == "__main__":
    """
    Exemplo de uso do RMNavigator.
    
    Este exemplo demonstra como usar o navegador para navegar
    até um elemento específico no sistema RM.
    """
    try:
        from pywinauto import Application
        
        # Conectar à aplicação RM
        app = Application(backend="uia").connect(path="RM.exe")
        main_window = app.window(
            title_re=".*TOTVS.*", 
            class_name="WindowsForms10.Window.8.app.0.31d2b0c_r9_ad1"
        )
        
        # Criar navegador
        navigator = RMNavigator(app, main_window)
        
        # Critérios de navegação
        tab_criteria = {"title": "Encargos", "control_type": "TabItem"}
        toolbar_criteria = {"title": "Contabilização", "control_type": "Pane"}
        button_criteria = {"title": "Geração dos Encargos", "control_type": "Button"}
        
        # Executar navegação
        success, button_text = navigator.navigate_to_element(
            tab_criteria, toolbar_criteria, button_criteria
        )
        
        if success:
            print(f"Navegação bem-sucedida. Botão clicado: {button_text}")
        else:
            print("Navegação falhou.")
            
    except Exception as e:
        print(f"Erro no exemplo: {e}")