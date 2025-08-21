"""
Session - Representa uma sessão WhatsApp individual

Gerencia a comunicação com o sidecar para uma sessão específica.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import websockets
import requests

from .exceptions import (
    SessionError, ConnectionError, MessageError, 
    WebSocketError, APIError, AuthenticationError
)
from .enums import SessionStatus, MessageType, EventType
from .models import Message, Contact, Group


class Session:
    """Sessão WhatsApp individual"""
    
    def __init__(self, session_id: str, manager, **kwargs):
        """
        Inicializa uma sessão
        
        Args:
            session_id: ID único da sessão
            manager: Referência para o WhatsWebManager
            **kwargs: Argumentos adicionais
        """
        self.session_id = session_id
        self.manager = manager
        
        # Status da sessão
        self._status = SessionStatus.DISCONNECTED
        self._created_at = datetime.now()
        self._last_activity = datetime.now()
        
        # WebSocket
        self._ws = None
        self._ws_connected = False
        self._ws_reconnect_task = None
        self._ws_heartbeat_task = None
        
        # Reconexão
        self._reconnection_attempts = 0
        self._max_reconnection_attempts = 5
        self._reconnection_backoff_base = 2
        self._last_reconnection_attempt = 0
        
        # Heartbeat
        self._heartbeat_interval = 30  # segundos
        self._last_heartbeat = time.time()
        self._heartbeat_timeout = 10   # segundos
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {
            'qr': [],
            'authenticated': [],
            'ready': [],
            'message': [],
            'disconnected': [],
            'error': []
        }
        
        # Configurar logging
        self.logger = logging.getLogger(f"{__name__}.{session_id}")
        
        # Dados da sessão
        self.phone_number = kwargs.get('phone_number')
        self.qr_code = None
        self.is_authenticated = False
        
        self.logger.info(f"Sessão {session_id} inicializada")
    
    def get_status(self) -> SessionStatus:
        """Retorna status atual da sessão"""
        return self._status
    
    def is_active(self) -> bool:
        """Verifica se a sessão está ativa (conectada e pronta)"""
        return self._status == SessionStatus.READY
    
    def is_connected(self) -> bool:
        """Verifica se a sessão está conectada"""
        return self._status in [SessionStatus.CONNECTED, SessionStatus.READY]
    
    def start(self) -> bool:
        """
        Inicia a sessão (conecta com o sidecar)
        
        Returns:
            True se iniciada com sucesso
        """
        try:
            self.logger.info(f"Iniciando sessão {self.session_id}")
            self._status = SessionStatus.CONNECTING
            
            # Iniciar sessão no sidecar
            response = self._api_request(
                'POST', 
                f'/session/{self.session_id}/start'
            )
            
            if response.get('success'):
                self._status = SessionStatus.CONNECTED
                self.logger.info(f"Sessão {self.session_id} iniciada no sidecar")
                
                # Conectar WebSocket para eventos
                asyncio.create_task(self._connect_websocket())
                
                return True
            else:
                raise SessionError(f"Erro ao iniciar sessão: {response.get('error')}")
                
        except Exception as e:
            self._status = SessionStatus.ERROR
            self.logger.error(f"Erro ao iniciar sessão {self.session_id}: {e}")
            raise SessionError(f"Falha ao iniciar sessão: {e}")
    
    def stop(self) -> bool:
        """
        Para a sessão
        
        Returns:
            True se parada com sucesso
        """
        try:
            self.logger.info(f"Parando sessão {self.session_id}")
            
            # Cancelar tarefas de reconexão e heartbeat
            if self._ws_reconnect_task:
                self._ws_reconnect_task.cancel()
            if self._ws_heartbeat_task:
                self._ws_heartbeat_task.cancel()
            
            # Desconectar WebSocket
            if self._ws:
                asyncio.create_task(self._disconnect_websocket())
            
            # Parar sessão no sidecar
            response = self._api_request(
                'POST', 
                f'/session/{self.session_id}/stop'
            )
            
            if response.get('success'):
                self._status = SessionStatus.DISCONNECTED
                self.logger.info(f"Sessão {self.session_id} parada")
                return True
            else:
                raise SessionError(f"Erro ao parar sessão: {response.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Erro ao parar sessão {self.session_id}: {e}")
            raise SessionError(f"Falha ao parar sessão: {e}")
    
    def get_status_info(self) -> Dict[str, Any]:
        """
        Obtém informações detalhadas do status
        
        Returns:
            Dicionário com informações da sessão
        """
        try:
            response = self._api_request(
                'GET', 
                f'/session/{self.session_id}/status'
            )
            
            return {
                'session_id': self.session_id,
                'status': self._status.value,
                'created_at': self._created_at.isoformat(),
                'last_activity': self._last_activity.isoformat(),
                'phone_number': self.phone_number,
                'is_authenticated': self.is_authenticated,
                'ws_connected': self._ws_connected,
                'reconnection_attempts': self._reconnection_attempts,
                'sidecar_info': response
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status: {e}")
            return {
                'session_id': self.session_id,
                'status': self._status.value,
                'error': str(e)
            }
    
    def send_text(self, to: str, text: str) -> str:
        """
        Envia mensagem de texto
        
        Args:
            to: Número de telefone do destinatário
            text: Texto da mensagem
            
        Returns:
            ID da mensagem enviada
        """
        if not self.is_connected():
            raise SessionError("Sessão não está conectada")
        
        try:
            response = self._api_request(
                'POST',
                f'/session/{self.session_id}/send-message',
                data={
                    'to': to,
                    'message': text,
                    'type': 'text'
                }
            )
            
            if response.get('success'):
                message_id = response.get('messageId')
                self.logger.info(f"Mensagem enviada para {to}: {message_id}")
                
                # Salvar no storage
                self._save_message_to_storage(to, text, 'text', message_id)
                
                return message_id
            else:
                raise MessageError(f"Erro ao enviar mensagem: {response.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem para {to}: {e}")
            raise MessageError(f"Falha ao enviar mensagem: {e}")
    
    def send_media(self, to: str, media_path: str, caption: str = "") -> str:
        """
        Envia arquivo de mídia
        
        Args:
            to: Número de telefone do destinatário
            media_path: Caminho para o arquivo
            caption: Legenda da mídia
            
        Returns:
            ID da mensagem enviada
        """
        if not self.is_connected():
            raise SessionError("Sessão não está conectada")
        
        try:
            # Determinar tipo de mídia
            media_type = self._get_media_type(media_path)
            
            response = self._api_request(
                'POST',
                f'/session/{self.session_id}/send-message',
                data={
                    'to': to,
                    'message': media_path,
                    'type': media_type,
                    'caption': caption
                }
            )
            
            if response.get('success'):
                message_id = response.get('messageId')
                self.logger.info(f"Mídia enviada para {to}: {message_id}")
                
                # Salvar no storage
                self._save_message_to_storage(to, f"{media_path} {caption}", media_type, message_id)
                
                return message_id
            else:
                raise MessageError(f"Erro ao enviar mídia: {response.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Erro ao enviar mídia para {to}: {e}")
            raise MessageError(f"Falha ao enviar mídia: {e}")
    
    def on(self, event: str, handler: Callable):
        """
        Registra handler para um evento
        
        Args:
            event: Nome do evento (qr, authenticated, ready, message, disconnected)
            handler: Função que será chamada quando o evento ocorrer
        """
        if event not in self._event_handlers:
            raise ValueError(f"Evento inválido: {event}")
        
        self._event_handlers[event].append(handler)
        self.logger.debug(f"Handler registrado para evento {event}")
    
    def _trigger_event(self, event: str, data: Dict[str, Any]):
        """Dispara um evento para todos os handlers registrados"""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Erro no handler do evento {event}: {e}")
    
    async def _connect_websocket(self):
        """Conecta ao WebSocket do sidecar"""
        try:
            ws_url = f"ws://{self.manager.sidecar_host}:{self.manager.sidecar_ws_port}"
            self.logger.info(f"Conectando WebSocket: {ws_url}")
            
            self._ws = await websockets.connect(ws_url)
            self._ws_connected = True
            self._reconnection_attempts = 0
            
            self.logger.info("WebSocket conectado")
            
            # Iniciar heartbeat
            self._ws_heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            # Loop de recebimento de mensagens
            async for message in self._ws:
                try:
                    data = json.loads(message)
                    await self._handle_websocket_message(data)
                except Exception as e:
                    self.logger.error(f"Erro ao processar mensagem WebSocket: {e}")
                    
        except Exception as e:
            self.logger.error(f"Erro ao conectar WebSocket: {e}")
            self._ws_connected = False
            self._status = SessionStatus.ERROR
            
            # Tentar reconectar automaticamente
            await self._schedule_reconnection()
    
    async def _disconnect_websocket(self):
        """Desconecta do WebSocket"""
        if self._ws:
            try:
                await self._ws.close()
                self.logger.info("WebSocket desconectado")
            except Exception as e:
                self.logger.error(f"Erro ao desconectar WebSocket: {e}")
            finally:
                self._ws = None
                self._ws_connected = False
    
    async def _schedule_reconnection(self):
        """Agenda tentativa de reconexão com backoff exponencial"""
        if self._reconnection_attempts >= self._max_reconnection_attempts:
            self.logger.error("Máximo de tentativas de reconexão atingido")
            return
        
        # Calcular delay com backoff exponencial
        delay = self._reconnection_backoff_base ** self._reconnection_attempts
        self._reconnection_attempts += 1
        
        self.logger.info(f"Tentativa de reconexão {self._reconnection_attempts} em {delay}s")
        
        # Agendar reconexão
        await asyncio.sleep(delay)
        
        if not self._ws_connected:
            self._ws_reconnect_task = asyncio.create_task(self._connect_websocket())
    
    async def _heartbeat_loop(self):
        """Loop de heartbeat para manter conexão ativa"""
        while self._ws_connected:
            try:
                # Enviar ping
                if self._ws:
                    await self._ws.ping()
                    self._last_heartbeat = time.time()
                    self.logger.debug("Heartbeat enviado")
                
                # Aguardar próximo heartbeat
                await asyncio.sleep(self._heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no heartbeat: {e}")
                break
        
        self.logger.info("Loop de heartbeat finalizado")
    
    async def _handle_websocket_message(self, data: Dict[str, Any]):
        """Processa mensagem recebida via WebSocket"""
        try:
            event = data.get('event')
            event_data = data.get('data', {})
            
            # Verificar se é para esta sessão
            if event_data.get('sessionId') != self.session_id:
                return
            
            self.logger.debug(f"Evento recebido: {event}")
            
            # Processar evento
            if event == 'qr':
                self.qr_code = event_data.get('qr')
                self._trigger_event('qr', event_data)
                
            elif event == 'authenticated':
                self.is_authenticated = True
                self._status = SessionStatus.CONNECTED
                self._trigger_event('authenticated', event_data)
                
            elif event == 'ready':
                self._status = SessionStatus.READY
                self._trigger_event('ready', event_data)
                
            elif event == 'message':
                self._handle_incoming_message(event_data)
                self._trigger_event('message', event_data)
                
            elif event == 'disconnected':
                self._status = SessionStatus.DISCONNECTED
                self.is_authenticated = False
                self._trigger_event('disconnected', event_data)
                
                # Tentar reconectar automaticamente
                await self._schedule_reconnection()
                
            elif event == 'error':
                self._trigger_event('error', event_data)
                
                # Verificar se é erro recuperável
                if not event_data.get('recoverable', True):
                    self.logger.error("Erro não recuperável detectado")
                    self._status = SessionStatus.ERROR
                else:
                    # Tentar reconectar
                    await self._schedule_reconnection()
                
            # Atualizar última atividade
            self._last_activity = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Erro ao processar evento WebSocket: {e}")
    
    def _handle_incoming_message(self, data: Dict[str, Any]):
        """Processa mensagem recebida"""
        try:
            # Criar objeto Message
            message = Message(
                id=data.get('messageId'),
                content=data.get('body', ''),
                sender=Contact(phone=data.get('from')),
                recipient=Contact(phone=data.get('to')),
                message_type=data.get('type', 'text'),
                timestamp=datetime.fromtimestamp(data.get('timestamp', 0) / 1000)
            )
            
            # Salvar no storage
            self.manager.storage.save_message(message)
            
            self.logger.info(f"Mensagem recebida de {message.sender.phone}: {message.content}")
            
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem recebida: {e}")
    
    def _api_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Faz requisição HTTP para o sidecar"""
        try:
            url = f"{self.manager._base_url}{endpoint}"
            headers = {
                'Authorization': f'Bearer {self.manager.api_key}',
                'Content-Type': 'application/json'
            }
            
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise AuthenticationError("API key inválida")
            elif response.status_code == 404:
                raise SessionError("Sessão não encontrada")
            else:
                raise APIError(f"Erro HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Erro de conexão com sidecar: {e}")
        except Exception as e:
            raise APIError(f"Erro na requisição API: {e}")
    
    def _save_message_to_storage(self, to: str, content: str, message_type: str, message_id: str):
        """Salva mensagem no storage"""
        try:
            message = Message(
                id=message_id,
                content=content,
                sender=Contact(phone=self.phone_number or "unknown"),
                recipient=Contact(phone=to),
                message_type=message_type,
                timestamp=datetime.now()
            )
            
            self.manager.storage.save_message(message)
            
        except Exception as e:
            self.logger.warning(f"Erro ao salvar mensagem no storage: {e}")
    
    def _get_media_type(self, file_path: str) -> str:
        """Determina tipo de mídia baseado na extensão do arquivo"""
        import os
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.jpg', '.jpeg', '.png', '.gif']:
            return 'image'
        elif ext in ['.mp4', '.avi', '.mov']:
            return 'video'
        elif ext in ['.mp3', '.wav', '.ogg']:
            return 'audio'
        elif ext in ['.pdf', '.doc', '.txt']:
            return 'document'
        else:
            return 'document'
    
    def __str__(self):
        return f"Session({self.session_id}, status={self._status.value})"
    
    def __repr__(self):
        return self.__str__()
