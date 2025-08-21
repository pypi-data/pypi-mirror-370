#!/usr/bin/env python3
"""
Exemplo básico de uso da PyWhatsWeb

Este exemplo mostra como usar a biblioteca de forma básica.
"""

import asyncio
import logging
from pywhatsweb import WhatsWebManager, FileSystemStore

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def exemplo_basico():
    """Exemplo básico de uso"""
    print("🚀 Exemplo básico da PyWhatsWeb")
    
    # Criar manager
    manager = WhatsWebManager(
        sidecar_host="localhost",
        sidecar_port=3000,
        api_key="pywhatsweb-secret-key",
        storage=FileSystemStore("./whatsapp_data")
    )
    
    try:
        # Criar sessão
        session = manager.create_session("sessao_teste")
        print(f"✅ Sessão criada: {session.session_id}")
        
        # Configurar eventos
        @session.on("qr")
        def on_qr(data):
            print(f"🔍 QR Code gerado para sessão {data['sessionId']}")
            print(f"📱 Escaneie o QR Code: {data['qr'][:50]}...")
        
        @session.on("authenticated")
        def on_authenticated(data):
            print(f"✅ Autenticado com sucesso!")
        
        @session.on("ready")
        def on_ready(data):
            print(f"🚀 WhatsApp está pronto!")
        
        @session.on("message")
        def on_message(data):
            print(f"📨 Nova mensagem de {data['from']}: {data['body']}")
            
            # Auto-resposta simples
            if "oi" in data['body'].lower():
                try:
                    session.send_text(data['from'], "Oi! Como posso ajudar? 😊")
                    print(f"✅ Auto-resposta enviada para {data['from']}")
                except Exception as e:
                    print(f"❌ Erro ao enviar auto-resposta: {e}")
        
        @session.on("disconnected")
        def on_disconnected(data):
            print(f"❌ Desconectado: {data.get('reason', 'Desconhecido')}")
        
        # Iniciar sessão
        print("🔄 Iniciando sessão...")
        session.start()
        
        # Mostrar informações da sessão
        print(f"📊 Status da sessão: {session.get_status().value}")
        print(f"📱 Número: {session.phone_number or 'Não definido'}")
        
        # Manter ativo por um tempo
        print("⏳ Mantendo sessão ativa por 30 segundos...")
        import time
        time.sleep(30)
        
        # Parar sessão
        print("🛑 Parando sessão...")
        session.stop()
        
        print("✅ Exemplo concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no exemplo: {e}")
        logger.error(f"Erro no exemplo: {e}", exc_info=True)
    
    finally:
        # Limpar
        manager.cleanup()


def exemplo_multiplas_sessoes():
    """Exemplo com múltiplas sessões"""
    print("\n🎯 Exemplo com múltiplas sessões")
    
    manager = WhatsWebManager(
        sidecar_host="localhost",
        sidecar_port=3000,
        api_key="pywhatsweb-secret-key"
    )
    
    try:
        # Criar múltiplas sessões
        sessao1 = manager.create_session("sessao_1", phone_number="5511999999999")
        sessao2 = manager.create_session("sessao_2", phone_number="5511888888888")
        
        print(f"✅ Sessões criadas: {manager.list_sessions()}")
        print(f"📊 Total de sessões: {manager.get_session_count()}")
        
        # Configurar eventos para sessão 1
        @sessao1.on("ready")
        def on_ready_1(data):
            print(f"🚀 Sessão 1 está pronta!")
        
        # Configurar eventos para sessão 2
        @sessao2.on("ready")
        def on_ready_2(data):
            print(f"🚀 Sessão 2 está pronta!")
        
        # Iniciar sessões
        sessao1.start()
        sessao2.start()
        
        # Aguardar um pouco
        import time
        time.sleep(10)
        
        # Mostrar status
        print(f"📊 Status sessão 1: {sessao1.get_status().value}")
        print(f"📊 Status sessão 2: {sessao2.get_status().value}")
        
        # Parar sessões
        sessao1.stop()
        sessao2.stop()
        
        print("✅ Exemplo de múltiplas sessões concluído!")
        
    except Exception as e:
        print(f"❌ Erro no exemplo: {e}")
    
    finally:
        manager.cleanup()


def exemplo_storage():
    """Exemplo de uso do storage"""
    print("\n💾 Exemplo de uso do storage")
    
    # Criar storage
    storage = FileSystemStore("./whatsapp_data")
    
    try:
        # Criar contatos
        from pywhatsweb.models import Contact, Message
        
        contato1 = Contact(
            phone="5511999999999",
            name="João Silva",
            is_business=False
        )
        
        contato2 = Contact(
            phone="5511888888888",
            name="Maria Santos",
            is_business=True
        )
        
        # Salvar contatos
        storage.save_contact(contato1)
        storage.save_contact(contato2)
        print("✅ Contatos salvos no storage")
        
        # Recuperar contatos
        contato_recuperado = storage.get_contact("5511999999999")
        print(f"📱 Contato recuperado: {contato_recuperado.display_name}")
        
        # Criar mensagem
        mensagem = Message(
            id="msg_123",
            content="Olá! Teste da PyWhatsWeb",
            sender=contato1,
            recipient=contato2
        )
        
        # Salvar mensagem
        storage.save_message(mensagem)
        print("✅ Mensagem salva no storage")
        
        # Recuperar mensagens do chat
        mensagens = storage.get_chat_messages("5511888888888", limit=10)
        print(f"📨 Mensagens recuperadas: {len(mensagens)}")
        
        print("✅ Exemplo de storage concluído!")
        
    except Exception as e:
        print(f"❌ Erro no exemplo de storage: {e}")
    
    finally:
        storage.close()


if __name__ == "__main__":
    print("🎯 Exemplos da PyWhatsWeb v0.2.1")
    print("=" * 50)
    
    # Exemplo básico
    exemplo_basico()
    
    # Exemplo de múltiplas sessões
    exemplo_multiplas_sessoes()
    
    # Exemplo de storage
    exemplo_storage()
    
    print("\n🎉 Todos os exemplos executados!")
    print("\n💡 Lembre-se de ter o sidecar Node.js rodando!")
    print("   cd sidecar && npm start")
