"""
Enumerações e contratos do PyWhatsWeb

Define todos os tipos, status e contratos de eventos da biblioteca.
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid


class SessionStatus(Enum):
    """Status das sessões WhatsApp"""
    DISCONNECTED = "disconnected"    # Desconectado
    CONNECTING = "connecting"        # Conectando
    CONNECTED = "connected"          # Conectado
    READY = "ready"                  # Pronto para uso
    ERROR = "error"                  # Erro


class MessageType(Enum):
    """Tipos de mensagem suportados"""
    TEXT = "text"                    # Texto
    IMAGE = "image"                  # Imagem
    AUDIO = "audio"                  # Áudio
    VIDEO = "video"                  # Vídeo
    DOCUMENT = "document"            # Documento
    LOCATION = "location"            # Localização
    CONTACT = "contact"              # Contato
    STICKER = "sticker"              # Sticker


class KanbanStatus(Enum):
    """Status do fluxo Kanban para conversas"""
    NEW = "new"                      # Aguardando
    ACTIVE = "active"                # Em atendimento
    DONE = "done"                    # Concluídos


class EventType(Enum):
    """Tipos de eventos WebSocket"""
    QR = "qr"                        # QR Code para autenticação
    AUTHENTICATED = "authenticated"  # Autenticação bem-sucedida
    READY = "ready"                  # WhatsApp pronto
    MESSAGE = "message"              # Nova mensagem
    DISCONNECTED = "disconnected"    # Desconexão
    ERROR = "error"                  # Erro


class MessageStatus(Enum):
    """Status de entrega das mensagens"""
    PENDING = "pending"              # Enfileirada
    SENT = "sent"                    # Enviada
    DELIVERED = "delivered"          # Entregue
    READ = "read"                    # Lida
    FAILED = "failed"                # Falhou


@dataclass
class EventPayload:
    """Payload padrão para todos os eventos"""
    event: EventType                 # Tipo do evento
    session_id: str                  # ID da sessão
    timestamp: datetime              # Timestamp do evento
    trace_id: str                    # ID único para rastreamento
    data: Dict[str, Any]            # Dados específicos do evento
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.trace_id:
            self.trace_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'event': self.event.value,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'trace_id': self.trace_id,
            'data': self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventPayload':
        """Cria EventPayload a partir de dicionário"""
        # Converter event
        if 'event' in data:
            data['event'] = EventType(data['event'])
        
        # Converter timestamp
        if data.get('timestamp'):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return cls(**data)


# ============================================================================
# CONTRATOS DE EVENTOS ESPECÍFICOS
# ============================================================================

@dataclass
class QREventData:
    """Dados do evento QR"""
    qr: str                          # Data URL (PNG/base64) para <img src="...">
    expires_in: int                  # Tempo de expiração em segundos
    attempts: int                    # Tentativas de leitura
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'qr': self.qr,
            'expires_in': self.expires_in,
            'attempts': self.attempts
        }


@dataclass
class AuthenticatedEventData:
    """Dados do evento de autenticação"""
    phone_number: str                # Número do telefone
    device_info: Dict[str, Any]     # Informações do dispositivo
    contacts_count: int              # Número de contatos
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'phone_number': self.phone_number,
            'device_info': self.device_info,
            'contacts_count': self.contacts_count
        }


@dataclass
class ReadyEventData:
    """Dados do evento ready"""
    phone_number: str                # Número do telefone
    device_info: Dict[str, Any]     # Informações do dispositivo
    contacts_count: int              # Número de contatos
    groups_count: int                # Número de grupos
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'phone_number': self.phone_number,
            'device_info': self.device_info,
            'contacts_count': self.contacts_count,
            'groups_count': self.groups_count
        }


@dataclass
class MessageEventData:
    """Dados do evento de mensagem"""
    message_id: str                  # ID único da mensagem
    chat_id: str                     # ID do chat (número ou grupo)
    from_number: str                 # Número do remetente
    to_number: str                   # Número do destinatário
    body: str                        # Conteúdo da mensagem
    message_type: MessageType        # Tipo da mensagem
    timestamp: datetime              # Timestamp da mensagem
    is_group: bool                   # É mensagem de grupo?
    group_name: Optional[str]        # Nome do grupo (se aplicável)
    quoted_message: Optional[str]    # ID da mensagem citada
    mentions: Optional[list]         # Menções na mensagem
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'message_id': self.message_id,
            'chat_id': self.chat_id,
            'from_number': self.from_number,
            'to_number': self.to_number,
            'body': self.body,
            'message_type': self.message_type.value,
            'timestamp': self.timestamp.isoformat(),
            'is_group': self.is_group,
            'group_name': self.group_name,
            'quoted_message': self.quoted_message,
            'mentions': self.mentions
        }


@dataclass
class DisconnectedEventData:
    """Dados do evento de desconexão"""
    reason: str                      # Motivo da desconexão
    code: Optional[int]              # Código de erro (se aplicável)
    can_reconnect: bool              # Pode reconectar automaticamente
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'reason': self.reason,
            'code': self.code,
            'can_reconnect': self.can_reconnect
        }


@dataclass
class ErrorEventData:
    """Dados do evento de erro"""
    error_code: str                  # Código do erro
    error_message: str               # Mensagem de erro
    error_details: Optional[Dict[str, Any]]  # Detalhes adicionais
    recoverable: bool                # Erro é recuperável?
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error_code': self.error_code,
            'error_message': self.error_message,
            'error_details': self.error_details,
            'recoverable': self.recoverable
        }


# ============================================================================
# FÁBRICAS DE EVENTOS
# ============================================================================

def create_qr_event(session_id: str, qr_data: str, expires_in: int = 60, 
                   attempts: int = 0, trace_id: str = None) -> EventPayload:
    """Cria evento QR padronizado"""
    data = QREventData(
        qr=qr_data,
        expires_in=expires_in,
        attempts=attempts
    )
    
    return EventPayload(
        event=EventType.QR,
        session_id=session_id,
        timestamp=datetime.now(),
        trace_id=trace_id or str(uuid.uuid4()),
        data=data.to_dict()
    )


def create_message_event(session_id: str, message_data: Dict[str, Any], 
                        trace_id: str = None) -> EventPayload:
    """Cria evento de mensagem padronizado"""
    data = MessageEventData(
        message_id=message_data.get('messageId'),
        chat_id=message_data.get('chatId'),
        from_number=message_data.get('from'),
        to_number=message_data.get('to'),
        body=message_data.get('body', ''),
        message_type=MessageType(message_data.get('type', 'text')),
        timestamp=datetime.fromtimestamp(message_data.get('timestamp', 0) / 1000),
        is_group=message_data.get('isGroup', False),
        group_name=message_data.get('groupName'),
        quoted_message=message_data.get('quotedMessage'),
        mentions=message_data.get('mentions')
    )
    
    return EventPayload(
        event=EventType.MESSAGE,
        session_id=session_id,
        timestamp=datetime.now(),
        trace_id=trace_id or str(uuid.uuid4()),
        data=data.to_dict()
    )


def create_ready_event(session_id: str, phone_number: str, 
                      device_info: Dict[str, Any], contacts_count: int = 0,
                      groups_count: int = 0, trace_id: str = None) -> EventPayload:
    """Cria evento ready padronizado"""
    data = ReadyEventData(
        phone_number=phone_number,
        device_info=device_info,
        contacts_count=contacts_count,
        groups_count=groups_count
    )
    
    return EventPayload(
        event=EventType.READY,
        session_id=session_id,
        timestamp=datetime.now(),
        trace_id=trace_id or str(uuid.uuid4()),
        data=data.to_dict()
    )


def create_error_event(session_id: str, error_code: str, error_message: str,
                      error_details: Dict[str, Any] = None, recoverable: bool = True,
                      trace_id: str = None) -> EventPayload:
    """Cria evento de erro padronizado"""
    data = ErrorEventData(
        error_code=error_code,
        error_message=error_message,
        error_details=error_details,
        recoverable=recoverable
    )
    
    return EventPayload(
        event=EventType.ERROR,
        session_id=session_id,
        timestamp=datetime.now(),
        trace_id=trace_id or str(uuid.uuid4()),
        data=data.to_dict()
    )


# ============================================================================
# CONSTANTES DO SISTEMA
# ============================================================================

# Configurações de mídia
MAX_MEDIA_SIZE = 16 * 1024 * 1024  # 16MB (limite WhatsApp)
SUPPORTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
SUPPORTED_VIDEO_TYPES = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv']
SUPPORTED_AUDIO_TYPES = ['audio/mp3', 'audio/wav', 'audio/ogg', 'audio/m4a']
SUPPORTED_DOCUMENT_TYPES = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'text/plain', 'application/vnd.ms-excel']

# Timeouts
CONNECTION_TIMEOUT = 30             # Timeout de conexão (segundos)
MESSAGE_TIMEOUT = 60                # Timeout de envio de mensagem (segundos)
QR_EXPIRATION = 60                  # Expiração do QR (segundos)
RECONNECTION_BACKOFF_BASE = 2       # Base do backoff exponencial
MAX_RECONNECTION_ATTEMPTS = 5       # Máximo de tentativas de reconexão

# Rate limits
MAX_MESSAGES_PER_MINUTE = 30        # Máximo de mensagens por minuto
MAX_SESSIONS_PER_IP = 10            # Máximo de sessões por IP
MAX_REQUESTS_PER_MINUTE = 100       # Máximo de requisições por minuto
