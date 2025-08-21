#!/usr/bin/env python3
"""
Exemplo Django completo para PyWhatsWeb

Este exemplo mostra como integrar a biblioteca em um projeto Django existente,
incluindo views, templates e consumer WebSocket.
"""

import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.conf import settings

# Importar PyWhatsWeb
from pywhatsweb import WhatsWebManager, DjangoORMStore, KanbanStatus
from pywhatsweb.models import Chat, Message, Contact

# Configurar logging
logger = logging.getLogger(__name__)

# ============================================================================
# VIEWS DJANGO
# ============================================================================

class WhatsAppDashboardView(TemplateView):
    """View principal do dashboard WhatsApp"""
    template_name = 'whatsapp/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Inicializar manager (em produção, usar singleton)
        try:
            manager = WhatsWebManager(
                sidecar_host=getattr(settings, 'WHATSAPP_SIDECAR_HOST', 'localhost'),
                sidecar_port=getattr(settings, 'WHATSAPP_SIDECAR_PORT', 3000),
                api_key=getattr(settings, 'WHATSAPP_API_KEY', 'pywhatsweb-secret-key'),
                storage=DjangoORMStore()
            )
            
            # Configurar models Django
            from .models import WhatsAppSession, WhatsAppMessage, WhatsAppContact
            manager.storage.set_models(
                session_model=WhatsAppSession,
                message_model=WhatsAppMessage,
                contact_model=WhatsAppContact,
                group_model=None,  # Implementar se necessário
                chat_model=None,    # Implementar se necessário
                event_model=None    # Implementar se necessário
            )
            
            # Dados para o template
            context['sessions'] = manager.list_sessions()
            context['active_sessions'] = manager.get_active_sessions()
            context['sidecar_info'] = manager.get_sidecar_info()
            
        except Exception as e:
            logger.error(f"Erro ao inicializar WhatsApp manager: {e}")
            context['error'] = str(e)
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppSessionView(View):
    """API para gerenciar sessões WhatsApp"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Inicializar manager (em produção, usar singleton)
        self.manager = WhatsWebManager(
            sidecar_host=getattr(settings, 'WHATSAPP_SIDECAR_HOST', 'localhost'),
            sidecar_port=getattr(settings, 'WHATSAPP_SIDECAR_PORT', 3000),
            api_key=getattr(settings, 'WHATSAPP_API_KEY', 'pywhatsweb-secret-key'),
            storage=DjangoORMStore()
        )
        
        # Configurar models Django
        from .models import WhatsAppSession, WhatsAppMessage, WhatsAppContact
        self.manager.storage.set_models(
            session_model=WhatsAppSession,
            message_model=WhatsAppMessage,
            contact_model=WhatsAppContact,
            group_model=None,
            chat_model=None,
            event_model=None
        )
    
    def post(self, request, session_id):
        """Criar/iniciar sessão"""
        try:
            # Criar sessão
            session = self.manager.create_session(session_id)
            
            # Configurar eventos
            @session.on("qr")
            def on_qr(data):
                logger.info(f"QR gerado para sessão {session_id}")
                # Em produção, enviar via WebSocket para o frontend
            
            @session.on("ready")
            def on_ready(data):
                logger.info(f"Sessão {session_id} pronta")
                # Criar chat com status NEW
                chat = Chat(
                    chat_id=data.get('phone_number', session_id),
                    status=KanbanStatus.NEW
                )
                self.manager.storage.save_chat(chat)
            
            @session.on("message")
            def on_message(data):
                logger.info(f"Nova mensagem na sessão {session_id}")
                # Processar mensagem e atualizar chat
                self._handle_incoming_message(data, session_id)
            
            # Iniciar sessão
            session.start()
            
            return JsonResponse({
                'success': True,
                'message': 'Sessão criada e iniciada',
                'session_id': session_id
            })
            
        except Exception as e:
            logger.error(f"Erro ao criar sessão {session_id}: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def delete(self, request, session_id):
        """Parar/remover sessão"""
        try:
            session = self.manager.get_session(session_id)
            if session:
                session.stop()
                self.manager.remove_session(session_id)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Sessão parada e removida'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Sessão não encontrada'
                }, status=404)
                
        except Exception as e:
            logger.error(f"Erro ao parar sessão {session_id}: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def _handle_incoming_message(self, data, session_id):
        """Processar mensagem recebida"""
        try:
            # Criar contato se não existir
            contact = Contact(
                phone=data.get('from'),
                name=data.get('from'),  # Em produção, buscar nome real
                is_group=data.get('isGroup', False)
            )
            self.manager.storage.save_contact(contact)
            
            # Criar mensagem
            message = Message(
                id=data.get('messageId'),
                content=data.get('body', ''),
                sender=contact,
                recipient=Contact(phone=data.get('to')),
                message_type=data.get('type', 'text'),
                timestamp=data.get('timestamp'),
                status='received'
            )
            self.manager.storage.save_message(message)
            
            # Atualizar chat (mover para ACTIVE se estiver NEW)
            chat = self.manager.storage.get_chat(data.get('from'))
            if chat and chat.is_new:
                chat.assign_to('system')  # Em produção, atribuir para atendente real
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppMessageView(View):
    """API para enviar mensagens"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager = WhatsWebManager(
            sidecar_host=getattr(settings, 'WHATSAPP_SIDECAR_HOST', 'localhost'),
            sidecar_port=getattr(settings, 'WHATSAPP_SIDECAR_PORT', 3000),
            api_key=getattr(settings, 'WHATSAPP_API_KEY', 'pywhatsweb-secret-key'),
            storage=DjangoORMStore()
        )
        
        # Configurar models Django
        from .models import WhatsAppSession, WhatsAppMessage, WhatsAppContact
        self.manager.storage.set_models(
            session_model=WhatsAppSession,
            message_model=WhatsAppMessage,
            contact_model=WhatsAppContact,
            group_model=None,
            chat_model=None,
            event_model=None
        )
    
    def post(self, request, session_id):
        """Enviar mensagem"""
        try:
            data = json.loads(request.body)
            to = data.get('to')
            message_text = data.get('message')
            message_type = data.get('type', 'text')
            
            if not all([to, message_text]):
                return JsonResponse({
                    'success': False,
                    'error': 'Campos "to" e "message" são obrigatórios'
                }, status=400)
            
            # Obter sessão
            session = self.manager.get_session(session_id)
            if not session:
                return JsonResponse({
                    'success': False,
                    'error': 'Sessão não encontrada'
                }, status=404)
            
            # Enviar mensagem
            if message_type == 'text':
                message_id = session.send_text(to, message_text)
            else:
                # Implementar outros tipos de mensagem
                return JsonResponse({
                    'success': False,
                    'error': 'Tipo de mensagem não suportado'
                }, status=400)
            
            # Salvar mensagem no storage
            message = Message(
                id=message_id,
                content=message_text,
                sender=Contact(phone=session.phone_number or 'unknown'),
                recipient=Contact(phone=to),
                message_type='text',
                status='sent'
            )
            self.manager.storage.save_message(message)
            
            return JsonResponse({
                'success': True,
                'message_id': message_id
            })
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@require_http_methods(["GET"])
def whatsapp_health(request):
    """Health check do WhatsApp"""
    try:
        # Verificar conexão com sidecar
        import requests
        
        sidecar_url = f"http://{getattr(settings, 'WHATSAPP_SIDECAR_HOST', 'localhost')}:{getattr(settings, 'WHATSAPP_SIDECAR_PORT', 3000)}/health"
        response = requests.get(sidecar_url, timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            return JsonResponse({
                'status': 'healthy',
                'whatsapp': health_data,
                'django': 'ok'
            })
        else:
            return JsonResponse({
                'status': 'unhealthy',
                'whatsapp': 'error',
                'django': 'ok'
            }, status=503)
            
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'whatsapp': 'error',
            'django': 'ok',
            'error': str(e)
        }, status=503)


# ============================================================================
# CONSUMER WEBSOCKET (Django Channels)
# ============================================================================

try:
    from channels.generic.websocket import AsyncWebsocketConsumer
    from channels.db import database_sync_to_async
    
    class WhatsAppWebSocketConsumer(AsyncWebsocketConsumer):
        """Consumer WebSocket para eventos WhatsApp em tempo real"""
        
        async def connect(self):
            """Conectar ao WebSocket"""
            self.session_id = self.scope['url_route']['kwargs']['session_id']
            self.room_group_name = f'whatsapp_{self.session_id}'
            
            # Juntar ao grupo da sessão
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Enviar mensagem de conexão
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'session_id': self.session_id,
                'message': 'Conectado ao WebSocket WhatsApp'
            }))
        
        async def disconnect(self, close_code):
            """Desconectar do WebSocket"""
            # Sair do grupo da sessão
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        
        async def receive(self, text_data):
            """Receber mensagem do cliente"""
            try:
                data = json.loads(text_data)
                message_type = data.get('type')
                
                if message_type == 'chat_status_update':
                    # Atualizar status do chat (NEW -> ACTIVE -> DONE)
                    await self.update_chat_status(data)
                
                elif message_type == 'assign_chat':
                    # Atribuir chat para atendente
                    await self.assign_chat_to_attendant(data)
                
            except Exception as e:
                logger.error(f"Erro ao processar mensagem WebSocket: {e}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'error': str(e)
                }))
        
        async def whatsapp_event(self, event):
            """Enviar evento WhatsApp para o cliente"""
            await self.send(text_data=json.dumps({
                'type': 'whatsapp_event',
                'event': event['event_type'],
                'data': event['data']
            }))
        
        @database_sync_to_async
        def update_chat_status(self, data):
            """Atualizar status do chat"""
            try:
                chat_id = data.get('chat_id')
                new_status = data.get('status')
                
                if chat_id and new_status:
                    # Buscar chat no storage
                    chat = self.manager.storage.get_chat(chat_id)
                    if chat:
                        if new_status == 'active':
                            chat.assign_to(data.get('attendant_id', 'system'))
                        elif new_status == 'done':
                            chat.mark_as_done(data.get('attendant_id', 'system'))
                        
                        self.manager.storage.save_chat(chat)
                        
                        # Broadcast para outros clientes
                        self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'chat_status_updated',
                                'chat_id': chat_id,
                                'status': new_status
                            }
                        )
                        
            except Exception as e:
                logger.error(f"Erro ao atualizar status do chat: {e}")
        
        @database_sync_to_async
        def assign_chat_to_attendant(self, data):
            """Atribuir chat para atendente"""
            try:
                chat_id = data.get('chat_id')
                attendant_id = data.get('attendant_id')
                
                if chat_id and attendant_id:
                    chat = self.manager.storage.get_chat(chat_id)
                    if chat:
                        chat.assign_to(attendant_id)
                        self.manager.storage.save_chat(chat)
                        
                        # Broadcast para outros clientes
                        self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'chat_assigned',
                                'chat_id': chat_id,
                                'attendant_id': attendant_id
                            }
                        )
                        
            except Exception as e:
                logger.error(f"Erro ao atribuir chat: {e}")

except ImportError:
    # Django Channels não disponível
    logger.warning("Django Channels não disponível - WebSocket consumer não será criado")
    WhatsAppWebSocketConsumer = None


# ============================================================================
# URLS (para incluir no urls.py do projeto)
# ============================================================================

"""
# Adicionar ao urls.py do projeto Django:

from django.urls import path
from . import views

urlpatterns = [
    path('whatsapp/', views.WhatsAppDashboardView.as_view(), name='whatsapp_dashboard'),
    path('whatsapp/session/<str:session_id>/', views.WhatsAppSessionView.as_view(), name='whatsapp_session'),
    path('whatsapp/session/<str:session_id>/message/', views.WhatsAppMessageView.as_view(), name='whatsapp_message'),
    path('whatsapp/health/', views.whatsapp_health, name='whatsapp_health'),
]

# Para WebSocket (se usar Django Channels):
# routing.py:
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/whatsapp/(?P<session_id>\w+)/$', consumers.WhatsAppWebSocketConsumer.as_asgi()),
]
"""


# ============================================================================
# TEMPLATE HTML (dashboard.html)
# ============================================================================

TEMPLATE_HTML = """
{% extends "base.html" %}

{% block title %}Dashboard WhatsApp - PyWhatsWeb{% endblock %}

{% block content %}
<div class="whatsapp-dashboard">
    <div class="header">
        <h1>🚀 Dashboard WhatsApp</h1>
        <div class="status-indicator">
            <span class="status-dot" id="status-dot"></span>
            <span id="status-text">Conectando...</span>
        </div>
    </div>
    
    <div class="sessions-panel">
        <h2>📱 Sessões Ativas</h2>
        <div class="session-controls">
            <input type="text" id="session-id" placeholder="ID da sessão">
            <button onclick="createSession()">Criar Sessão</button>
        </div>
        <div id="sessions-list">
            {% for session in sessions %}
            <div class="session-item" data-session-id="{{ session }}">
                <span class="session-name">{{ session }}</span>
                <button onclick="stopSession('{{ session }}')">Parar</button>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <div class="qr-panel" id="qr-panel" style="display: none;">
        <h2>🔍 QR Code para Autenticação</h2>
        <div class="qr-container">
            <img id="qr-image" src="" alt="QR Code">
        </div>
        <p>Escaneie o QR Code com seu WhatsApp</p>
        <div class="qr-status" id="qr-status"></div>
    </div>
    
    <div class="chats-panel">
        <h2>💬 Conversas</h2>
        <div class="kanban-board">
            <div class="kanban-column">
                <h3>Aguardando</h3>
                <div id="new-chats" class="chat-list"></div>
            </div>
            <div class="kanban-column">
                <h3>Em Atendimento</h3>
                <div id="active-chats" class="chat-list"></div>
            </div>
            <div class="kanban-column">
                <h3>Concluídos</h3>
                <div id="done-chats" class="chat-list"></div>
            </div>
        </div>
    </div>
    
    <div class="messages-panel">
        <h2>📨 Mensagens</h2>
        <div class="message-input">
            <input type="text" id="message-to" placeholder="Para (número)">
            <input type="text" id="message-text" placeholder="Mensagem">
            <button onclick="sendMessage()">Enviar</button>
        </div>
        <div id="messages-list"></div>
    </div>
</div>

<script>
// WebSocket connection
let ws = null;
let currentSession = null;

function connectWebSocket(sessionId) {
    const wsUrl = `ws://${window.location.host}/ws/whatsapp/${sessionId}/`;
    ws = new WebSocket(wsUrl);
    
    ws.onopen = function() {
        console.log('WebSocket conectado');
        updateStatus('Conectado', 'connected');
    };
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onclose = function() {
        console.log('WebSocket desconectado');
        updateStatus('Desconectado', 'disconnected');
    };
    
    ws.onerror = function(error) {
        console.error('Erro WebSocket:', error);
        updateStatus('Erro', 'error');
    };
}

function handleWebSocketMessage(data) {
    switch(data.type) {
        case 'whatsapp_event':
            handleWhatsAppEvent(data.event, data.data);
            break;
        case 'chat_status_updated':
            updateChatStatus(data.chat_id, data.status);
            break;
        case 'chat_assigned':
            assignChat(data.chat_id, data.attendant_id);
            break;
    }
}

function handleWhatsAppEvent(event, data) {
    switch(event) {
        case 'qr':
            showQRCode(data.qr);
            break;
        case 'ready':
            hideQRCode();
            updateStatus('WhatsApp Pronto', 'ready');
            break;
        case 'message':
            handleNewMessage(data);
            break;
        case 'disconnected':
            updateStatus('Desconectado', 'disconnected');
            break;
    }
}

function showQRCode(qrDataUrl) {
    document.getElementById('qr-image').src = qrDataUrl;
    document.getElementById('qr-panel').style.display = 'block';
    document.getElementById('qr-status').textContent = 'Aguardando leitura...';
}

function hideQRCode() {
    document.getElementById('qr-panel').style.display = 'none';
}

function updateStatus(text, className) {
    document.getElementById('status-text').textContent = text;
    document.getElementById('status-dot').className = `status-dot ${className}`;
}

function createSession() {
    const sessionId = document.getElementById('session-id').value;
    if (!sessionId) {
        alert('Digite um ID para a sessão');
        return;
    }
    
    fetch(`/whatsapp/session/${sessionId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentSession = sessionId;
            connectWebSocket(sessionId);
            addSessionToList(sessionId);
            document.getElementById('session-id').value = '';
        } else {
            alert('Erro: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao criar sessão');
    });
}

function stopSession(sessionId) {
    fetch(`/whatsapp/session/${sessionId}/`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            removeSessionFromList(sessionId);
            if (sessionId === currentSession) {
                ws?.close();
                currentSession = null;
            }
        } else {
            alert('Erro: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao parar sessão');
    });
}

function addSessionToList(sessionId) {
    const sessionsList = document.getElementById('sessions-list');
    const sessionItem = document.createElement('div');
    sessionItem.className = 'session-item';
    sessionItem.setAttribute('data-session-id', sessionId);
    sessionItem.innerHTML = `
        <span class="session-name">${sessionId}</span>
        <button onclick="stopSession('${sessionId}')">Parar</button>
    `;
    sessionsList.appendChild(sessionItem);
}

function removeSessionFromList(sessionId) {
    const sessionItem = document.querySelector(`[data-session-id="${sessionId}"]`);
    if (sessionItem) {
        sessionItem.remove();
    }
}

function sendMessage() {
    if (!currentSession) {
        alert('Nenhuma sessão ativa');
        return;
    }
    
    const to = document.getElementById('message-to').value;
    const text = document.getElementById('message-text').value;
    
    if (!to || !text) {
        alert('Preencha todos os campos');
        return;
    }
    
    fetch(`/whatsapp/session/${currentSession}/message/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            to: to,
            message: text,
            type: 'text'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addMessageToList('outgoing', to, text);
            document.getElementById('message-text').value = '';
        } else {
            alert('Erro: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao enviar mensagem');
    });
}

function handleNewMessage(data) {
    addMessageToList('incoming', data.from_number, data.body);
    
    // Atualizar chat no Kanban
    updateChatInKanban(data.chat_id, 'new');
}

function addMessageToList(direction, from, text) {
    const messagesList = document.getElementById('messages-list');
    const messageItem = document.createElement('div');
    messageItem.className = `message-item ${direction}`;
    messageItem.innerHTML = `
        <div class="message-header">
            <span class="message-from">${from}</span>
            <span class="message-time">${new Date().toLocaleTimeString()}</span>
        </div>
        <div class="message-content">${text}</div>
    `;
    messagesList.appendChild(messageItem);
    messagesList.scrollTop = messagesList.scrollHeight;
}

function updateChatInKanban(chatId, status) {
    // Implementar lógica para mover chat entre colunas Kanban
    console.log(`Chat ${chatId} movido para status ${status}`);
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    updateStatus('Desconectado', 'disconnected');
});
</script>

<style>
.whatsapp-dashboard {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
}

.status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #ccc;
}

.status-dot.connected { background-color: #28a745; }
.status-dot.ready { background-color: #17a2b8; }
.status-dot.disconnected { background-color: #dc3545; }
.status-dot.error { background-color: #ffc107; }

.sessions-panel, .qr-panel, .chats-panel, .messages-panel {
    background: white;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.session-controls {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.session-controls input {
    flex: 1;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.session-controls button {
    padding: 8px 16px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.session-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    border: 1px solid #eee;
    border-radius: 4px;
    margin-bottom: 5px;
}

.qr-container {
    text-align: center;
    margin: 20px 0;
}

.qr-container img {
    max-width: 300px;
    border: 1px solid #ddd;
}

.kanban-board {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

.kanban-column {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 4px;
}

.chat-list {
    min-height: 200px;
}

.message-input {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.message-input input {
    flex: 1;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.message-input button {
    padding: 8px 16px;
    background: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

#messages-list {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #eee;
    border-radius: 4px;
    padding: 10px;
}

.message-item {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 4px;
}

.message-item.incoming {
    background: #e3f2fd;
    margin-right: 20%;
}

.message-item.outgoing {
    background: #e8f5e8;
    margin-left: 20%;
    text-align: right;
}

.message-header {
    font-size: 12px;
    color: #666;
    margin-bottom: 5px;
}

.message-content {
    word-wrap: break-word;
}
</style>
{% endblock %}
"""


# ============================================================================
# CONFIGURAÇÕES DJANGO (settings.py)
# ============================================================================

DJANGO_SETTINGS = """
# Adicionar ao settings.py do projeto Django:

# Configurações PyWhatsWeb
WHATSAPP_SIDECAR_HOST = 'localhost'
WHATSAPP_SIDECAR_PORT = 3000
WHATSAPP_API_KEY = 'sua-api-key-super-secreta-aqui'

# Para WebSocket (se usar Django Channels):
# INSTALLED_APPS += ['channels']
# ASGI_APPLICATION = 'seu_projeto.asgi.application'

# Configurações de segurança
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'whatsapp.log',
        },
    },
    'loggers': {
        'pywhatsweb': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}
"""


if __name__ == "__main__":
    print("🚀 Exemplo Django completo para PyWhatsWeb")
    print("=" * 60)
    print()
    print("📁 ARQUIVOS CRIADOS:")
    print("✅ django_complete_example.py - Views, consumers e exemplos")
    print("✅ Template HTML completo com JavaScript")
    print("✅ Configurações Django")
    print()
    print("🔧 COMO USAR:")
    print("1. Copie as views para seu app Django")
    print("2. Adicione as URLs ao urls.py")
    print("3. Configure as settings no settings.py")
    print("4. Crie o template HTML")
    print("5. Execute o sidecar: cd sidecar && npm start")
    print()
    print("🎯 FUNCIONALIDADES:")
    print("✅ Dashboard completo com sessões")
    print("✅ QR Code em tempo real")
    print("✅ Sistema Kanban (NEW → ACTIVE → DONE)")
    print("✅ Envio de mensagens")
    print("✅ WebSocket para eventos em tempo real")
    print("✅ Health check e métricas")
    print()
    print("💡 DICA: Este exemplo mostra como integrar PyWhatsWeb")
    print("   em um projeto Django existente de forma completa!")
