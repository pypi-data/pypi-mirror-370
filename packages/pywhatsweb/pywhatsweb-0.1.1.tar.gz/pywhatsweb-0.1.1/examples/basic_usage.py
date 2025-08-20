#!/usr/bin/env python3
"""
Exemplo básico de uso do PyWhatsWeb

Este exemplo demonstra como:
1. Conectar ao WhatsApp Web
2. Aguardar QR Code
3. Enviar mensagem
4. Desconectar
"""

import time
from pywhatsweb import WhatsAppClient, Config


def main():
    """Função principal do exemplo"""
    print("🚀 Iniciando exemplo do PyWhatsWeb...")
    
    # Configuração personalizada (opcional)
    config = Config(
        headless=False,  # Mostrar navegador
        timeout=30,      # Timeout de 30 segundos
        debug=True       # Ativar logs de debug
    )
    
    # Criar cliente
    client = WhatsAppClient(config=config)
    
    try:
        # Conectar ao WhatsApp Web
        print("📱 Conectando ao WhatsApp Web...")
        client.connect()
        
        # Aguardar QR Code
        print("🔍 Aguardando QR Code...")
        qr_code = client.wait_for_qr()
        print(f"📋 QR Code gerado: {qr_code[:20]}...")
        print("📱 Escaneie o QR Code com seu WhatsApp!")
        
        # Aguardar conexão
        print("⏳ Aguardando conexão...")
        if client.wait_for_connection():
            print("✅ Conectado com sucesso!")
            
            # Aguardar um pouco para estabilizar
            time.sleep(3)
            
            # Enviar mensagem de teste
            phone = "5511999999999"  # Substitua pelo número real
            message = "Olá! Esta é uma mensagem de teste do PyWhatsWeb! 🚀"
            
            print(f"📤 Enviando mensagem para {phone}...")
            success = client.send_message(phone, message)
            
            if success:
                print("✅ Mensagem enviada com sucesso!")
            else:
                print("❌ Falha ao enviar mensagem")
            
            # Aguardar um pouco antes de desconectar
            print("⏳ Aguardando 5 segundos antes de desconectar...")
            time.sleep(5)
            
        else:
            print("❌ Falha na conexão")
            
    except KeyboardInterrupt:
        print("\n⚠️ Interrupção do usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        # Sempre desconectar
        print("🔌 Desconectando...")
        client.disconnect()
        print("✅ Desconectado com sucesso!")


def example_with_events():
    """Exemplo usando eventos"""
    print("\n🎯 Exemplo com eventos...")
    
    def on_message_received(message):
        print(f"📨 Nova mensagem de {message.sender.phone}: {message.content}")
        
        # Auto-resposta simples
        if "oi" in message.content.lower():
            response = "Oi! Como posso ajudar? 😊"
            client.send_message(message.sender.phone, response)
            print(f"🤖 Auto-resposta enviada: {response}")
    
    def on_connection():
        print("🔗 Conexão estabelecida!")
    
    def on_qr(qr_data):
        print(f"🔍 QR Code gerado: {qr_data[:20]}...")
    
    def on_ready():
        print("🚀 Cliente pronto para uso!")
    
    # Configurar cliente com eventos
    client = WhatsAppClient()
    client.on_message = on_message_received
    client.on_connection = on_connection
    client.on_qr = on_qr
    client.on_ready = on_ready
    
    try:
        # Conectar
        client.connect()
        
        # Aguardar QR Code
        client.wait_for_qr()
        print("📱 Escaneie o QR Code!")
        
        # Aguardar conexão
        if client.wait_for_connection():
            print("✅ Conectado! Aguardando mensagens...")
            
            # Manter conexão ativa
            client.wait_forever()
            
    except KeyboardInterrupt:
        print("\n⚠️ Interrupção do usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        client.disconnect()


if __name__ == "__main__":
    print("=" * 50)
    print("PyWhatsWeb - Exemplo Básico")
    print("=" * 50)
    
    # Executar exemplo básico
    main()
    
    # Perguntar se quer executar exemplo com eventos
    try:
        choice = input("\n🎯 Quer executar o exemplo com eventos? (s/n): ").lower()
        if choice in ['s', 'sim', 'y', 'yes']:
            example_with_events()
    except KeyboardInterrupt:
        print("\n👋 Até logo!")
    
    print("\n🎉 Exemplos concluídos!")
