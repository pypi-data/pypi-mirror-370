"""
Storage Django opcional para PyWhatsWeb

Este storage só funciona se o projeto que usar a biblioteca tiver Django instalado.
É uma implementação opcional para quem quiser usar Django ORM.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from .base import BaseStore
from ..models import Message, Contact, Group
from ..enums import KanbanStatus
from ..exceptions import StorageError


class DjangoORMStore(BaseStore):
    """Storage baseado em Django ORM (OPCIONAL)"""
    
    def __init__(self):
        # Verificar se Django está disponível
        try:
            import django
            from django.db import models
            from django.utils import timezone
            self._django_available = True
        except ImportError:
            self._django_available = False
            raise StorageError(
                "Django não está disponível. "
                "Este storage é opcional e só funciona em projetos Django. "
                "Use FileSystemStore para projetos sem Django."
            )
    
    def _get_models(self):
        """Retorna os models Django (deve ser implementado pelo usuário)"""
        if not hasattr(self, '_models_loaded'):
            # O usuário deve registrar os models manualmente
            raise StorageError(
                "Models Django não configurados. "
                "Use set_models() para registrar os models antes de usar este storage."
            )
        return self._models
    
    def set_models(self, session_model, message_model, contact_model, 
                   group_model, chat_model, event_model):
        """Configura os models Django (deve ser chamado pelo usuário)"""
        self._models = {
            'session': session_model,
            'message': message_model,
            'contact': contact_model,
            'group': group_model,
            'chat': chat_model,
            'event': event_model
        }
        self._models_loaded = True
    
    def save_message(self, message: Message) -> bool:
        """Salva uma mensagem"""
        try:
            models = self._get_models()
            
            # Buscar ou criar contatos
            sender, _ = models['contact'].objects.get_or_create(
                phone=message.sender.phone,
                defaults={'name': message.sender.name}
            )
            
            recipient, _ = models['contact'].objects.get_or_create(
                phone=message.recipient.phone,
                defaults={'name': message.recipient.name}
            )
            
            # Salvar mensagem
            message_obj = models['message'].objects.create(
                message_id=message.id,
                content=message.content,
                sender=sender,
                recipient=recipient,
                message_type=message.message_type.value,
                timestamp=message.timestamp,
                status=message.status.value,
                metadata=message.metadata
            )
            
            return True
            
        except Exception as e:
            raise StorageError(f"Erro ao salvar mensagem: {e}")
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """Recupera uma mensagem por ID"""
        try:
            models = self._get_models()
            message_obj = models['message'].objects.filter(message_id=message_id).first()
            if not message_obj:
                return None
            
            # Reconstruir objetos
            sender = Contact(
                phone=message_obj.sender.phone,
                name=message_obj.sender.name
            )
            recipient = Contact(
                phone=message_obj.recipient.phone,
                name=message_obj.recipient.name
            )
            
            message = Message(
                id=message_obj.message_id,
                content=message_obj.content,
                sender=sender,
                recipient=recipient,
                message_type=message_obj.message_type,
                timestamp=message_obj.timestamp
            )
            
            return message
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar mensagem: {e}")
    
    def get_chat_messages(self, chat_id: str, limit: int = 50) -> List[Message]:
        """Recupera mensagens de um chat"""
        try:
            models = self._get_models()
            message_objs = models['message'].objects.filter(
                recipient__phone=chat_id
            ).order_by('-timestamp')[:limit]
            
            messages = []
            for message_obj in message_objs:
                sender = Contact(
                    phone=message_obj.sender.phone,
                    name=message_obj.sender.name
                )
                recipient = Contact(
                    phone=message_obj.recipient.phone,
                    name=message_obj.recipient.name
                )
                
                message = Message(
                    id=message_obj.message_id,
                    content=message_obj.content,
                    sender=sender,
                    recipient=recipient,
                    message_type=message_obj.message_type,
                    timestamp=message_obj.timestamp
                )
                messages.append(message)
            
            return messages
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar mensagens do chat: {e}")
    
    def save_contact(self, contact: Contact) -> bool:
        """Salva um contato"""
        try:
            models = self._get_models()
            contact_obj, created = models['contact'].objects.update_or_create(
                phone=contact.phone,
                defaults={
                    'name': contact.name,
                    'is_group': contact.is_group,
                    'is_business': contact.is_business,
                    'profile_picture': contact.profile_picture,
                    'status': contact.status,
                    'last_seen': contact.last_seen
                }
            )
            
            return True
            
        except Exception as e:
            raise StorageError(f"Erro ao salvar contato: {e}")
    
    def get_contact(self, phone: str) -> Optional[Contact]:
        """Recupera um contato por telefone"""
        try:
            models = self._get_models()
            contact_obj = models['contact'].objects.filter(phone=phone).first()
            if not contact_obj:
                return None
            
            contact = Contact(
                phone=contact_obj.phone,
                name=contact_obj.name,
                is_group=contact_obj.is_group,
                is_business=contact_obj.is_business,
                profile_picture=contact_obj.profile_picture,
                status=contact_obj.status,
                last_seen=contact_obj.last_seen
            )
            
            return contact
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar contato: {e}")
    
    def save_group(self, group: Group) -> bool:
        """Salva um grupo"""
        try:
            models = self._get_models()
            group_obj, created = models['group'].objects.update_or_create(
                group_id=group.id,
                defaults={
                    'name': group.name,
                    'description': group.description,
                    'invite_link': group.invite_link,
                    'created_at': group.created_at,
                    'updated_at': group.updated_at
                }
            )
            
            # Adicionar participantes
            for participant in group.participants:
                contact, _ = models['contact'].objects.get_or_create(
                    phone=participant.phone,
                    defaults={'name': participant.name}
                )
                group_obj.participants.add(contact)
            
            # Adicionar admins
            for admin in group.admins:
                contact, _ = models['contact'].objects.get_or_create(
                    phone=admin.phone,
                    defaults={'name': admin.name}
                )
                group_obj.admins.add(contact)
            
            return True
            
        except Exception as e:
            raise StorageError(f"Erro ao salvar grupo: {e}")
    
    def get_group(self, group_id: str) -> Optional[Group]:
        """Recupera um grupo por ID"""
        try:
            models = self._get_models()
            group_obj = models['group'].objects.filter(group_id=group_id).first()
            if not group_obj:
                return None
            
            # Reconstruir participantes
            participants = [
                Contact(phone=p.phone, name=p.name) 
                for p in group_obj.participants.all()
            ]
            admins = [
                Contact(phone=a.phone, name=a.name) 
                for a in group_obj.admins.all()
            ]
            
            group = Group(
                id=group_obj.group_id,
                name=group_obj.name,
                participants=participants,
                admins=admins,
                description=group_obj.description,
                invite_link=group_obj.invite_link,
                created_at=group_obj.created_at,
                updated_at=group_obj.updated_at
            )
            
            return group
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar grupo: {e}")
    
    def update_chat_status(self, chat_id: str, status: KanbanStatus, 
                          owner_id: Optional[str] = None) -> bool:
        """Atualiza status de um chat no Kanban"""
        try:
            models = self._get_models()
            from django.utils import timezone
            
            chat_obj, created = models['chat'].objects.update_or_create(
                chat_id=chat_id,
                defaults={
                    'status': status.value,
                    'owner_id': owner_id,
                    'updated_at': timezone.now()
                }
            )
            
            return True
            
        except Exception as e:
            raise StorageError(f"Erro ao atualizar status do chat: {e}")
    
    def get_chat_status(self, chat_id: str) -> Optional[KanbanStatus]:
        """Recupera status de um chat"""
        try:
            models = self._get_models()
            chat_obj = models['chat'].objects.filter(chat_id=chat_id).first()
            if not chat_obj:
                return None
            
            return KanbanStatus(chat_obj.status)
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar status do chat: {e}")
    
    def get_chats_by_status(self, status: KanbanStatus) -> List[Dict[str, Any]]:
        """Recupera chats por status"""
        try:
            models = self._get_models()
            chat_objs = models['chat'].objects.filter(status=status.value)
            
            chats = []
            for chat_obj in chat_objs:
                chats.append({
                    'chat_id': chat_obj.chat_id,
                    'status': chat_obj.status,
                    'owner_id': chat_obj.owner_id,
                    'created_at': chat_obj.created_at.isoformat() if chat_obj.created_at else None,
                    'updated_at': chat_obj.updated_at.isoformat() if chat_obj.updated_at else None
                })
            
            return chats
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar chats por status: {e}")
    
    def save_session_event(self, session_id: str, event_type: str, 
                          data: Dict[str, Any]) -> bool:
        """Salva evento de sessão para auditoria"""
        try:
            models = self._get_models()
            from django.utils import timezone
            
            # Buscar sessão
            session_obj = models['session'].objects.filter(session_id=session_id).first()
            if not session_obj:
                # Criar sessão se não existir
                session_obj = models['session'].objects.create(
                    session_id=session_id,
                    status='connecting'
                )
            
            # Salvar evento
            models['event'].objects.create(
                session=session_obj,
                event_type=event_type,
                data=data,
                timestamp=timezone.now()
            )
            
            return True
            
        except Exception as e:
            raise StorageError(f"Erro ao salvar evento de sessão: {e}")
    
    def get_session_events(self, session_id: str, 
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Recupera eventos de uma sessão"""
        try:
            models = self._get_models()
            session_obj = models['session'].objects.filter(session_id=session_id).first()
            if not session_obj:
                return []
            
            event_objs = models['event'].objects.filter(
                session=session_obj
            ).order_by('-timestamp')[:limit]
            
            events = []
            for event_obj in event_objs:
                events.append({
                    'session_id': session_id,
                    'event_type': event_obj.event_type,
                    'timestamp': event_obj.timestamp.isoformat(),
                    'data': event_obj.data
                })
            
            return events
            
        except Exception as e:
            raise StorageError(f"Erro ao recuperar eventos da sessão: {e}")
    
    def close(self):
        """Fecha conexões/recursos"""
        # Django ORM não precisa fechar conexões manualmente
        pass
