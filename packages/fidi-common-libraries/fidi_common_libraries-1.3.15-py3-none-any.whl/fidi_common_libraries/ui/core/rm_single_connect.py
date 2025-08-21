"""
Conector único para aplicação RM.

Fornece funcionalidades para conexão robusta com a aplicação RM,
incluindo retry automático, captura de screenshots e validação estrutural.
"""

import logging
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

import yaml
from pywinauto import Application, Desktop

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIConnectionError, UIElementNotFoundError
from ..utils.screenshot import capture_screenshot_on_error


logger = logging.getLogger(__name__)


class RMSingleConnect:
    """
    Conector único para aplicação RM.
    
    Realiza conexão robusta com a aplicação RM usando backend único,
    com funcionalidades enterprise como retry automático, screenshots
    e validação estrutural opcional.
    """
    
    def __init__(
        self,
        backend: str = "uia",
        screenshot_enabled: bool = False,
        screenshot_dir: Optional[str] = None,
        retries: int = 3,
        delay: float = 2.0,
        control_retry: int = 3,
        control_delay: float = 1.0
    ):
        """
        Inicializa o conector único.
        
        Args:
            backend: Backend de automação ("win32" ou "uia").
            screenshot_enabled: Se deve capturar screenshots das janelas.
            screenshot_dir: Diretório para salvar screenshots.
            retries: Número de tentativas de conexão global.
            delay: Delay entre tentativas de conexão (segundos).
            control_retry: Tentativas por controle/janela individual.
            control_delay: Delay entre tentativas de controle (segundos).
        """
        self.config = get_ui_config()
        self.backend = backend
        self.screenshot_enabled = screenshot_enabled
        self.retries = retries
        self.delay = delay
        self.control_retry = control_retry
        self.control_delay = control_delay
        
        # Configurar diretório de screenshots
        if screenshot_dir:
            self.screenshot_dir = Path(screenshot_dir)
        else:
            self.screenshot_dir = Path("screenshots")
        
        if screenshot_enabled:
            self.screenshot_dir.mkdir(exist_ok=True)
        
        # Estado da conexão
        self._app: Optional[Application] = None
        self._connected_windows: Dict[str, Dict[str, Any]] = {}
    
    def connect_single(
        self,
        titulos: Optional[List[str]] = None,
        classe: Optional[str] = None,
        pid: Optional[int] = None,
        yaml_expected: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Conecta no TOTVS RM com funcionalidades enterprise avançadas.
        
        Args:
            titulos: Lista de títulos para buscar janelas RM.
            classe: Nome da classe da janela para conexão.
            pid: Process ID específico para conexão direta.
            yaml_expected: Arquivo YAML para validação estrutural.
        
        Returns:
            Tuple[bool, Dict[str, Any]]:
                - (True, janelas_dict) se conexão bem-sucedida
                - (False, {}) se falhar
        
        Raises:
            UIConnectionError: Se não conseguir conectar após todas as tentativas.
        """
        try:
            logger.info("Iniciando conexão única com aplicação RM")
            
            # 1. Estabelecer conexão com retry
            success = self._establish_connection(titulos, classe, pid)
            if not success:
                return False, {}
            
            # 2. Capturar janelas
            self._capture_windows()
            
            # 3. Validação estrutural (opcional)
            if yaml_expected:
                self._validate_structure(yaml_expected)
            
            logger.info(f"Conexão única estabelecida com {len(self._connected_windows)} janelas")
            return True, self._connected_windows
            
        except Exception as e:
            error_msg = f"Erro durante conexão única: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_single_connect_failed")
            return False, {}
    
    def _establish_connection(
        self,
        titulos: Optional[List[str]],
        classe: Optional[str],
        pid: Optional[int]
    ) -> bool:
        """
        Estabelece conexão com retry automático.
        
        Args:
            titulos: Lista de títulos para buscar.
            classe: Classe da janela.
            pid: Process ID.
        
        Returns:
            bool: True se conexão bem-sucedida.
        """
        for attempt in range(1, self.retries + 1):
            try:
                logger.info(f"Tentativa {attempt}/{self.retries} para conectar RM")
                
                if pid:
                    self._app = Application(backend=self.backend).connect(process=pid)
                elif classe:
                    janela = Desktop(backend=self.backend).window(class_name=classe)
                    pid_found = janela.process_id()
                    self._app = Application(backend=self.backend).connect(process=pid_found)
                elif titulos:
                    for titulo in titulos:
                        try:
                            janela = Desktop(backend=self.backend).window(title_re=f".*{titulo}.*")
                            pid_found = janela.process_id()
                            self._app = Application(backend=self.backend).connect(process=pid_found)
                            break
                        except Exception:
                            continue
                
                # Fallback: buscar qualquer janela com "RM"
                if not self._app:
                    for w in Desktop(backend=self.backend).windows():
                        if "RM" in w.window_text():
                            pid_found = w.process_id()
                            self._app = Application(backend=self.backend).connect(process=pid_found)
                            break
                
                if self._app:
                    logger.info("Conexão estabelecida com sucesso")
                    return True
                    
            except Exception as e:
                logger.warning(f"Falha na tentativa {attempt}: {e}")
                if attempt < self.retries:
                    time.sleep(self.delay)
        
        logger.error("Não foi possível estabelecer conexão com o TOTVS RM")
        return False
    
    def _capture_windows(self) -> None:
        """
        Captura informações de todas as janelas da aplicação.
        """
        if not self._app:
            return
        
        for window in self._app.windows():
            try:
                window_info = self._process_window(window)
                if window_info:
                    handle = str(window.handle)
                    self._connected_windows[handle] = window_info
                    
            except Exception as e:
                logger.error(f"Falha ao processar janela {window.window_text()}: {e}")
                continue
    
    def _process_window(self, window) -> Optional[Dict[str, Any]]:
        """
        Processa uma janela individual com retry.
        
        Args:
            window: Janela a ser processada.
        
        Returns:
            Dict com informações da janela ou None se falhar.
        """
        img_path = None
        
        # Capturar screenshot com retry
        if self.screenshot_enabled:
            for attempt in range(1, self.control_retry + 1):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_title = self._sanitize_filename(window.window_text())
                    img_path = self.screenshot_dir / f"{timestamp}_{safe_title}.png"
                    window.capture_as_image().save(str(img_path))
                    break
                except Exception as e:
                    logger.warning(f"Tentativa {attempt} falhou para screenshot: {e}")
                    if attempt < self.control_retry:
                        time.sleep(self.control_delay)
        
        return {
            "title": window.window_text(),
            "pid": window.process_id(),
            "element": window,
            "screenshot": str(img_path) if img_path else None
        }
    
    def _sanitize_filename(self, filename: str, max_length: int = 40) -> str:
        """
        Sanitiza nome de arquivo removendo caracteres inválidos.
        
        Args:
            filename: Nome original.
            max_length: Comprimento máximo.
        
        Returns:
            Nome sanitizado.
        """
        # Remover caracteres inválidos
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")
        
        # Substituir espaços e limitar comprimento
        filename = filename.replace(" ", "_")[:max_length]
        
        return filename if filename else "unnamed"
    
    def _validate_structure(self, yaml_path: str) -> None:
        """
        Valida estrutura das janelas contra arquivo YAML.
        
        Args:
            yaml_path: Caminho para arquivo YAML de validação.
        """
        try:
            expected_structure = self._load_yaml_structure(yaml_path)
            
            for handle, window_info in self._connected_windows.items():
                real_tree = self._extract_window_tree(window_info["element"], depth=2)
                
                for expected_window in expected_structure.get("expected_windows", []):
                    errors = self._validate_tree(real_tree, expected_window, f"[handle {handle}]")
                    
                    if errors:
                        logger.warning(f"Divergências encontradas para handle {handle}:\n" + "\n".join(errors))
                    else:
                        logger.info(f"[handle {handle}] Estrutura validada com sucesso!")
                        
        except Exception as e:
            logger.warning(f"Erro durante validação estrutural: {e}")
    
    def _load_yaml_structure(self, yaml_path: str) -> Dict[str, Any]:
        """
        Carrega estrutura esperada do arquivo YAML.
        
        Args:
            yaml_path: Caminho para o arquivo YAML.
        
        Returns:
            Estrutura carregada do YAML.
        """
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def _extract_window_tree(self, window, depth: int = 2) -> Dict[str, Any]:
        """
        Extrai árvore de elementos da janela.
        
        Args:
            window: Janela para extrair árvore.
            depth: Profundidade da extração.
        
        Returns:
            Árvore de elementos.
        """
        element_info = getattr(window, "element_info", None)
        control_type = getattr(element_info, "control_type", None) if element_info else None
        
        node = {
            "title": window.window_text(),
            "control_type": control_type,
            "children": []
        }
        
        if depth > 0:
            try:
                for child in window.children():
                    node["children"].append(self._extract_window_tree(child, depth - 1))
            except Exception as e:
                logger.debug(f"Erro ao extrair filhos: {e}")
        
        return node
    
    def _validate_tree(self, real: Dict[str, Any], expected: Dict[str, Any], path: str = "") -> List[str]:
        """
        Valida árvore real contra esperada.
        
        Args:
            real: Árvore real extraída.
            expected: Árvore esperada do YAML.
            path: Caminho atual na validação.
        
        Returns:
            Lista de erros encontrados.
        """
        errors = []
        
        # Elementos dinâmicos do RM que podem não estar presentes
        dynamic_elements = {
            'Minimize', 'Maximize', 'Close',
            'barSubItemContext', 'biWindowMDI', 'barSubItemWindows',
            'barSubItemStartup', 'bBISelfService',
            'Administração de Pessoal', 'Folha Mensal', 'Férias',
            'Rescisão', 'Encargos', 'Anuais', 'eSocial',
            'Orçamento (beta)', 'Configurações', 'Assinatura Eletrônica',
            'Customização', 'Gestão', 'Ambiente',
            'btShowDockedWindows', 'barButtonHelp', 'System'
        }
        
        # Validar título
        if "title" in expected and expected["title"] not in real.get("title", ""):
            errors.append(f"{path}: esperado título '{expected['title']}' mas obtido '{real.get('title')}'")
        
        # Validar tipo de controle
        if "control_type" in expected and expected["control_type"] != real.get("control_type"):
            errors.append(f"{path}: esperado control_type '{expected['control_type']}' mas obtido '{real.get('control_type')}'")
        
        # Validar filhos
        for idx, child_expected in enumerate(expected.get("children", [])):
            child_title = child_expected.get('title', '')
            
            # Pular validação de elementos dinâmicos
            if child_title in dynamic_elements:
                continue
            
            if idx < len(real.get("children", [])):
                errors.extend(self._validate_tree(
                    real["children"][idx], 
                    child_expected, 
                    path + f"/{child_title}"
                ))
            else:
                # Só reportar erro se não for elemento dinâmico
                if child_title not in dynamic_elements:
                    errors.append(f"{path}: filho esperado '{child_title}' não encontrado")
        
        return errors
    
    def generate_yaml_baseline(
        self,
        output_file: Optional[str] = None,
        depth: int = 3
    ) -> str:
        """
        Gera baseline YAML da estrutura atual.
        
        Args:
            output_file: Arquivo de saída. Se None, usa padrão.
            depth: Profundidade da extração.
        
        Returns:
            Caminho do arquivo gerado.
        """
        if not self._app:
            raise UIConnectionError("Aplicação não conectada", "App is None")
        
        if not output_file:
            output_path = self.screenshot_dir / "rm_baseline.yaml"
        else:
            output_path = Path(output_file)
        
        baseline = {"expected_windows": []}
        
        for window in self._app.windows():
            baseline["expected_windows"].append(self._extract_window_tree(window, depth))
        
        # Criar diretório se não existir
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(baseline, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"Baseline YAML gerado em: {output_path}")
        return str(output_path)
    
    def get_connected_windows(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna dicionário de janelas conectadas.
        
        Returns:
            Dicionário com informações das janelas.
        """
        return self._connected_windows.copy()
    
    def get_application(self) -> Optional[Application]:
        """
        Retorna a aplicação conectada.
        
        Returns:
            Instância da aplicação ou None se não conectada.
        """
        return self._app
    
    def disconnect(self) -> None:
        """
        Desconecta da aplicação e limpa recursos.
        """
        self._app = None
        self._connected_windows.clear()
        logger.info("Desconectado da aplicação RM")


def connect_single(
    titulos: Optional[List[str]] = None,
    classe: Optional[str] = None,
    pid: Optional[int] = None,
    backend: str = "uia",
    screenshot: bool = False,
    screenshot_dir: str = "screenshots",
    retries: int = 3,
    delay: float = 2.0,
    yaml_expected: Optional[str] = None,
    control_retry: int = 3,
    control_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Função de conveniência para conexão única com RM.
    
    Args:
        titulos: Lista de títulos para buscar janelas RM.
        classe: Nome da classe da janela para conexão.
        pid: Process ID específico para conexão direta.
        backend: Backend de automação ("win32" ou "uia").
        screenshot: Se deve capturar screenshots das janelas.
        screenshot_dir: Diretório para salvar screenshots.
        retries: Número de tentativas de conexão global.
        delay: Delay entre tentativas de conexão (segundos).
        yaml_expected: Arquivo YAML para validação estrutural.
        control_retry: Tentativas por controle/janela individual.
        control_delay: Delay entre tentativas de controle (segundos).
    
    Returns:
        Dict[str, Any]: Dicionário com handles das janelas encontradas.
    
    Example:
        >>> # Conexão básica com UIA
        >>> janelas = connect_single(
        ...     titulos=["CorporeRM", "TOTVS"],
        ...     backend="uia",
        ...     screenshot=True
        ... )
        
        >>> # Conexão via PID específico
        >>> janelas = connect_single(
        ...     pid=1234,
        ...     backend="uia",
        ...     retries=5
        ... )
    """
    connector = RMSingleConnect(
        backend=backend,
        screenshot_enabled=screenshot,
        screenshot_dir=screenshot_dir,
        retries=retries,
        delay=delay,
        control_retry=control_retry,
        control_delay=control_delay
    )
    
    success, windows = connector.connect_single(
        titulos=titulos,
        classe=classe,
        pid=pid,
        yaml_expected=yaml_expected
    )
    
    return windows if success else {}