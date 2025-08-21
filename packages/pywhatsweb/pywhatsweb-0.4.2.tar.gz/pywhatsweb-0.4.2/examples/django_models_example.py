#!/usr/bin/env python3
"""
Exemplo de models Django para PyWhatsWeb (OPCIONAL)

Este arquivo mostra como criar os models Django necessários para usar DjangoORMStore.
É APENAS um exemplo - o usuário pode adaptar para seu projeto Django.
"""

# Este arquivo é APENAS um exemplo para projetos Django
# A biblioteca funciona perfeitamente sem Django usando FileSystemStore

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class WhatsAppSession(models.Model):
    """Sessão WhatsApp ativa"""
    
    session_id = models.CharField(max_length=100, unique=True, primary_key=True)
    status = models.CharField(max_length=20, default='connecting')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'whatsapp_sessions'
        verbose_name = 'Sessão WhatsApp'
        verbose_name_plural = 'Sessões WhatsApp'
    
    def __str__(self):
        return f"Sessão {self.session_id} ({self.status})"


class WhatsAppContact(models.Model):
    """Contato WhatsApp"""
    
    phone = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    is_group = models.BooleanField(default=False)
    is_business = models.BooleanField(default=False)
    profile_picture = models.URLField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'whatsapp_contacts'
        verbose_name = 'Contato WhatsApp'
        verbose_name_plural = 'Contatos WhatsApp'
    
    def __str__(self):
        return f"{self.name or 'Sem nome'} ({self.phone})"


class WhatsAppGroup(models.Model):
    """Grupo WhatsApp"""
    
    group_id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    invite_link = models.URLField(blank=True, null=True)
    participants = models.ManyToManyField(WhatsAppContact, related_name='groups')
    admins = models.ManyToManyField(WhatsAppContact, related_name='admin_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'whatsapp_groups'
        verbose_name = 'Grupo WhatsApp'
        verbose_name_plural = 'Grupos WhatsApp'
    
    def __str__(self):
        return f"Grupo {self.name} ({self.group_id})"


class WhatsAppMessage(models.Model):
    """Mensagem WhatsApp"""
    
    message_id = models.CharField(max_length=100, unique=True, primary_key=True)
    content = models.TextField()
    sender = models.ForeignKey(WhatsAppContact, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(WhatsAppContact, on_delete=models.CASCADE, related_name='received_messages')
    message_type = models.CharField(max_length=20, default='text')
    timestamp = models.DateTimeField()
    status = models.CharField(max_length=20, default='pending')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'whatsapp_messages'
        verbose_name = 'Mensagem WhatsApp'
        verbose_name_plural = 'Mensagens WhatsApp'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Mensagem de {self.sender.phone} para {self.recipient.phone}"


class WhatsAppChat(models.Model):
    """Chat/Conversa WhatsApp com status Kanban"""
    
    chat_id = models.CharField(max_length=100, unique=True, primary_key=True)
    status = models.CharField(max_length=20, default='NEW')  # NEW, ACTIVE, DONE
    owner_id = models.CharField(max_length=100, blank=True, null=True)  # ID do atendente
    last_message_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'whatsapp_chats'
        verbose_name = 'Chat WhatsApp'
        verbose_name_plural = 'Chats WhatsApp'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat {self.chat_id} ({self.status})"


class WhatsAppSessionEvent(models.Model):
    """Evento de sessão para auditoria"""
    
    session = models.ForeignKey(WhatsAppSession, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50)  # qr, authenticated, ready, message, disconnected
    data = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'whatsapp_session_events'
        verbose_name = 'Evento de Sessão'
        verbose_name_plural = 'Eventos de Sessão'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Evento {self.event_type} em {self.session.session_id}"


class WhatsAppAttendant(models.Model):
    """Atendente do sistema"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='whatsapp_attendant')
    is_active = models.BooleanField(default=True)
    max_concurrent_chats = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'whatsapp_attendants'
        verbose_name = 'Atendente WhatsApp'
        verbose_name_plural = 'Atendentes WhatsApp'
    
    def __str__(self):
        return f"Atendente {self.user.username}"
    
    @property
    def current_chats(self):
        """Retorna número de chats ativos"""
        return WhatsAppChat.objects.filter(
            owner_id=str(self.user.id),
            status='ACTIVE'
        ).count()
    
    def can_take_chat(self):
        """Verifica se pode assumir novo chat"""
        return self.current_chats < self.max_concurrent_chats


# ============================================================================
# COMO USAR ESTES MODELS
# ============================================================================

"""
Para usar estes models em seu projeto Django:

1. Copie os models para seu app Django
2. Crie e execute as migrações:
   python manage.py makemigrations
   python manage.py migrate

3. Use com PyWhatsWeb:

from pywhatsweb import WhatsWebManager, DjangoORMStore
from .models import (WhatsAppSession, WhatsAppMessage, WhatsAppContact,
                     WhatsAppGroup, WhatsAppChat, WhatsAppSessionEvent)

# Criar manager
manager = WhatsWebManager(
    sidecar_host="localhost",
    sidecar_port=3000,
    api_key="sua-api-key",
    storage=DjangoORMStore()
)

# Configurar models
manager.storage.set_models(
    session_model=WhatsAppSession,
    message_model=WhatsAppMessage,
    contact_model=WhatsAppContact,
    group_model=WhatsAppGroup,
    chat_model=WhatsAppChat,
    event_model=WhatsAppSessionEvent
)

# Usar normalmente
session = manager.create_session("sessao_123")
session.start()
"""

if __name__ == "__main__":
    print("📋 Exemplo de models Django para PyWhatsWeb")
    print("=" * 50)
    print("Este arquivo é APENAS um exemplo!")
    print("A biblioteca funciona perfeitamente SEM Django usando FileSystemStore.")
    print("\nPara usar com Django:")
    print("1. Copie os models para seu app Django")
    print("2. Execute as migrações")
    print("3. Configure o storage DjangoORMStore")
    print("\nPara usar SEM Django:")
    print("Use FileSystemStore (padrão) - funciona em qualquer projeto Python!")
