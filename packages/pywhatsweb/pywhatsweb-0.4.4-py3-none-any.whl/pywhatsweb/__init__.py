"""
PyWhatsWeb - Biblioteca Python para WhatsApp Web corporativo
Baseada em sidecar Node.js com whatsapp-web.js

Funcionalidades principais:
- Gerenciamento de sessões WhatsApp
- Envio e recebimento de mensagens
- Suporte a mídia (imagens, documentos, áudio, vídeo)
- Sistema de idempotência para mensagens
- Integração com Django ORM
- Multi-tenancy e auditoria
- Métricas Prometheus
- WebSocket para eventos em tempo real

Compatibilidade:
- Python: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- Django: 3.2+ (opcional)
- Node.js: 18+ (para sidecar)
- whatsapp-web.js: 1.23+ (para sidecar)
- Puppeteer: 21+ (para sidecar)

Exemplo básico:
    from pywhatsweb import WhatsWebManager
    
    # Inicializar gerenciador
    manager = WhatsWebManager(
        sidecar_host="localhost",
        sidecar_port=3000,
        api_key="sua-chave-api"
    )
    
    # Criar sessão
    session = manager.create_session("minha-sessao")
    
    # Conectar WhatsApp
    session.start()
    
    # Enviar mensagem
    session.send_text("5511999999999", "Olá! Como vai?")
    
    # Parar sessão
    session.stop()
"""

import sys
from typing import TYPE_CHECKING

# Verificar compatibilidade do Python
def check_python_compatibility():
    """Verifica compatibilidade com versão do Python"""
    if sys.version_info < (3, 8):
        raise RuntimeError(
            "PyWhatsWeb requer Python 3.8 ou superior. "
            f"Versão atual: {sys.version}"
        )
    
    # Verificar versões recomendadas
    if sys.version_info >= (3, 13):
        print("✅ Python 3.13+ detectado - Suporte completo!")
    elif sys.version_info >= (3, 11):
        print("✅ Python 3.11+ detectado - Suporte completo!")
    elif sys.version_info >= (3, 8):
        print("✅ Python 3.8+ detectado - Suporte básico!")
    
    # Verificar dependências opcionais
    try:
        import django
        if django.VERSION >= (3, 2):
            print("✅ Django 3.2+ detectado - Suporte completo!")
        else:
            print("⚠️  Django < 3.2 detectado - Funcionalidades limitadas")
    except ImportError:
        print("ℹ️  Django não instalado - Use 'pip install pywhatsweb[django]'")
    
    try:
        import websockets
        # websockets 15.0+ não tem version_tuple, usar __version__ em vez disso
        try:
            # Tentar usar version_tuple (websockets < 15.0)
            if hasattr(websockets, 'version_tuple') and websockets.version_tuple >= (10, 0):
                print("✅ websockets 10.0+ detectado - Suporte completo!")
            elif hasattr(websockets, '__version__'):
                # websockets 15.0+ usa __version__
                import packaging.version
                ws_version = packaging.version.parse(websockets.__version__)
                if ws_version >= packaging.version.parse("10.0"):
                    print("✅ websockets 10.0+ detectado - Suporte completo!")
                else:
                    print("⚠️  websockets < 10.0 detectado - Funcionalidades limitadas")
            else:
                print("⚠️  websockets versão desconhecida - Funcionalidades limitadas")
        except Exception:
            print("⚠️  Erro ao verificar versão do websockets - Funcionalidades limitadas")
    except ImportError:
        print("ℹ️  websockets não instalado - Funcionalidades limitadas")

# Executar verificação de compatibilidade
check_python_compatibility()

# Importações principais
from .manager import WhatsWebManager
from .session import Session
from .storage import BaseStore, FileSystemStore, DjangoORMStore
from .enums import SessionStatus, KanbanStatus, MessageType, MessageStatus, ErrorCode

# Configuração de tipos para mypy
if TYPE_CHECKING:
    from .types import (
        Message,
        Contact,
        Group,
        Chat,
        SessionEvent,
        MessageDeliveryStatus
    )

# Versão da biblioteca
__version__ = "0.4.4"
__author__ = "TI Léo Team"
__email__ = "ti.leo@example.com"
__license__ = "MIT"
__url__ = "https://github.com/ti-leo/pywhatsweb"

# Informações de compatibilidade
__python_requires__ = ">=3.8"
__python_support__ = ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]

# Dependências principais
__dependencies__ = [
    "requests>=2.25.0",
    "websockets>=10.0",
    "packaging>=21.0",
    "qrcode>=7.4.0",
    "Pillow>=10.0.0",
]

# Dependências opcionais
__optional_dependencies__ = {
    "django": ["Django>=3.2", "django-storages>=1.13.0"],
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
        "pre-commit>=3.0.0",
    ]
}

# Configurações padrão
__default_config__ = {
    "sidecar_host": "localhost",
    "sidecar_port": 3000,
    "api_key": "pywhatsweb-secret-key",
    "storage_backend": "filesystem",
    "websocket_reconnect_attempts": 5,
    "websocket_reconnect_delay": 1.0,
    "websocket_heartbeat_interval": 30,
    "message_timeout": 30,
    "media_max_size": 16 * 1024 * 1024,  # 16MB
    "idempotency_ttl": 24 * 60 * 60,  # 24 horas
}

# Expor classes principais
__all__ = [
    # Classes principais
    "WhatsWebManager",
    "Session",
    
    # Storage
    "BaseStore",
    "FileSystemStore", 
    "DjangoORMStore",
    
    # Enums
    "SessionStatus",
    "KanbanStatus",
    "MessageType",
    "MessageStatus",
    "ErrorCode",
    
    # Informações da biblioteca
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__url__",
    "__python_requires__",
    "__python_support__",
    "__dependencies__",
    "__optional_dependencies__",
    "__default_config__",
]

# Mensagem de boas-vindas
def _print_welcome():
    """Imprime mensagem de boas-vindas"""
    print(f"🚀 PyWhatsWeb {__version__} carregado com sucesso!")
    print(f"✅ Compatível com Python {'.'.join(map(str, sys.version_info[:2]))}")
    print(f"📚 Documentação: {__url__}")
    print(f"🐛 Issues: {__url__}/issues")

# Imprimir mensagem de boas-vindas apenas em desenvolvimento
if __name__ == "__main__":
    _print_welcome()
