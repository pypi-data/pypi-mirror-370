"""
Interface base para storage pluggable
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..models import Message, Contact, Group
from ..enums import KanbanStatus


class BaseStore(ABC):
    """Interface base para storage pluggable"""
    
    @abstractmethod
    def save_message(self, message: Message) -> bool:
        """Salva uma mensagem"""
        pass
    
    @abstractmethod
    def get_message(self, message_id: str) -> Optional[Message]:
        """Recupera uma mensagem por ID"""
        pass
    
    @abstractmethod
    def get_chat_messages(self, chat_id: str, limit: int = 50) -> List[Message]:
        """Recupera mensagens de um chat"""
        pass
    
    @abstractmethod
    def save_contact(self, contact: Contact) -> bool:
        """Salva um contato"""
        pass
    
    @abstractmethod
    def get_contact(self, phone: str) -> Optional[Contact]:
        """Recupera um contato por telefone"""
        pass
    
    @abstractmethod
    def save_group(self, group: Group) -> bool:
        """Salva um grupo"""
        pass
    
    @abstractmethod
    def get_group(self, group_id: str) -> Optional[Group]:
        """Recupera um grupo por ID"""
        pass
    
    @abstractmethod
    def update_chat_status(self, chat_id: str, status: KanbanStatus, 
                          owner_id: Optional[str] = None) -> bool:
        """Atualiza status de um chat no Kanban"""
        pass
    
    @abstractmethod
    def get_chat_status(self, chat_id: str) -> Optional[KanbanStatus]:
        """Recupera status de um chat"""
        pass
    
    @abstractmethod
    def get_chats_by_status(self, status: KanbanStatus) -> List[Dict[str, Any]]:
        """Recupera chats por status"""
        pass
    
    @abstractmethod
    def save_session_event(self, session_id: str, event_type: str, 
                          data: Dict[str, Any]) -> bool:
        """Salva evento de sessão para auditoria"""
        pass
    
    @abstractmethod
    def get_session_events(self, session_id: str, 
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Recupera eventos de uma sessão"""
        pass
    
    @abstractmethod
    def close(self):
        """Fecha conexões/recursos"""
        pass
