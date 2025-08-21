"""
Exceções personalizadas para PyWhatsWeb
"""


class WhatsAppError(Exception):
    """Exceção base para todos os erros do PyWhatsWeb"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ConnectionError(WhatsAppError):
    """Erro de conexão com o sidecar"""
    
    def __init__(self, message: str = "Erro de conexão com o sidecar"):
        super().__init__(message, "CONNECTION_ERROR")


class SessionError(WhatsAppError):
    """Erro relacionado a sessões"""
    
    def __init__(self, message: str = "Erro relacionado a sessões"):
        super().__init__(message, "SESSION_ERROR")


class AuthenticationError(WhatsAppError):
    """Erro de autenticação (QR Code, sessão expirada, etc.)"""
    
    def __init__(self, message: str = "Erro de autenticação"):
        super().__init__(message, "AUTH_ERROR")


class MessageError(WhatsAppError):
    """Erro ao enviar ou processar mensagem"""
    
    def __init__(self, message: str = "Erro ao processar mensagem"):
        super().__init__(message, "MESSAGE_ERROR")


class StorageError(WhatsAppError):
    """Erro de persistência/storage"""
    
    def __init__(self, message: str = "Erro de persistência"):
        super().__init__(message, "STORAGE_ERROR")


class TimeoutError(WhatsAppError):
    """Timeout em operações"""
    
    def __init__(self, message: str = "Timeout na operação"):
        super().__init__(message, "TIMEOUT_ERROR")


class ElementNotFoundError(WhatsAppError):
    """Elemento não encontrado na página"""
    
    def __init__(self, message: str = "Elemento não encontrado"):
        super().__init__(message, "ELEMENT_NOT_FOUND")


class InvalidPhoneError(WhatsAppError):
    """Número de telefone inválido"""
    
    def __init__(self, phone: str):
        message = f"Número de telefone inválido: {phone}"
        super().__init__(message, "INVALID_PHONE")


class GroupError(WhatsAppError):
    """Erro relacionado a grupos"""
    
    def __init__(self, message: str = "Erro relacionado a grupos"):
        super().__init__(message, "GROUP_ERROR")


class WebSocketError(WhatsAppError):
    """Erro de WebSocket"""
    
    def __init__(self, message: str = "Erro de WebSocket"):
        super().__init__(message, "WEBSOCKET_ERROR")


class APIError(WhatsAppError):
    """Erro da API do sidecar"""
    
    def __init__(self, message: str = "Erro da API", status_code: int = None):
        self.status_code = status_code
        super().__init__(message, "API_ERROR")
