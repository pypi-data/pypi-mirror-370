"""
Configurações para o cliente PyWhatsWeb
"""

import os
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configurações para o cliente WhatsApp"""
    
    # Configurações do navegador
    headless: bool = False
    timeout: int = 30
    user_data_dir: str = "./whatsapp_data"
    chrome_options: List[str] = None
    
    # Configurações do WhatsApp
    wait_timeout: int = 60
    qr_timeout: int = 120
    message_timeout: int = 30
    
    # Configurações de debug
    debug: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Inicializa configurações padrão"""
        if self.chrome_options is None:
            self.chrome_options = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",
                "--disable-javascript",
                "--disable-web-security",
                "--allow-running-insecure-content",
                "--disable-features=VizDisplayCompositor"
            ]
        
        # Criar diretório de dados se não existir
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Cria configuração a partir de variáveis de ambiente"""
        return cls(
            headless=os.getenv('WHATSAPP_HEADLESS', 'false').lower() == 'true',
            timeout=int(os.getenv('WHATSAPP_TIMEOUT', '30')),
            user_data_dir=os.getenv('WHATSAPP_USER_DATA_DIR', './whatsapp_data'),
            debug=os.getenv('WHATSAPP_DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('WHATSAPP_LOG_LEVEL', 'INFO')
        )
    
    def get_chrome_options(self) -> List[str]:
        """Retorna opções do Chrome para o Selenium"""
        options = self.chrome_options.copy()
        
        if self.headless:
            options.append("--headless")
        
        options.extend([
            f"--user-data-dir={self.user_data_dir}",
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions-except=./extensions",
            "--disable-plugins-discovery",
            "--disable-default-apps"
        ])
        
        return options
