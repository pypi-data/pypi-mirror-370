#!/usr/bin/env python3
"""
Exemplo de integração PyWhatsWeb com Django (OPCIONAL)

Este exemplo mostra como usar a biblioteca em um projeto Django existente.
A biblioteca NÃO é um projeto Django, é uma biblioteca Python que pode ser usada em Django.
"""

# Este arquivo é apenas um exemplo para projetos Django
# A biblioteca funciona perfeitamente sem Django usando FileSystemStore

from pywhatsweb import WhatsWebManager, Session, FileSystemStore, DjangoORMStore
from pywhatsweb.enums import KanbanStatus

# ============================================================================
# EXEMPLO 1: Uso básico com FileSystemStore (SEM Django)
# ============================================================================

def exemplo_sem_django():
    """Exemplo usando apenas filesystem (funciona em qualquer projeto Python)"""
    print("🚀 Exemplo SEM Django - FileSystemStore")
    
    # Criar manager com storage de filesystem
    manager = WhatsWebManager(
        sidecar_host="localhost",
        sidecar_port=3000,
        api_key="sua-api-key",
        storage=FileSystemStore("./whatsapp_data")  # Storage local
    )
    
    # Criar sessão
    session = manager.create_session("sessao_123")
    
    # Usar normalmente
    session.start()
    
    print("✅ Funcionando perfeitamente sem Django!")

# ============================================================================
# EXEMPLO 2: Integração com Django (OPCIONAL)
# ============================================================================

def exemplo_com_django():
    """Exemplo de integração com Django (OPCIONAL)"""
    print("🔧 Exemplo COM Django - DjangoORMStore")
    
    try:
        # Verificar se Django está disponível
        import django
        from django.conf import settings
        
        # Configurar Django (se não estiver configurado)
        if not settings.configured:
            settings.configure(
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': 'whatsapp.db',
                    }
                },
                INSTALLED_APPS=['django.contrib.auth'],
                USE_TZ=True,
            )
            django.setup()
        
        # Criar manager com storage Django
        manager = WhatsWebManager(
            sidecar_host="localhost",
            sidecar_port=3000,
            api_key="sua-api-key",
            storage=DjangoORMStore()  # Storage Django
        )
        
        # Configurar models Django (usuário deve implementar)
        from .models import (  # Models do projeto Django do usuário
            WhatsAppSession, WhatsAppMessage, WhatsAppContact,
            WhatsAppGroup, WhatsAppChat, WhatsAppSessionEvent
        )
        
        # Registrar models no storage
        manager.storage.set_models(
            session_model=WhatsAppSession,
            message_model=WhatsAppMessage,
            contact_model=WhatsAppContact,
            group_model=WhatsAppGroup,
            chat_model=WhatsAppChat,
            event_model=WhatsAppSessionEvent
        )
        
        # Criar sessão
        session = manager.create_session("sessao_123")
        
        # Usar normalmente
        session.start()
        
        print("✅ Integração com Django funcionando!")
        
    except ImportError:
        print("❌ Django não disponível - use FileSystemStore")
    except Exception as e:
        print(f"❌ Erro na integração Django: {e}")

# ============================================================================
# EXEMPLO 3: Uso em script Python simples
# ============================================================================

def exemplo_script_simples():
    """Exemplo de uso em script Python simples"""
    print("📝 Exemplo em script Python simples")
    
    # Criar manager com storage padrão (FileSystem)
    manager = WhatsWebManager(
        sidecar_host="localhost",
        sidecar_port=3000,
        api_key="sua-api-key"
        # storage não especificado = usa FileSystemStore por padrão
    )
    
    # Criar sessão
    session = manager.create_session("sessao_123")
    
    # Configurar eventos
    @session.on("qr")
    def on_qr(data):
        print(f"🔍 QR Code gerado para sessão {data['sessionId']}")
        print(f"📱 Escaneie o QR Code: {data['qr'][:50]}...")
    
    @session.on("message")
    def on_message(data):
        print(f"📨 Nova mensagem: {data['body']}")
        
        # Auto-resposta simples
        if "oi" in data['body'].lower():
            session.send_text(data['from'], "Oi! Como posso ajudar? 😊")
    
    # Iniciar sessão
    session.start()
    
    print("✅ Script Python funcionando perfeitamente!")

# ============================================================================
# EXEMPLO 4: Uso em FastAPI
# ============================================================================

def exemplo_fastapi():
    """Exemplo de uso em FastAPI"""
    print("⚡ Exemplo em FastAPI")
    
    # Em um projeto FastAPI, você pode usar assim:
    
    # from fastapi import FastAPI
    # from pywhatsweb import WhatsWebManager, FileSystemStore
    # 
    # app = FastAPI()
    # 
    # # Criar manager global
    # manager = WhatsWebManager(
    #     sidecar_host="localhost",
    #     sidecar_port=3000,
    #     api_key="sua-api-key",
    #     storage=FileSystemStore("./whatsapp_data")
    # )
    # 
    # @app.post("/whatsapp/session/{session_id}/start")
    # async def start_session(session_id: str):
    #     session = manager.create_session(session_id)
    #     session.start()
    #     return {"message": "Sessão iniciada"}
    # 
    # @app.post("/whatsapp/session/{session_id}/send")
    # async def send_message(session_id: str, to: str, message: str):
    #     session = manager.get_session(session_id)
    #     session.send_text(to, message)
    #     return {"message": "Mensagem enviada"}
    
    print("✅ Exemplo FastAPI configurado!")

# ============================================================================
# EXEMPLO 5: Uso em Flask
# ============================================================================

def exemplo_flask():
    """Exemplo de uso em Flask"""
    print("🌶️ Exemplo em Flask")
    
    # Em um projeto Flask, você pode usar assim:
    
    # from flask import Flask, request, jsonify
    # from pywhatsweb import WhatsWebManager, FileSystemStore
    # 
    # app = Flask(__name__)
    # 
    # # Criar manager global
    # manager = WhatsWebManager(
    #     sidecar_host="localhost",
    #     sidecar_port=3000,
    #     api_key="sua-api-key",
    #     storage=FileSystemStore("./whatsapp_data")
    # )
    # 
    # @app.route('/whatsapp/session/<session_id>/start', methods=['POST'])
    # def start_session(session_id):
    #     session = manager.create_session(session_id)
    #     session.start()
    #     return jsonify({"message": "Sessão iniciada"})
    # 
    # @app.route('/whatsapp/session/<session_id>/send', methods=['POST'])
    # def send_message(session_id):
    #     data = request.get_json()
    #     session = manager.get_session(session_id)
    #     session.send_text(data['to'], data['message'])
    #     return jsonify({"message": "Mensagem enviada"})
    
    print("✅ Exemplo Flask configurado!")

# ============================================================================
# EXECUTAR EXEMPLOS
# ============================================================================

if __name__ == "__main__":
    print("🎯 Exemplos de uso da PyWhatsWeb (biblioteca Python pura)")
    print("=" * 60)
    
    # Exemplo sem Django (sempre funciona)
    exemplo_sem_django()
    print()
    
    # Exemplo com Django (opcional)
    exemplo_com_django()
    print()
    
    # Exemplo em script Python
    exemplo_script_simples()
    print()
    
    # Exemplos de frameworks
    exemplo_fastapi()
    exemplo_flask()
    print()
    
    print("🎉 Todos os exemplos configurados!")
    print("\n💡 Lembre-se: PyWhatsWeb é uma BIBLIOTECA Python, não um projeto Django!")
    print("   Use em qualquer projeto Python: scripts, FastAPI, Flask, Django, etc.")
