"""
Modelos de dados para PyWhatsWeb

Dataclasses que representam entidades do WhatsApp (mensagens, contatos, grupos).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid

from .enums import MessageType, KanbanStatus, MessageStatus


@dataclass
class Contact:
    """Contato WhatsApp"""
    
    phone: str
    name: Optional[str] = None
    is_group: bool = False
    is_business: bool = False
    profile_picture: Optional[str] = None
    status: Optional[str] = None
    last_seen: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.phone:
            raise ValueError("Phone é obrigatório")
        
        # Formatar telefone se necessário
        if not self.phone.endswith('@c.us') and not self.phone.endswith('@g.us'):
            if self.is_group:
                self.phone = f"{self.phone}@g.us"
            else:
                self.phone = f"{self.phone}@c.us"
    
    @property
    def display_name(self) -> str:
        """Nome de exibição do contato"""
        return self.name or self.phone.split('@')[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'phone': self.phone,
            'name': self.name,
            'is_group': self.is_group,
            'is_business': self.is_business,
            'profile_picture': self.profile_picture,
            'status': self.status,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contact':
        """Cria Contact a partir de dicionário"""
        # Converter timestamps
        if data.get('last_seen'):
            data['last_seen'] = datetime.fromisoformat(data['last_seen'])
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)


@dataclass
class Group:
    """Grupo WhatsApp"""
    
    id: str
    name: str
    participants: List[Contact] = field(default_factory=list)
    admins: List[Contact] = field(default_factory=list)
    description: Optional[str] = None
    invite_link: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.id:
            raise ValueError("ID é obrigatório")
        if not self.name:
            raise ValueError("Nome é obrigatório")
        
        # Formatar ID se necessário
        if not self.id.endswith('@g.us'):
            self.id = f"{self.id}@g.us"
    
    @property
    def participant_count(self) -> int:
        """Número de participantes"""
        return len(self.participants)
    
    @property
    def admin_count(self) -> int:
        """Número de administradores"""
        return len(self.admins)
    
    def add_participant(self, contact: Contact):
        """Adiciona participante"""
        if contact not in self.participants:
            self.participants.append(contact)
            self.updated_at = datetime.now()
    
    def remove_participant(self, contact: Contact):
        """Remove participante"""
        if contact in self.participants:
            self.participants.remove(contact)
            self.updated_at = datetime.now()
    
    def add_admin(self, contact: Contact):
        """Adiciona administrador"""
        if contact not in self.admins:
            self.admins.append(contact)
            self.updated_at = datetime.now()
    
    def remove_admin(self, contact: Contact):
        """Remove administrador"""
        if contact in self.admins:
            self.admins.remove(contact)
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'participants': [p.to_dict() for p in self.participants],
            'admins': [a.to_dict() for a in self.admins],
            'description': self.description,
            'invite_link': self.invite_link,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Group':
        """Cria Group a partir de dicionário"""
        # Converter participantes
        if 'participants' in data:
            data['participants'] = [Contact.from_dict(p) for p in data['participants']]
        if 'admins' in data:
            data['admins'] = [Contact.from_dict(a) for a in data['admins']]
        
        # Converter timestamps
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)


@dataclass
class Message:
    """Mensagem WhatsApp com idempotência"""
    
    # Campos obrigatórios primeiro (sem default)
    id: str                          # ID único da mensagem
    content: str                     # Conteúdo da mensagem
    sender: Contact                  # Remetente
    recipient: Contact               # Destinatário
    message_type: MessageType        # Tipo da mensagem
    timestamp: datetime              # Timestamp da mensagem
    status: MessageStatus            # Status de entrega
    metadata: Dict[str, Any]        # Metadados adicionais
    
    # Campos opcionais depois (com default)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    producer_id: Optional[str] = None  # ID do produtor (para deduplicação)
    correlation_id: Optional[str] = None  # ID de correlação
    sequence_number: Optional[int] = None  # Número de sequência
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.id:
            raise ValueError("ID é obrigatório")
        if not self.content:
            raise ValueError("Conteúdo é obrigatório")
        if not self.sender:
            raise ValueError("Remetente é obrigatório")
        if not self.recipient:
            raise ValueError("Destinatário é obrigatório")
        
        # Gerar trace_id se não fornecido
        if not self.trace_id:
            self.trace_id = str(uuid.uuid4())
    
    @property
    def is_incoming(self) -> bool:
        """Verifica se é mensagem recebida"""
        return self.sender.phone != self.recipient.phone
    
    @property
    def is_outgoing(self) -> bool:
        """Verifica se é mensagem enviada"""
        return self.sender.phone == self.recipient.phone
    
    @property
    def is_group_message(self) -> bool:
        """Verifica se é mensagem de grupo"""
        return self.recipient.is_group
    
    def get_idempotency_key(self) -> str:
        """Gera chave de idempotência única"""
        if self.producer_id and self.sequence_number:
            return f"{self.producer_id}:{self.sequence_number}"
        return f"{self.trace_id}:{self.timestamp.timestamp()}"
    
    def mark_as_sent(self):
        """Marca mensagem como enviada"""
        self.status = MessageStatus.SENT
        self.updated_at = datetime.now()
    
    def mark_as_delivered(self):
        """Marca mensagem como entregue"""
        self.status = MessageStatus.DELIVERED
        self.updated_at = datetime.now()
    
    def mark_as_read(self):
        """Marca mensagem como lida"""
        self.status = MessageStatus.READ
        self.updated_at = datetime.now()
    
    def mark_as_failed(self, error: str = None):
        """Marca mensagem como falhou"""
        self.status = MessageStatus.FAILED
        if error:
            self.metadata['error'] = error
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'content': self.content,
            'sender': self.sender.to_dict(),
            'recipient': self.recipient.to_dict(),
            'message_type': self.message_type.value,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status.value,
            'metadata': self.metadata,
            'trace_id': self.trace_id,
            'producer_id': self.producer_id,
            'correlation_id': self.correlation_id,
            'sequence_number': self.sequence_number,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Cria Message a partir de dicionário"""
        # Converter sender e recipient
        if 'sender' in data:
            data['sender'] = Contact.from_dict(data['sender'])
        if 'recipient' in data:
            data['recipient'] = Contact.from_dict(data['recipient'])
        
        # Converter message_type
        if 'message_type' in data:
            data['message_type'] = MessageType(data['message_type'])
        
        # Converter status
        if 'status' in data:
            data['status'] = MessageStatus(data['status'])
        
        # Converter timestamps
        if data.get('timestamp'):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)


class MediaMessage(Message):
    """Mensagem de mídia com idempotência"""
    
    def __init__(self, id: str, content: str, sender: Contact, recipient: Contact, 
                 message_type: MessageType, timestamp: datetime, status: MessageStatus, 
                 metadata: Dict[str, Any], media_path: str, **kwargs):
        """Inicializador customizado para MediaMessage"""
        # Chamar o __init__ da classe pai
        super().__init__(
            id=id,
            content=content,
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            timestamp=timestamp,
            status=status,
            metadata=metadata,
            **kwargs
        )
        
        # Definir campos específicos da MediaMessage
        self.media_path = media_path
        self.media_url = kwargs.get('media_url')
        self.media_size = kwargs.get('media_size')
        self.media_mime_type = kwargs.get('media_mime_type')
        self.caption = kwargs.get('caption')
        self.media_hash = kwargs.get('media_hash')
        self.media_storage_path = kwargs.get('media_storage_path')
        
        # Validação pós-inicialização
        if not self.media_path:
            raise ValueError("Caminho da mídia é obrigatório")
        
        # Definir tipo de mensagem baseado na extensão se não foi definido
        if not self.message_type or self.message_type == MessageType.TEXT:
            self.message_type = self._get_media_type()
    
    def _get_media_type(self) -> MessageType:
        """Determina tipo de mídia baseado na extensão"""
        import os
        ext = os.path.splitext(self.media_path)[1].lower()
        
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return MessageType.IMAGE
        elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
            return MessageType.VIDEO
        elif ext in ['.mp3', '.wav', '.ogg', '.m4a']:
            return MessageType.AUDIO
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.xlsx']:
            return MessageType.DOCUMENT
        else:
            return MessageType.DOCUMENT
    
    def get_media_idempotency_key(self) -> str:
        """Gera chave de idempotência específica para mídia"""
        if self.media_hash:
            return f"{self.producer_id}:{self.media_hash}"
        return self.get_idempotency_key()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        base_dict = super().to_dict()
        base_dict.update({
            'media_path': self.media_path,
            'media_url': self.media_url,
            'media_size': self.media_size,
            'media_mime_type': self.media_mime_type,
            'caption': self.caption,
            'media_hash': self.media_hash,
            'media_storage_path': self.media_storage_path
        })
        return base_dict


@dataclass
class Chat:
    """Chat/Conversa WhatsApp com status Kanban"""
    
    # Campos obrigatórios primeiro (sem default)
    chat_id: str
    
    # Campos opcionais depois (com default)
    status: KanbanStatus = KanbanStatus.NEW
    owner_id: Optional[str] = None
    last_message_at: Optional[datetime] = None
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    assigned_at: Optional[datetime] = None
    assigned_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    completed_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.chat_id:
            raise ValueError("Chat ID é obrigatório")
    
    @property
    def is_new(self) -> bool:
        """Verifica se é chat novo"""
        return self.status == KanbanStatus.NEW
    
    @property
    def is_active(self) -> bool:
        """Verifica se está em atendimento"""
        return self.status == KanbanStatus.ACTIVE
    
    @property
    def is_done(self) -> bool:
        """Verifica se está concluído"""
        return self.status == KanbanStatus.DONE
    
    def assign_to(self, owner_id: str, assigned_by: str = None):
        """Atribui chat para um atendente"""
        self.owner_id = owner_id
        self.status = KanbanStatus.ACTIVE
        self.assigned_at = datetime.now()
        self.assigned_by = assigned_by
        self.updated_at = datetime.now()
    
    def mark_as_done(self, completed_by: str = None):
        """Marca chat como concluído"""
        self.status = KanbanStatus.DONE
        self.completed_at = datetime.now()
        self.completed_by = completed_by
        self.updated_at = datetime.now()
    
    def reopen(self, reopened_by: str = None):
        """Reabre chat"""
        self.status = KanbanStatus.NEW
        self.owner_id = None
        self.assigned_at = None
        self.assigned_by = None
        self.completed_at = None
        self.completed_by = None
        self.updated_at = datetime.now()
    
    def update_last_message(self, timestamp: datetime):
        """Atualiza timestamp da última mensagem"""
        self.last_message_at = timestamp
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'chat_id': self.chat_id,
            'status': self.status.value,
            'owner_id': self.owner_id,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'trace_id': self.trace_id,
            'correlation_id': self.correlation_id,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'assigned_by': self.assigned_by,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'completed_by': self.completed_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chat':
        """Cria Chat a partir de dicionário"""
        # Converter status
        if 'status' in data:
            data['status'] = KanbanStatus(data['status'])
        
        # Converter timestamps
        if data.get('last_message_at'):
            data['last_message_at'] = datetime.fromisoformat(data['last_message_at'])
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('assigned_at'):
            data['assigned_at'] = datetime.fromisoformat(data['assigned_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        
        return cls(**data)


@dataclass
class SessionEvent:
    """Evento de sessão para auditoria com rastreamento"""
    
    session_id: str
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Campos de rastreamento
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None  # Usuário que disparou o evento
    
    # Campos de auditoria
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.session_id:
            raise ValueError("Session ID é obrigatório")
        if not self.event_type:
            raise ValueError("Tipo de evento é obrigatório")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'session_id': self.session_id,
            'event_type': self.event_type,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'trace_id': self.trace_id,
            'correlation_id': self.correlation_id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionEvent':
        """Cria SessionEvent a partir de dicionário"""
        # Converter timestamp
        if data.get('timestamp'):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return cls(**data)


@dataclass
class MessageDeliveryStatus:
    """Status de entrega de mensagem com rastreamento"""
    
    message_id: str
    status: MessageStatus
    timestamp: datetime
    details: Optional[str] = None
    
    # Campos de rastreamento
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    
    # Campos de auditoria
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.message_id:
            raise ValueError("Message ID é obrigatório")
        if not self.timestamp:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'message_id': self.message_id,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details,
            'trace_id': self.trace_id,
            'correlation_id': self.correlation_id,
            'updated_by': self.updated_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageDeliveryStatus':
        """Cria MessageDeliveryStatus a partir de dicionário"""
        # Converter status
        if 'status' in data:
            data['status'] = MessageStatus(data['status'])
        
        # Converter timestamp
        if data.get('timestamp'):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return cls(**data)
