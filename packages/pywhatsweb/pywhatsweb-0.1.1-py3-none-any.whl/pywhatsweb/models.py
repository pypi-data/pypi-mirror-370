"""
Modelos de dados para PyWhatsWeb
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """Tipos de mensagem"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"
    REACTION = "reaction"


class MessageStatus(Enum):
    """Status das mensagens"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class Contact:
    """Modelo de contato"""
    phone: str
    name: Optional[str] = None
    is_group: bool = False
    is_business: bool = False
    profile_picture: Optional[str] = None
    status: Optional[str] = None
    last_seen: Optional[datetime] = None
    
    def __post_init__(self):
        """Valida e formata o telefone"""
        if not self.phone:
            raise ValueError("Telefone é obrigatório")
        
        # Remove caracteres especiais e formata
        self.phone = ''.join(filter(str.isdigit, self.phone))
        
        # Adiciona código do país se não tiver
        if not self.phone.startswith('55') and len(self.phone) <= 11:
            self.phone = '55' + self.phone


@dataclass
class Group:
    """Modelo de grupo"""
    id: str
    name: str
    participants: List[Contact] = field(default_factory=list)
    admins: List[Contact] = field(default_factory=list)
    description: Optional[str] = None
    invite_link: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def add_participant(self, contact: Contact):
        """Adiciona participante ao grupo"""
        if contact not in self.participants:
            self.participants.append(contact)
    
    def remove_participant(self, contact: Contact):
        """Remove participante do grupo"""
        if contact in self.participants:
            self.participants.remove(contact)
    
    def is_admin(self, contact: Contact) -> bool:
        """Verifica se o contato é admin"""
        return contact in self.admins


@dataclass
class MediaMessage:
    """Modelo para mensagens de mídia"""
    file_path: str
    mime_type: str
    file_size: int
    caption: Optional[str] = None
    thumbnail: Optional[str] = None
    
    def __post_init__(self):
        """Valida o arquivo"""
        import os
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.file_path}")


@dataclass
class Message:
    """Modelo de mensagem"""
    id: str
    content: str
    sender: Contact
    recipient: Contact
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime = field(default_factory=datetime.now)
    status: MessageStatus = MessageStatus.PENDING
    media: Optional[MediaMessage] = None
    reply_to: Optional['Message'] = None
    forwarded: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validações básicas"""
        if not self.content and not self.media:
            raise ValueError("Mensagem deve ter conteúdo ou mídia")
        
        if not self.id:
            self.id = f"msg_{int(self.timestamp.timestamp())}_{hash(self.content)}"
    
    def is_from_me(self) -> bool:
        """Verifica se a mensagem é do usuário atual"""
        # Implementar lógica para identificar mensagens próprias
        return False
    
    def is_group_message(self) -> bool:
        """Verifica se é mensagem de grupo"""
        return self.recipient.is_group
    
    def get_formatted_content(self) -> str:
        """Retorna conteúdo formatado"""
        if self.media:
            media_info = f"[{self.message_type.value.upper()}]"
            if self.content:
                return f"{media_info} {self.content}"
            return media_info
        return self.content


@dataclass
class Location:
    """Modelo de localização"""
    latitude: float
    longitude: float
    name: Optional[str] = None
    address: Optional[str] = None
    
    def __post_init__(self):
        """Valida coordenadas"""
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude deve estar entre -90 e 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude deve estar entre -180 e 180")


@dataclass
class Reaction:
    """Modelo de reação"""
    emoji: str
    sender: Contact
    message: Message
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Valida emoji"""
        if not self.emoji:
            raise ValueError("Emoji é obrigatório")
