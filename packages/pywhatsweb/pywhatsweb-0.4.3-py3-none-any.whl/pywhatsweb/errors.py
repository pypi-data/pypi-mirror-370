"""
Catálogo de erros padronizados para PyWhatsWeb

Define todos os códigos de erro, HTTP status, mensagens e ações recomendadas.
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class ErrorCode(Enum):
    """Códigos de erro padronizados"""
    
    # Erros de sessão
    E_SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    E_SESSION_ALREADY_EXISTS = "SESSION_ALREADY_EXISTS"
    E_SESSION_NOT_READY = "SESSION_NOT_READY"
    E_SESSION_EXPIRED = "SESSION_EXPIRED"
    E_SESSION_LIMIT_EXCEEDED = "SESSION_LIMIT_EXCEEDED"
    
    # Erros de autenticação
    E_AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    E_AUTHENTICATION_EXPIRED = "AUTHENTICATION_EXPIRED"
    E_INVALID_API_KEY = "INVALID_API_KEY"
    E_INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Erros de mensagem
    E_MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"
    E_MEDIA_TOO_LARGE = "MEDIA_TOO_LARGE"
    E_INVALID_MEDIA_TYPE = "INVALID_MEDIA_TYPE"
    E_MESSAGE_RATE_LIMIT = "MESSAGE_RATE_LIMIT"
    E_MESSAGE_DELIVERY_FAILED = "MESSAGE_DELIVERY_FAILED"
    
    # Erros de conexão
    E_CONNECTION_FAILED = "CONNECTION_FAILED"
    E_CONNECTION_TIMEOUT = "CONNECTION_TIMEOUT"
    E_WEBSOCKET_ERROR = "WEBSOCKET_ERROR"
    E_SIDECAR_UNAVAILABLE = "SIDECAR_UNAVAILABLE"
    
    # Erros de validação
    E_INVALID_PHONE_NUMBER = "INVALID_PHONE_NUMBER"
    E_INVALID_SESSION_ID = "INVALID_SESSION_ID"
    E_INVALID_TENANT_ID = "INVALID_TENANT_ID"
    E_INVALID_PAYLOAD = "INVALID_PAYLOAD"
    
    # Erros de storage
    E_STORAGE_ERROR = "STORAGE_ERROR"
    E_STORAGE_FULL = "STORAGE_FULL"
    E_STORAGE_PERMISSION_DENIED = "STORAGE_PERMISSION_DENIED"
    
    # Erros de sistema
    E_INTERNAL_ERROR = "INTERNAL_ERROR"
    E_SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    E_MAINTENANCE_MODE = "MAINTENANCE_MODE"
    E_VERSION_INCOMPATIBLE = "VERSION_INCOMPATIBLE"
    
    # Erros de WhatsApp
    E_WHATSAPP_NOT_CONNECTED = "WHATSAPP_NOT_CONNECTED"
    E_WHATSAPP_QR_EXPIRED = "WHATSAPP_QR_EXPIRED"
    E_WHATSAPP_2FA_REQUIRED = "WHATSAPP_2FA_REQUIRED"
    E_WHATSAPP_BANNED = "WHATSAPP_BANNED"
    E_WHATSAPP_RATE_LIMITED = "WHATSAPP_RATE_LIMITED"


class ErrorSeverity(Enum):
    """Severidade dos erros"""
    LOW = "low"           # Aviso, não afeta funcionalidade
    MEDIUM = "medium"     # Erro recuperável
    HIGH = "high"         # Erro crítico, afeta funcionalidade
    CRITICAL = "critical" # Erro fatal, sistema inoperante


@dataclass
class ErrorInfo:
    """Informações completas sobre um erro"""
    code: ErrorCode
    http_status: int
    message: str
    severity: ErrorSeverity
    retryable: bool
    action: str
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'error_code': self.code.value,
            'http_status': self.http_status,
            'message': self.message,
            'severity': self.severity.value,
            'retryable': self.retryable,
            'action': self.action,
            'details': self.details,
            'timestamp': None  # Será preenchido pelo handler
        }


# Catálogo completo de erros
ERROR_CATALOG: Dict[ErrorCode, ErrorInfo] = {
    # Erros de sessão
    ErrorCode.E_SESSION_NOT_FOUND: ErrorInfo(
        code=ErrorCode.E_SESSION_NOT_FOUND,
        http_status=404,
        message="Sessão não encontrada",
        severity=ErrorSeverity.MEDIUM,
        retryable=False,
        action="Verificar se o session_id está correto e se a sessão foi criada"
    ),
    
    ErrorCode.E_SESSION_ALREADY_EXISTS: ErrorInfo(
        code=ErrorCode.E_SESSION_ALREADY_EXISTS,
        http_status=409,
        message="Sessão já existe",
        severity=ErrorSeverity.LOW,
        retryable=False,
        action="Usar session_id diferente ou parar a sessão existente primeiro"
    ),
    
    ErrorCode.E_SESSION_NOT_READY: ErrorInfo(
        code=ErrorCode.E_SESSION_NOT_READY,
        http_status=400,
        message="Sessão não está pronta",
        severity=ErrorSeverity.MEDIUM,
        retryable=True,
        action="Aguardar evento 'ready' ou verificar status da sessão"
    ),
    
    ErrorCode.E_SESSION_EXPIRED: ErrorInfo(
        code=ErrorCode.E_SESSION_EXPIRED,
        http_status=410,
        message="Sessão expirada",
        severity=ErrorSeverity.MEDIUM,
        retryable=False,
        action="Criar nova sessão e escanear QR code novamente"
    ),
    
    ErrorCode.E_SESSION_LIMIT_EXCEEDED: ErrorInfo(
        code=ErrorCode.E_SESSION_LIMIT_EXCEEDED,
        http_status=429,
        message="Limite de sessões excedido",
        severity=ErrorSeverity.HIGH,
        retryable=True,
        action="Parar sessões não utilizadas ou aumentar limite no sidecar"
    ),
    
    # Erros de autenticação
    ErrorCode.E_AUTHENTICATION_FAILED: ErrorInfo(
        code=ErrorCode.E_AUTHENTICATION_FAILED,
        http_status=401,
        message="Falha na autenticação",
        severity=ErrorSeverity.HIGH,
        retryable=False,
        action="Verificar API key e permissões"
    ),
    
    ErrorCode.E_AUTHENTICATION_EXPIRED: ErrorInfo(
        code=ErrorCode.E_AUTHENTICATION_EXPIRED,
        http_status=401,
        message="Autenticação expirada",
        severity=ErrorSeverity.MEDIUM,
        retryable=True,
        action="Renovar token de autenticação"
    ),
    
    ErrorCode.E_INVALID_API_KEY: ErrorInfo(
        code=ErrorCode.E_INVALID_API_KEY,
        http_status=401,
        message="API key inválida",
        severity=ErrorSeverity.HIGH,
        retryable=False,
        action="Verificar API key no header Authorization"
    ),
    
    ErrorCode.E_INSUFFICIENT_PERMISSIONS: ErrorInfo(
        code=ErrorCode.E_INSUFFICIENT_PERMISSIONS,
        http_status=403,
        message="Permissões insuficientes",
        severity=ErrorSeverity.HIGH,
        retryable=False,
        action="Verificar permissões do usuário/tenant"
    ),
    
    # Erros de mensagem
    ErrorCode.E_MESSAGE_TOO_LONG: ErrorInfo(
        code=ErrorCode.E_MESSAGE_TOO_LONG,
        http_status=400,
        message="Mensagem muito longa",
        severity=ErrorSeverity.LOW,
        retryable=False,
        action="Reduzir tamanho da mensagem (máximo 4096 caracteres)"
    ),
    
    ErrorCode.E_MEDIA_TOO_LARGE: ErrorInfo(
        code=ErrorCode.E_MEDIA_TOO_LARGE,
        http_status=400,
        message="Arquivo de mídia muito grande",
        severity=ErrorSeverity.LOW,
        retryable=False,
        action="Reduzir tamanho do arquivo (máximo 16MB) ou usar ponteiro S3"
    ),
    
    ErrorCode.E_INVALID_MEDIA_TYPE: ErrorInfo(
        code=ErrorCode.E_INVALID_MEDIA_TYPE,
        http_status=400,
        message="Tipo de mídia não suportado",
        severity=ErrorSeverity.LOW,
        retryable=False,
        action="Usar tipo de mídia suportado (JPEG, PNG, MP4, PDF, etc.)"
    ),
    
    ErrorCode.E_MESSAGE_RATE_LIMIT: ErrorInfo(
        code=ErrorCode.E_MESSAGE_RATE_LIMIT,
        http_status=429,
        message="Limite de mensagens excedido",
        severity=ErrorSeverity.MEDIUM,
        retryable=True,
        action="Aguardar e tentar novamente (máximo 30 msg/min)"
    ),
    
    ErrorCode.E_MESSAGE_DELIVERY_FAILED: ErrorInfo(
        code=ErrorCode.E_MESSAGE_DELIVERY_FAILED,
        http_status=500,
        message="Falha na entrega da mensagem",
        severity=ErrorSeverity.MEDIUM,
        retryable=True,
        action="Verificar conexão e tentar novamente"
    ),
    
    # Erros de conexão
    ErrorCode.E_CONNECTION_FAILED: ErrorInfo(
        code=ErrorCode.E_CONNECTION_FAILED,
        http_status=503,
        message="Falha na conexão com sidecar",
        severity=ErrorSeverity.HIGH,
        retryable=True,
        action="Verificar se o sidecar está rodando e acessível"
    ),
    
    ErrorCode.E_CONNECTION_TIMEOUT: ErrorInfo(
        code=ErrorCode.E_CONNECTION_TIMEOUT,
        http_status=504,
        message="Timeout na conexão",
        severity=ErrorSeverity.MEDIUM,
        retryable=True,
        action="Verificar latência de rede e aumentar timeout se necessário"
    ),
    
    ErrorCode.E_WEBSOCKET_ERROR: ErrorInfo(
        code=ErrorCode.E_WEBSOCKET_ERROR,
        http_status=500,
        message="Erro na conexão WebSocket",
        severity=ErrorSeverity.MEDIUM,
        retryable=True,
        action="Verificar conectividade e tentar reconectar"
    ),
    
    ErrorCode.E_SIDECAR_UNAVAILABLE: ErrorInfo(
        code=ErrorCode.E_SIDECAR_UNAVAILABLE,
        http_status=503,
        message="Sidecar indisponível",
        severity=ErrorSeverity.HIGH,
        retryable=True,
        action="Verificar status do sidecar e reiniciar se necessário"
    ),
    
    # Erros de validação
    ErrorCode.E_INVALID_PHONE_NUMBER: ErrorInfo(
        code=ErrorCode.E_INVALID_PHONE_NUMBER,
        http_status=400,
        message="Número de telefone inválido",
        severity=ErrorSeverity.LOW,
        retryable=False,
        action="Usar formato E.164 (+5511999999999)"
    ),
    
    ErrorCode.E_INVALID_SESSION_ID: ErrorInfo(
        code=ErrorCode.E_INVALID_SESSION_ID,
        http_status=400,
        message="ID de sessão inválido",
        severity=ErrorSeverity.LOW,
        retryable=False,
        action="Usar apenas letras, números e underscore (3-100 chars)"
    ),
    
    ErrorCode.E_INVALID_TENANT_ID: ErrorInfo(
        code=ErrorCode.E_INVALID_TENANT_ID,
        http_status=400,
        message="ID de tenant inválido",
        severity=ErrorSeverity.LOW,
        retryable=False,
        action="Usar apenas letras, números e underscore (3-50 chars)"
    ),
    
    ErrorCode.E_INVALID_PAYLOAD: ErrorInfo(
        code=ErrorCode.E_INVALID_PAYLOAD,
        http_status=400,
        message="Payload da requisição inválido",
        severity=ErrorSeverity.LOW,
        retryable=False,
        action="Verificar formato JSON e campos obrigatórios"
    ),
    
    # Erros de storage
    ErrorCode.E_STORAGE_ERROR: ErrorInfo(
        code=ErrorCode.E_STORAGE_ERROR,
        http_status=500,
        message="Erro no sistema de storage",
        severity=ErrorSeverity.HIGH,
        retryable=True,
        action="Verificar permissões de arquivo/banco e espaço em disco"
    ),
    
    ErrorCode.E_STORAGE_FULL: ErrorInfo(
        code=ErrorCode.E_STORAGE_FULL,
        http_status=507,
        message="Storage cheio",
        severity=ErrorSeverity.HIGH,
        retryable=False,
        action="Liberar espaço ou configurar novo storage"
    ),
    
    ErrorCode.E_STORAGE_PERMISSION_DENIED: ErrorInfo(
        code=ErrorCode.E_STORAGE_PERMISSION_DENIED,
        http_status=403,
        message="Permissão negada no storage",
        severity=ErrorSeverity.HIGH,
        retryable=False,
        action="Verificar permissões de arquivo/banco"
    ),
    
    # Erros de sistema
    ErrorCode.E_INTERNAL_ERROR: ErrorInfo(
        code=ErrorCode.E_INTERNAL_ERROR,
        http_status=500,
        message="Erro interno do sistema",
        severity=ErrorSeverity.CRITICAL,
        retryable=True,
        action="Verificar logs e contatar suporte"
    ),
    
    ErrorCode.E_SERVICE_UNAVAILABLE: ErrorInfo(
        code=ErrorCode.E_SERVICE_UNAVAILABLE,
        http_status=503,
        message="Serviço indisponível",
        severity=ErrorSeverity.HIGH,
        retryable=True,
        action="Aguardar e tentar novamente"
    ),
    
    ErrorCode.E_MAINTENANCE_MODE: ErrorInfo(
        code=ErrorCode.E_MAINTENANCE_MODE,
        http_status=503,
        message="Sistema em manutenção",
        severity=ErrorSeverity.MEDIUM,
        retryable=True,
        action="Aguardar conclusão da manutenção"
    ),
    
    ErrorCode.E_VERSION_INCOMPATIBLE: ErrorInfo(
        code=ErrorCode.E_VERSION_INCOMPATIBLE,
        http_status=400,
        message="Versão incompatível",
        severity=ErrorSeverity.HIGH,
        retryable=False,
        action="Atualizar SDK ou sidecar para versão compatível"
    ),
    
    # Erros de WhatsApp
    ErrorCode.E_WHATSAPP_NOT_CONNECTED: ErrorInfo(
        code=ErrorCode.E_WHATSAPP_NOT_CONNECTED,
        http_status=400,
        message="WhatsApp não está conectado",
        severity=ErrorSeverity.MEDIUM,
        retryable=True,
        action="Verificar conexão e reconectar se necessário"
    ),
    
    ErrorCode.E_WHATSAPP_QR_EXPIRED: ErrorInfo(
        code=ErrorCode.E_WHATSAPP_QR_EXPIRED,
        http_status=400,
        message="QR Code expirado",
        severity=ErrorSeverity.MEDIUM,
        retryable=False,
        action="Gerar novo QR Code e escanear novamente"
    ),
    
    ErrorCode.E_WHATSAPP_2FA_REQUIRED: ErrorInfo(
        code=ErrorCode.E_WHATSAPP_2FA_REQUIRED,
        http_status=400,
        message="Autenticação 2FA necessária",
        severity=ErrorSeverity.HIGH,
        retryable=False,
        action="Configurar 2FA no WhatsApp ou usar backup"
    ),
    
    ErrorCode.E_WHATSAPP_BANNED: ErrorInfo(
        code=ErrorCode.E_WHATSAPP_BANNED,
        http_status=403,
        message="WhatsApp banido",
        severity=ErrorSeverity.CRITICAL,
        retryable=False,
        action="Verificar status da conta e contatar suporte WhatsApp"
    ),
    
    ErrorCode.E_WHATSAPP_RATE_LIMITED: ErrorInfo(
        code=ErrorCode.E_WHATSAPP_RATE_LIMITED,
        http_status=429,
        message="WhatsApp com limite de taxa",
        severity=ErrorSeverity.MEDIUM,
        retryable=True,
        action="Aguardar e reduzir frequência de mensagens"
    ),
}


def get_error_info(error_code: ErrorCode) -> ErrorInfo:
    """Obtém informações de um erro pelo código"""
    return ERROR_CATALOG.get(error_code, ERROR_CATALOG[ErrorCode.E_INTERNAL_ERROR])


def get_error_by_http_status(http_status: int) -> list[ErrorInfo]:
    """Obtém todos os erros com um determinado HTTP status"""
    return [error for error in ERROR_CATALOG.values() if error.http_status == http_status]


def get_retryable_errors() -> list[ErrorInfo]:
    """Obtém todos os erros que podem ser tentados novamente"""
    return [error for error in ERROR_CATALOG.values() if error.retryable]


def get_errors_by_severity(severity: ErrorSeverity) -> list[ErrorInfo]:
    """Obtém todos os erros de uma determinada severidade"""
    return [error for error in ERROR_CATALOG.values() if error.severity == severity]


def create_error_response(error_code: ErrorCode, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Cria resposta de erro padronizada"""
    error_info = get_error_info(error_code)
    
    response = error_info.to_dict()
    if details:
        response['details'] = details
    
    return response


# Constantes para uso em código
RETRYABLE_ERRORS = get_retryable_errors()
CRITICAL_ERRORS = get_errors_by_severity(ErrorSeverity.CRITICAL)
HIGH_SEVERITY_ERRORS = get_errors_by_severity(ErrorSeverity.HIGH)
