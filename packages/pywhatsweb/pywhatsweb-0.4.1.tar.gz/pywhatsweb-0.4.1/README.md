# PyWhatsWeb 🚀 v0.2.1

**Biblioteca Python pura** para WhatsApp Web corporativo, baseada em sidecar Node.js com `whatsapp-web.js`.

## 🎯 **O QUE É**

PyWhatsWeb é uma **biblioteca Python** que pode ser usada em **qualquer projeto Python**:
- ✅ **Scripts Python simples**
- ✅ **FastAPI**
- ✅ **Flask** 
- ✅ **Django** (opcional)
- ✅ **Qualquer outro framework Python**

**NÃO é um projeto Django** - é uma biblioteca Python que pode ser integrada em projetos Django se você quiser.

## ✨ **CARACTERÍSTICAS**

- 🔐 **Autenticação QR Code** via sidecar Node.js
- 📡 **Eventos WebSocket** em tempo real
- 🎯 **Multi-sessão** com isolamento por sessionId
- 📊 **Sistema Kanban** (NEW/ACTIVE/DONE) para roteamento
- 💾 **Storage pluggable** (FileSystem + Django opcional)
- 🌐 **API HTTP** para controle de sessões
- 🔒 **Autenticação por API Key**
- 📱 **Suporte completo** ao whatsapp-web.js

## 🚀 **INSTALAÇÃO**

### PyPI Oficial
```bash
pip install pywhatsweb
```

### Com suporte Django (opcional)
```bash
pip install pywhatsweb[django]
```

### Desenvolvimento
```bash
git clone https://github.com/llongaray/pywhatsweb.git
cd pywhatsweb
pip install -e .
```

## 📖 **USO BÁSICO (SEM Django)**

### 1. Script Python Simples
```python
from pywhatsweb import WhatsWebManager, FileSystemStore

# Criar manager com storage de filesystem
manager = WhatsWebManager(
    sidecar_host="localhost",
    sidecar_port=3000,
    api_key="sua-api-key",
    storage=FileSystemStore("./whatsapp_data")  # Storage local
)

# Criar sessão
session = manager.create_session("sessao_123")

# Configurar eventos
@session.on("qr")
def on_qr(data):
    print(f"🔍 QR Code: {data['qr'][:50]}...")

@session.on("message")
def on_message(data):
    print(f"📨 Nova mensagem: {data['body']}")

# Iniciar sessão
session.start()
```

### 2. FastAPI
```python
from fastapi import FastAPI
from pywhatsweb import WhatsWebManager, FileSystemStore

app = FastAPI()

# Criar manager global
manager = WhatsWebManager(
    sidecar_host="localhost",
    sidecar_port=3000,
    api_key="sua-api-key",
    storage=FileSystemStore("./whatsapp_data")
)

@app.post("/whatsapp/session/{session_id}/start")
async def start_session(session_id: str):
    session = manager.create_session(session_id)
    session.start()
    return {"message": "Sessão iniciada"}

@app.post("/whatsapp/session/{session_id}/send")
async def send_message(session_id: str, to: str, message: str):
    session = manager.get_session(session_id)
    session.send_text(to, message)
    return {"message": "Mensagem enviada"}
```

### 3. Flask
```python
from flask import Flask, request, jsonify
from pywhatsweb import WhatsWebManager, FileSystemStore

app = Flask(__name__)

# Criar manager global
manager = WhatsWebManager(
    sidecar_host="localhost",
    sidecar_port=3000,
    api_key="sua-api-key",
    storage=FileSystemStore("./whatsapp_data")
)

@app.route('/whatsapp/session/<session_id>/start', methods=['POST'])
def start_session(session_id):
    session = manager.create_session(session_id)
    session.start()
    return jsonify({"message": "Sessão iniciada"})

@app.route('/whatsapp/session/<session_id>/send', methods=['POST'])
def send_message(session_id):
    data = request.get_json()
    session = manager.get_session(session_id)
    session.send_text(data['to'], data['message'])
    return jsonify({"message": "Mensagem enviada"})
```

## 🔧 **INTEGRAÇÃO COM DJANGO (OPCIONAL)**

Se você **quiser** usar em um projeto Django, pode usar o `DjangoORMStore`:

```python
from pywhatsweb import WhatsWebManager, DjangoORMStore
from .models import (WhatsAppSession, WhatsAppMessage, WhatsAppContact,
                     WhatsAppGroup, WhatsAppChat, WhatsAppSessionEvent)

# Criar manager com storage Django
manager = WhatsWebManager(
    sidecar_host="localhost",
    sidecar_port=3000,
    api_key="sua-api-key",
    storage=DjangoORMStore()
)

# Configurar models Django (você deve implementar)
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
```

**NOTA:** Django NÃO é obrigatório! A biblioteca funciona perfeitamente sem Django usando `FileSystemStore`.

## 🏗️ **ARQUITETURA**

```
┌─────────────────┐    HTTP + WebSocket    ┌─────────────────┐
│   Seu App       │ ◄────────────────────► │   Sidecar       │
│   Python        │                        │   Node.js       │
│                 │                        │                 │
│  PyWhatsWeb    │                        │ whatsapp-web.js │
│  (SDK)         │                        │                 │
└─────────────────┘                        └─────────────────┘
```

- **Seu App Python**: Usa a biblioteca PyWhatsWeb
- **Sidecar Node.js**: Gerencia conexões WhatsApp via whatsapp-web.js
- **Comunicação**: HTTP (ações) + WebSocket (eventos)

## 📱 **SIDECAR NODE.JS**

A biblioteca precisa do sidecar Node.js rodando. Veja a pasta `sidecar/` para instalação:

```bash
cd sidecar
npm install
npm start
```

## 🎯 **SISTEMA KANBAN**

A biblioteca fornece enums para roteamento de conversas:

```python
from pywhatsweb.enums import KanbanStatus

# Status disponíveis
KanbanStatus.NEW      # Aguardando
KanbanStatus.ACTIVE   # Em atendimento  
KanbanStatus.DONE     # Concluído

# Nomes de exibição
KanbanStatus.get_display_name(KanbanStatus.NEW)  # "Aguardando"
```

## 💾 **STORAGE PLUGGABLE**

### FileSystemStore (padrão)
```python
from pywhatsweb import FileSystemStore

storage = FileSystemStore("./whatsapp_data")
# Salva tudo em arquivos JSON
```

### DjangoORMStore (opcional)
```python
from pywhatsweb import DjangoORMStore

storage = DjangoORMStore()
# Salva no banco Django (se disponível)
```

## 🔌 **EVENTOS WEBSOCKET**

```python
@session.on("qr")
def on_qr(data):
    # QR Code gerado
    qr_data_url = data['qr']  # data:image/png;base64,...

@session.on("authenticated")
def on_authenticated(data):
    # Autenticação bem-sucedida

@session.on("ready")
def on_ready(data):
    # Cliente WhatsApp pronto

@session.on("message")
def on_message(data):
    # Nova mensagem recebida
    chat_id = data['chatId']
    message_body = data['body']
    sender = data['from']

@session.on("disconnected")
def on_disconnected(data):
    # Cliente desconectado
```

## 📡 **API HTTP**

### Sessões
- `POST /session/:id/start` - Iniciar sessão
- `POST /session/:id/stop` - Parar sessão
- `GET /session/:id/status` - Status da sessão

### Mensagens
- `POST /session/:id/send-message` - Enviar mensagem

### Health Check
- `GET /health` - Status do sidecar

## 🚨 **IMPORTANTE**

- **PyWhatsWeb é uma BIBLIOTECA Python**, não um projeto Django
- **Funciona em qualquer projeto Python** usando FileSystemStore
- **Django é opcional** - use DjangoORMStore se quiser
- **Sidecar Node.js é obrigatório** para funcionar
- **Não abre navegador** - tudo via whatsapp-web.js headless

## 🧪 **EXEMPLOS**

Veja a pasta `examples/` para exemplos completos:
- `basic_usage.py` - Uso básico
- `django_integration.py` - Integração com Django (opcional)
- `django_models_example.py` - Models Django de exemplo

## 📚 **DOCUMENTAÇÃO**

- [Sidecar Node.js](sidecar/README.md)
- [Exemplos](examples/)
- [Changelog](CHANGELOG.md)

## 🤝 **CONTRIBUIÇÃO**

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 **LICENÇA**

MIT License - veja [LICENSE](LICENSE).

---

**PyWhatsWeb** - Biblioteca Python para WhatsApp Web corporativo 🚀
