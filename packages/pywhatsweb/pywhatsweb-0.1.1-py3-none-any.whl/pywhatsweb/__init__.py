"""
PyWhatsWeb - Biblioteca Python para automação do WhatsApp Web

Uma biblioteca inspirada no whatsapp-web.js para automação completa
do WhatsApp Web usando Python e Selenium.
"""

__version__ = "0.1.0"
__author__ = "TI Léo Team"
__email__ = "ti.leo@example.com"

from .client import WhatsAppClient
from .config import Config
from .models import Message, Contact, Group, MediaMessage
from .exceptions import WhatsAppError, ConnectionError, MessageError

__all__ = [
    "WhatsAppClient",
    "Config", 
    "Message",
    "Contact",
    "Group",
    "MediaMessage",
    "WhatsAppError",
    "ConnectionError",
    "MessageError",
]
