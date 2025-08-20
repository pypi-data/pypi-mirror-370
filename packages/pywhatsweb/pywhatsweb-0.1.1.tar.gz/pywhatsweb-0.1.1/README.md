# PyWhatsWeb 🚀 v

Uma biblioteca Python poderosa para automação do WhatsApp Web, baseada no `whatsapp-web.js` do Node.js.

[![PyPI version](https://badge.fury.io/py/pywhatsweb.svg)](https://badge.fury.io/py/pywhatsweb)
[![Python versions](https://img.shields.io/pypi/pyversions/pywhatsweb.svg)](https://pypi.org/project/pywhatsweb/)
[![License](https://img.shields.io/pypi/l/pywhatsweb.svg)](https://pypi.org/project/pywhatsweb/)

## ✨ Características

- 🔐 **Autenticação QR Code** automática
- 💬 **Envio de mensagens** (texto, mídia, localização)
- 👥 **Gerenciamento de grupos** (criar, adicionar/remover membros)
- 📱 **Eventos em tempo real** (mensagens, conexão, desconexão)
- 🎯 **Configuração flexível** (headless, timeouts, Chrome options)
- 🧪 **Testes completos** com pytest
- 📚 **Documentação detalhada** e exemplos práticos

## 🚀 Instalação

### PyPI Oficial (Recomendado)
```bash
pip install pywhatsweb
```

### TestPyPI (Versão de teste)
```bash
pip install -i https://test.pypi.org/simple pywhatsweb
```

### Desenvolvimento
```bash
git clone https://github.com/llongaray/pywhatsweb.git
cd pywhatsweb
pip install -e .
```

## 📖 Uso Básico

### 1. Uso Simples (Terminal)

```bash
# Instalar
pip install pywhatsweb

# Usar via CLI
pywhatsweb --help
pywhatsweb --qr-only  # Apenas gerar QR code
pywhatsweb --send "5511999999999" "Olá! Teste da biblioteca PyWhatsWeb"
```

### 2. Uso em Python Puro

```python
from pywhatsweb import WhatsAppClient, Config

# Configuração básica
config = Config(
    headless=False,  # Mostrar navegador
    timeout=30,      # Timeout de conexão
    debug=True       # Logs detalhados
)

# Criar cliente
client = WhatsAppClient(config)

# Conectar e aguardar QR code
client.connect()
client.wait_for_qr_code()

# Enviar mensagem
client.send_message("5511999999999", "Olá! Teste da PyWhatsWeb!")

# Desconectar
client.disconnect()
```

### 3. Uso com Eventos

```python
from pywhatsweb import WhatsAppClient, Config

def on_message(message):
    print(f"📨 Nova mensagem: {message.content}")
    if message.content.lower() == "oi":
        client.send_message(message.sender.phone, "Olá! Como posso ajudar?")

def on_connection():
    print("✅ Conectado ao WhatsApp!")

def on_disconnection():
    print("❌ Desconectado do WhatsApp!")

# Configurar eventos
client = WhatsAppClient(Config(debug=True))
client.on_message = on_message
client.on_connection = on_connection
client.on_disconnection = on_disconnection

# Conectar
client.connect()
client.wait_for_qr_code()

# Manter conectado
try:
    while True:
        import time
        time.sleep(1)
except KeyboardInterrupt:
    client.disconnect()
```

## 🌐 Integração com Frameworks Web

### Django

#### 1. Instalação
```bash
pip install pywhatsweb
pip install django
```

#### 2. Configuração (settings.py)
```python
# settings.py
INSTALLED_APPS = [
    # ... outros apps
    'whatsapp',  # seu app
]

# Configurações do WhatsApp
WHATSAPP_CONFIG = {
    'headless': True,
    'timeout': 30,
    'user_data_dir': 'whatsapp_data/',
    'debug': False,
}
```

#### 3. Models (models.py)
```python
# models.py
from django.db import models
from django.contrib.auth.models import User

class WhatsAppSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)
    session_data = models.JSONField(default=dict)
    
    class Meta:
        unique_together = ['user', 'phone']

class WhatsAppMessage(models.Model):
    session = models.ForeignKey(WhatsAppSession, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    content = models.TextField()
    message_type = models.CharField(max_length=20, default='text')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
```

#### 4. Views (views.py)
```python
# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from pywhatsweb import WhatsAppClient, Config
from .models import WhatsAppSession, WhatsAppMessage
import json

# Cliente global (em produção, use Redis ou similar)
whatsapp_client = None

@login_required
def whatsapp_dashboard(request):
    sessions = WhatsAppSession.objects.filter(user=request.user)
    return render(request, 'whatsapp/dashboard.html', {'sessions': sessions})

@login_required
def connect_whatsapp(request):
    global whatsapp_client
    
    if whatsapp_client is None:
        config = Config(
            headless=True,
            timeout=30,
            user_data_dir='whatsapp_data/',
            debug=False
        )
        whatsapp_client = WhatsAppClient(config)
        whatsapp_client.connect()
    
    # Gerar QR code
    qr_code = whatsapp_client.get_qr_code()
    
    return JsonResponse({
        'status': 'connected',
        'qr_code': qr_code,
        'message': 'WhatsApp conectado com sucesso!'
    })

@csrf_exempt
@login_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone = data.get('phone')
        message = data.get('message')
        
        if whatsapp_client and whatsapp_client.is_connected():
            # Enviar mensagem
            whatsapp_client.send_message(phone, message)
            
            # Salvar no banco
            session = WhatsAppSession.objects.get(user=request.user)
            WhatsAppMessage.objects.create(
                session=session,
                phone=phone,
                content=message,
                is_sent=True
            )
            
            return JsonResponse({'status': 'sent'})
        else:
            return JsonResponse({'status': 'error', 'message': 'WhatsApp não conectado'})
    
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'})

@login_required
def get_messages(request, phone):
    session = WhatsAppSession.objects.get(user=request.user)
    messages = WhatsAppMessage.objects.filter(
        session=session,
        phone=phone
    )[:50]  # Últimas 50 mensagens
    
    return JsonResponse({
        'messages': list(messages.values())
    })
```

#### 5. URLs (urls.py)
```python
# urls.py
from django.urls import path
from . import views

app_name = 'whatsapp'

urlpatterns = [
    path('', views.whatsapp_dashboard, name='dashboard'),
    path('connect/', views.connect_whatsapp, name='connect'),
    path('send/', views.send_message, name='send_message'),
    path('messages/<str:phone>/', views.get_messages, name='get_messages'),
]
```

#### 6. Template (dashboard.html)
```html
<!-- templates/whatsapp/dashboard.html -->
{% extends 'base.html' %}

{% block content %}
<div class="whatsapp-dashboard">
    <h2>WhatsApp Dashboard</h2>
    
    <!-- Status de conexão -->
    <div class="connection-status">
        <h3>Status da Conexão</h3>
        <button id="connect-btn" class="btn btn-primary">Conectar WhatsApp</button>
        <div id="status" class="status-indicator"></div>
    </div>
    
    <!-- Enviar mensagem -->
    <div class="send-message">
        <h3>Enviar Mensagem</h3>
        <form id="message-form">
            <input type="tel" id="phone" placeholder="Telefone (ex: 5511999999999)" required>
            <textarea id="message" placeholder="Mensagem" required></textarea>
            <button type="submit" class="btn btn-success">Enviar</button>
        </form>
    </div>
    
    <!-- Histórico de mensagens -->
    <div class="message-history">
        <h3>Histórico de Mensagens</h3>
        <div id="messages"></div>
    </div>
</div>

<script>
// Conectar WhatsApp
document.getElementById('connect-btn').addEventListener('click', async () => {
    const response = await fetch('/whatsapp/connect/');
    const data = await response.json();
    
    if (data.status === 'connected') {
        document.getElementById('status').innerHTML = '✅ Conectado';
        document.getElementById('connect-btn').disabled = true;
    }
});

// Enviar mensagem
document.getElementById('message-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const phone = document.getElementById('phone').value;
    const message = document.getElementById('message').value;
    
    const response = await fetch('/whatsapp/send/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone, message })
    });
    
    const data = await response.json();
    
    if (data.status === 'sent') {
        alert('Mensagem enviada com sucesso!');
        document.getElementById('message-form').reset();
    } else {
        alert('Erro ao enviar mensagem: ' + data.message);
    }
});
</script>
{% endblock %}
```

### Flask

#### 1. Instalação
```bash
pip install pywhatsweb
pip install flask
pip install flask-sqlalchemy
```

#### 2. Aplicação Flask
```python
# app.py
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from pywhatsweb import WhatsAppClient, Config
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///whatsapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Cliente global
whatsapp_client = None

# Models
class WhatsAppSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    session_data = db.Column(db.JSON)

class WhatsAppMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_sent = db.Column(db.Boolean, default=False)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/connect', methods=['POST'])
def connect_whatsapp():
    global whatsapp_client
    
    if whatsapp_client is None:
        config = Config(headless=True, timeout=30)
        whatsapp_client = WhatsAppClient(config)
        whatsapp_client.connect()
    
    return jsonify({'status': 'connected'})

@app.route('/send', methods=['POST'])
def send_message():
    data = request.get_json()
    phone = data.get('phone')
    message = data.get('message')
    
    if whatsapp_client and whatsapp_client.is_connected():
        whatsapp_client.send_message(phone, message)
        
        # Salvar no banco
        db_message = WhatsAppMessage(phone=phone, content=message, is_sent=True)
        db.session.add(db_message)
        db.session.commit()
        
        return jsonify({'status': 'sent'})
    
    return jsonify({'status': 'error', 'message': 'WhatsApp não conectado'})

@app.route('/messages/<phone>')
def get_messages(phone):
    messages = WhatsAppMessage.query.filter_by(phone=phone).order_by(
        WhatsAppMessage.timestamp.desc()
    ).limit(50).all()
    
    return jsonify({
        'messages': [
            {
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'is_sent': msg.is_sent
            }
            for msg in messages
        ]
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

## 🗄️ Bancos de Dados

### SQLite3 (Padrão Django/Flask)
```python
# Django settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Flask app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///whatsapp.db'
```

### MySQL
```bash
# Instalar dependências
pip install mysqlclient  # Django
pip install pymysql      # Flask
```

```python
# Django settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'whatsapp_db',
        'USER': 'whatsapp_user',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# Flask app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://whatsapp_user:sua_senha@localhost/whatsapp_db'
```

### Sessions Locais (Redis)
```bash
pip install redis
```

```python
# Django settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Flask app.py
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=1)

# Armazenar sessão
def store_session(phone, session_data):
    redis_client.setex(f"whatsapp_session:{phone}", 3600, json.dumps(session_data))

# Recuperar sessão
def get_session(phone):
    data = redis_client.get(f"whatsapp_session:{phone}")
    return json.loads(data) if data else None
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```bash
# .env
WHATSAPP_HEADLESS=true
WHATSAPP_TIMEOUT=30
WHATSAPP_USER_DATA_DIR=whatsapp_data/
WHATSAPP_DEBUG=false
WHATSAPP_LOG_LEVEL=INFO
```

### Configuração Python
```python
from pywhatsweb import Config

config = Config(
    headless=True,                    # Modo headless
    timeout=30,                       # Timeout de conexão
    user_data_dir='whatsapp_data/',   # Diretório de dados
    chrome_options=[                  # Opções do Chrome
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
    ],
    wait_timeout=10,                  # Timeout de espera
    qr_timeout=60,                    # Timeout do QR code
    message_timeout=30,               # Timeout de mensagem
    debug=True,                       # Modo debug
    log_level='INFO'                  # Nível de log
)
```

## 🧪 Testes

```bash
# Executar testes
python -m pytest

# Com cobertura
python -m pytest --cov=pywhatsweb

# Testes específicos
python -m pytest tests/test_client.py -v
```

## 📚 Exemplos Completos

### Bot de Atendimento Automático
```python
from pywhatsweb import WhatsAppClient, Config
import re

class WhatsAppBot:
    def __init__(self):
        self.client = WhatsAppClient(Config(debug=True))
        self.commands = {
            r'oi|olá|ola': 'Olá! Como posso ajudar?',
            r'ajuda|help': 'Comandos disponíveis:\n- oi: Saudação\n- ajuda: Esta mensagem\n- contato: Informações de contato',
            r'contato': 'Entre em contato: contato@empresa.com',
            r'preço|valor': 'Consulte nossos preços em: empresa.com/precos',
        }
    
    def start(self):
        self.client.on_message = self.handle_message
        self.client.connect()
        self.client.wait_for_qr_code()
        
        print("🤖 Bot iniciado! Aguardando mensagens...")
        
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            self.client.disconnect()
            print("Bot finalizado!")
    
    def handle_message(self, message):
        content = message.content.lower()
        response = "Desculpe, não entendi. Digite 'ajuda' para ver os comandos."
        
        for pattern, reply in self.commands.items():
            if re.search(pattern, content):
                response = reply
                break
        
        self.client.send_message(message.sender.phone, response)
        print(f"📨 Respondido para {message.sender.phone}: {response}")

if __name__ == "__main__":
    bot = WhatsAppBot()
    bot.start()
```

## 🚨 Solução de Problemas

### Erro de Conexão
```python
try:
    client.connect()
except Exception as e:
    print(f"Erro de conexão: {e}")
    # Verificar se o Chrome está instalado
    # Verificar permissões de rede
```

### QR Code não aparece
```python
# Forçar modo não-headless para debug
config = Config(headless=False, debug=True)
client = WhatsAppClient(config)
```

### Mensagens não são enviadas
```python
# Verificar status de conexão
if client.is_connected():
    client.send_message(phone, message)
else:
    print("WhatsApp não está conectado!")
```

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, leia o [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre nosso código de conduta e o processo para enviar pull requests.

## 📞 Suporte

- 📧 Email: ti.leo@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/llongaray/pywhatsweb/issues)
- 📚 Documentação: [GitHub README](https://github.com/llongaray/pywhatsweb#readme)

## ⚠️ Aviso Legal

Esta biblioteca é para fins educacionais e de desenvolvimento. Respeite os termos de serviço do WhatsApp e use de forma responsável. Os desenvolvedores não se responsabilizam pelo uso inadequado da biblioteca.

---

**Desenvolvido com ❤️ pela TI Léo Team**
