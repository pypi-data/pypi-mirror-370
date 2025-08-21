"""
Storage de filesystem para PyWhatsWeb
"""

import os
import json
import pickle
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from .base import BaseStore
from ..models import Message, Contact, Group
from ..enums import KanbanStatus
from ..exceptions import StorageError


class FileSystemStore(BaseStore):
    """Storage baseado em filesystem"""
    
    def __init__(self, base_dir: str = "./pywhatsweb_data"):
        self.base_dir = Path(base_dir)
        self.messages_dir = self.base_dir / "messages"
        self.contacts_dir = self.base_dir / "contacts"
        self.groups_dir = self.base_dir / "groups"
        self.chats_dir = self.base_dir / "chats"
        self.events_dir = self.base_dir / "events"
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Cria diretórios necessários"""
        try:
            for directory in [self.messages_dir, self.contacts_dir, 
                            self.groups_dir, self.chats_dir, self.events_dir]:
                directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise StorageError(f"Erro ao criar diretórios: {e}")
    
    def save_message(self, message: Message) -> bool:
        """Salva uma mensagem"""
        try:
            # Criar diretório do chat se não existir
            chat_dir = self.messages_dir / message.recipient.phone
            chat_dir.mkdir(parents=True, exist_ok=True)
            
            # Salvar mensagem
            message_file = chat_dir / f"{message.id}.json"
            message_data = {
                'id': message.id,
                'content': message.content,
                'sender_phone': message.sender.phone,
                'sender_name': message.sender.name,
                'recipient_phone': message.recipient.phone,
                'recipient_name': message.recipient.name,
                'message_type': message.message_type.value,
                'timestamp': message.timestamp.isoformat(),
                'status': message.status.value,
                'metadata': message.metadata
            }
            
            with open(message_file, 'w', encoding='utf-8') as f:
                json.dump(message_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            raise StorageError(f"Erro ao salvar mensagem: {e}")
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """Recupera uma mensagem por ID"""
        try:
            # Buscar em todos os chats
            for chat_dir in self.messages_dir.iterdir():
                if chat_dir.is_dir():
                    message_file = chat_dir / f"{message_id}.json"
                    if message_file.exists():
                        with open(message_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Reconstruir objetos
                        sender = Contact(phone=data['sender_phone'], name=data['sender_name'])
                        recipient = Contact(phone=data['recipient_phone'], name=data['recipient_name'])
                        
                        message = Message(
                            id=data['id'],
                            content=data['content'],
                            sender=sender,
                            recipient=recipient,
                            message_type=data['message_type'],
                            timestamp=datetime.fromisoformat(data['timestamp'])
                        )
                        return message
            
            return None
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar mensagem: {e}")
    
    def get_chat_messages(self, chat_id: str, limit: int = 50) -> List[Message]:
        """Recupera mensagens de um chat"""
        try:
            chat_dir = self.messages_dir / chat_id
            if not chat_dir.exists():
                return []
            
            messages = []
            message_files = sorted(chat_dir.glob("*.json"), 
                                 key=lambda x: x.stat().st_mtime, reverse=True)
            
            for message_file in message_files[:limit]:
                try:
                    with open(message_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    sender = Contact(phone=data['sender_phone'], name=data['sender_name'])
                    recipient = Contact(phone=data['recipient_phone'], name=data['recipient_name'])
                    
                    message = Message(
                        id=data['id'],
                        content=data['content'],
                        sender=sender,
                        recipient=recipient,
                        message_type=data['message_type'],
                        timestamp=datetime.fromisoformat(data['timestamp'])
                    )
                    messages.append(message)
                    
                except Exception as e:
                    print(f"Erro ao processar mensagem {message_file}: {e}")
                    continue
            
            return messages
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar mensagens do chat: {e}")
    
    def save_contact(self, contact: Contact) -> bool:
        """Salva um contato"""
        try:
            contact_file = self.contacts_dir / f"{contact.phone}.json"
            contact_data = {
                'phone': contact.phone,
                'name': contact.name,
                'is_group': contact.is_group,
                'is_business': contact.is_business,
                'profile_picture': contact.profile_picture,
                'status': contact.status,
                'last_seen': contact.last_seen.isoformat() if contact.last_seen else None
            }
            
            with open(contact_file, 'w', encoding='utf-8') as f:
                json.dump(contact_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            raise StorageError(f"Erro ao salvar contato: {e}")
    
    def get_contact(self, phone: str) -> Optional[Contact]:
        """Recupera um contato por telefone"""
        try:
            contact_file = self.contacts_dir / f"{phone}.json"
            if not contact_file.exists():
                return None
            
            with open(contact_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            contact = Contact(
                phone=data['phone'],
                name=data['name'],
                is_group=data['is_group'],
                is_business=data['is_business'],
                profile_picture=data['profile_picture'],
                status=data['status']
            )
            
            if data['last_seen']:
                contact.last_seen = datetime.fromisoformat(data['last_seen'])
            
            return contact
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar contato: {e}")
    
    def save_group(self, group: Group) -> bool:
        """Salva um grupo"""
        try:
            group_file = self.groups_dir / f"{group.id}.json"
            group_data = {
                'id': group.id,
                'name': group.name,
                'participants': [p.phone for p in group.participants],
                'admins': [a.phone for a in group.admins],
                'description': group.description,
                'invite_link': group.invite_link,
                'created_at': group.created_at.isoformat() if group.created_at else None,
                'updated_at': group.updated_at.isoformat() if group.updated_at else None
            }
            
            with open(group_file, 'w', encoding='utf-8') as f:
                json.dump(group_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            raise StorageError(f"Erro ao salvar grupo: {e}")
    
    def get_group(self, group_id: str) -> Optional[Group]:
        """Recupera um grupo por ID"""
        try:
            group_file = self.groups_dir / f"{group_id}.json"
            if not group_file.exists():
                return None
            
            with open(group_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruir participantes
            participants = [Contact(phone=p) for p in data['participants']]
            admins = [Contact(phone=a) for a in data['admins']]
            
            group = Group(
                id=data['id'],
                name=data['name'],
                participants=participants,
                admins=admins,
                description=data['description'],
                invite_link=data['invite_link']
            )
            
            if data['created_at']:
                group.created_at = datetime.fromisoformat(data['created_at'])
            if data['updated_at']:
                group.updated_at = datetime.fromisoformat(data['updated_at'])
            
            return group
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar grupo: {e}")
    
    def update_chat_status(self, chat_id: str, status: KanbanStatus, 
                          owner_id: Optional[str] = None) -> bool:
        """Atualiza status de um chat no Kanban"""
        try:
            chat_file = self.chats_dir / f"{chat_id}.json"
            
            chat_data = {
                'chat_id': chat_id,
                'status': status.value,
                'owner_id': owner_id,
                'updated_at': datetime.now().isoformat()
            }
            
            # Carregar dados existentes se arquivo existir
            if chat_file.exists():
                with open(chat_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    chat_data.update(existing_data)
            
            with open(chat_file, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            raise StorageError(f"Erro ao atualizar status do chat: {e}")
    
    def get_chat_status(self, chat_id: str) -> Optional[KanbanStatus]:
        """Recupera status de um chat"""
        try:
            chat_file = self.chats_dir / f"{chat_id}.json"
            if not chat_file.exists():
                return None
            
            with open(chat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return KanbanStatus(data['status'])
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar status do chat: {e}")
    
    def get_chats_by_status(self, status: KanbanStatus) -> List[Dict[str, Any]]:
        """Recupera chats por status"""
        try:
            chats = []
            
            for chat_file in self.chats_dir.glob("*.json"):
                try:
                    with open(chat_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if data.get('status') == status.value:
                        chats.append(data)
                        
                except Exception as e:
                    print(f"Erro ao processar chat {chat_file}: {e}")
                    continue
            
            return chats
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar chats por status: {e}")
    
    def save_session_event(self, session_id: str, event_type: str, 
                          data: Dict[str, Any]) -> bool:
        """Salva evento de sessão para auditoria"""
        try:
            events_dir = self.events_dir / session_id
            events_dir.mkdir(parents=True, exist_ok=True)
            
            event_file = events_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{event_type}.json"
            
            event_data = {
                'session_id': session_id,
                'event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            with open(event_file, 'w', encoding='utf-8') as f:
                json.dump(event_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            raise StorageError(f"Erro ao salvar evento de sessão: {e}")
    
    def get_session_events(self, session_id: str, 
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Recupera eventos de uma sessão"""
        try:
            events_dir = self.events_dir / session_id
            if not events_dir.exists():
                return []
            
            events = []
            event_files = sorted(events_dir.glob("*.json"), 
                               key=lambda x: x.stat().st_mtime, reverse=True)
            
            for event_file in event_files[:limit]:
                try:
                    with open(event_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    events.append(data)
                    
                except Exception as e:
                    print(f"Erro ao processar evento {event_file}: {e}")
                    continue
            
            return events
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar eventos da sessão: {e}")
    
    def close(self):
        """Fecha conexões/recursos"""
        # Filesystem não precisa fechar conexões
        pass
