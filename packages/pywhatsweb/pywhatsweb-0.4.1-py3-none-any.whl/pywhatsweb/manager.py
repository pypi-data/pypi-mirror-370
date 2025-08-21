"""
WhatsWebManager - Gerenciador principal do PyWhatsWeb

Gerencia múltiplas sessões WhatsApp e fornece interface unificada para o usuário.
"""

import asyncio
import logging
from typing import Dict, Optional, List
from datetime import datetime

from .session import Session
from .storage.base import BaseStore
from .storage.filesystem import FileSystemStore
from .exceptions import SessionError, ConnectionError, AuthenticationError
from .enums import SessionStatus


class WhatsWebManager:
    """Gerenciador principal do PyWhatsWeb"""
    
    def __init__(self, 
                 sidecar_host: str = "localhost",
                 sidecar_port: int = 3000,
                 sidecar_ws_port: int = 3001,
                 api_key: str = "pywhatsweb-secret-key",
                 storage: Optional[BaseStore] = None,
                 session_base_dir: str = "./sessions"):
        """
        Inicializa o manager
        
        Args:
            sidecar_host: Host do sidecar Node.js
            sidecar_port: Porta HTTP do sidecar
            sidecar_ws_port: Porta WebSocket do sidecar
            api_key: Chave de API para autenticação
            storage: Storage pluggable (padrão: FileSystemStore)
            session_base_dir: Diretório base para sessões
        """
        self.sidecar_host = sidecar_host
        self.sidecar_port = sidecar_port
        self.sidecar_ws_port = sidecar_ws_port
        self.api_key = api_key
        self.session_base_dir = session_base_dir
        
        # Storage padrão se não especificado
        if storage is None:
            self.storage = FileSystemStore(f"{session_base_dir}/data")
        else:
            self.storage = storage
        
        # Sessões ativas
        self._sessions: Dict[str, Session] = {}
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # URLs do sidecar
        self._base_url = f"http://{sidecar_host}:{sidecar_port}"
        self._ws_url = f"ws://{sidecar_host}:{sidecar_ws_port}"
        
        self.logger.info(f"PyWhatsWeb Manager inicializado - Sidecar: {self._base_url}")
    
    def create_session(self, session_id: str, **kwargs) -> Session:
        """
        Cria uma nova sessão WhatsApp
        
        Args:
            session_id: ID único da sessão
            **kwargs: Argumentos adicionais para a sessão
            
        Returns:
            Session: Nova sessão criada
            
        Raises:
            SessionError: Se a sessão já existir
        """
        if session_id in self._sessions:
            raise SessionError(f"Sessão {session_id} já existe")
        
        # Criar sessão
        session = Session(
            session_id=session_id,
            manager=self,
            **kwargs
        )
        
        # Armazenar sessão
        self._sessions[session_id] = session
        
        self.logger.info(f"Sessão {session_id} criada")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Recupera uma sessão existente
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Session ou None se não existir
        """
        return self._sessions.get(session_id)
    
    def list_sessions(self) -> List[str]:
        """
        Lista todas as sessões ativas
        
        Returns:
            Lista de IDs de sessão
        """
        return list(self._sessions.keys())
    
    def remove_session(self, session_id: str) -> bool:
        """
        Remove uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            True se removida com sucesso
        """
        if session_id not in self._sessions:
            return False
        
        session = self._sessions[session_id]
        
        # Parar sessão se estiver ativa
        if session.is_active():
            try:
                session.stop()
            except Exception as e:
                self.logger.warning(f"Erro ao parar sessão {session_id}: {e}")
        
        # Remover da memória
        del self._sessions[session_id]
        
        self.logger.info(f"Sessão {session_id} removida")
        return True
    
    def get_session_status(self, session_id: str) -> Optional[SessionStatus]:
        """
        Obtém status de uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Status da sessão ou None se não existir
        """
        session = self.get_session(session_id)
        if session:
            return session.get_status()
        return None
    
    def get_active_sessions(self) -> List[str]:
        """
        Lista sessões ativas (conectadas e prontas)
        
        Returns:
            Lista de IDs de sessão ativa
        """
        active_sessions = []
        for session_id, session in self._sessions.items():
            if session.is_active():
                active_sessions.append(session_id)
        return active_sessions
    
    def get_session_count(self) -> int:
        """
        Retorna número total de sessões
        
        Returns:
            Número de sessões
        """
        return len(self._sessions)
    
    def get_sidecar_info(self) -> Dict[str, str]:
        """
        Informações do sidecar
        
        Returns:
            Dicionário com informações do sidecar
        """
        return {
            "host": self.sidecar_host,
            "http_port": self.sidecar_port,
            "ws_port": self.sidecar_ws_port,
            "base_url": self._base_url,
            "ws_url": self._ws_url
        }
    
    def close_all_sessions(self):
        """Para e remove todas as sessões"""
        session_ids = list(self._sessions.keys())
        
        for session_id in session_ids:
            try:
                self.remove_session(session_id)
            except Exception as e:
                self.logger.error(f"Erro ao fechar sessão {session_id}: {e}")
        
        self.logger.info("Todas as sessões foram fechadas")
    
    def cleanup(self):
        """Limpeza e fechamento do manager"""
        self.close_all_sessions()
        
        if hasattr(self.storage, 'close'):
            try:
                self.storage.close()
            except Exception as e:
                self.logger.error(f"Erro ao fechar storage: {e}")
        
        self.logger.info("PyWhatsWeb Manager finalizado")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
    
    def __del__(self):
        """Destructor"""
        try:
            self.cleanup()
        except:
            pass
