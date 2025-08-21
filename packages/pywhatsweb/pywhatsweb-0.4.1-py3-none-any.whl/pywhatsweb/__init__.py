"""
PyWhatsWeb - Biblioteca Python para WhatsApp Web corporativo

Uma biblioteca baseada em sidecar Node.js com whatsapp-web.js para integração
direta em apps corporativos (Django, Flask, etc.) sem abrir navegador.
"""

import sys
from packaging import version

def check_python_compatibility():
    """Verifica compatibilidade do Python no import"""
    python_version = sys.version_info

    if python_version < (3, 8):
        raise RuntimeError(
            f"Python 3.8+ é obrigatório. Atual: {python_version.major}.{python_version.minor}"
        )

    # Verificar dependências opcionais
    try:
        import django
        django_version = version.parse(django.get_version())
        if django_version < version.parse("3.2"):
            print("⚠️  Django 3.2+ recomendado para funcionalidade completa")
    except ImportError:
        pass  # Django é opcional

    try:
        import websockets
        websockets_version = version.parse(websockets.__version__)
        if websockets_version < version.parse("10.0"):
            print("⚠️  websockets 10.0+ recomendado para funcionalidade completa")
    except ImportError:
        pass  # websockets é obrigatório mas pode falhar aqui

# Executar verificação no import
check_python_compatibility()

__version__ = "0.4.1"
__author__ = "TI Léo Team"
__email__ = "ti.leo@example.com"

# Core classes
from .manager import WhatsWebManager
from .session import Session

# Enums
from .enums import SessionStatus, MessageType, KanbanStatus

# Interfaces de persistência
from .storage.base import BaseStore
from .storage.filesystem import FileSystemStore
from .storage.django import DjangoORMStore

# Exceções
from .exceptions import (
    WhatsAppError, ConnectionError, SessionError, 
    MessageError, StorageError, AuthenticationError, WebSocketError, APIError
)

# Modelos de dados
from .models import Message, Contact, Group, MediaMessage, Chat, SessionEvent

__all__ = [
    # Core
    "WhatsWebManager",
    "Session",
    
    # Enums
    "SessionStatus", 
    "MessageType",
    "KanbanStatus",
    
    # Storage
    "BaseStore",
    "FileSystemStore", 
    "DjangoORMStore",
    
    # Exceções
    "WhatsAppError",
    "ConnectionError", 
    "SessionError",
    "MessageError",
    "StorageError",
    "AuthenticationError",
    "WebSocketError",
    "APIError",
    
    # Modelos
    "Message",
    "Contact", 
    "Group",
    "MediaMessage",
    "Chat",
    "SessionEvent",
]
