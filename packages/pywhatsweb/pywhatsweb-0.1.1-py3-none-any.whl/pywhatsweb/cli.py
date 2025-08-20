#!/usr/bin/env python3
"""
Interface de linha de comando para PyWhatsWeb
"""

import argparse
import sys
import time
from typing import Optional

from . import WhatsAppClient, Config


def main():
    """Função principal do CLI"""
    parser = argparse.ArgumentParser(
        description="PyWhatsWeb - Cliente de linha de comando para WhatsApp Web",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s --send "5511999999999" "Olá, mundo!"
  %(prog)s --listen
  %(prog)s --qr-only
        """
    )
    
    # Argumentos principais
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executar em modo headless (sem interface gráfica)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout em segundos (padrão: 30)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Ativar modo debug"
    )
    
    # Comandos
    parser.add_argument(
        "--send",
        nargs=2,
        metavar=("PHONE", "MESSAGE"),
        help="Enviar mensagem para um número"
    )
    
    parser.add_argument(
        "--listen",
        action="store_true",
        help="Escutar mensagens recebidas"
    )
    
    parser.add_argument(
        "--qr-only",
        action="store_true",
        help="Apenas gerar QR Code e sair"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="PyWhatsWeb 0.1.0"
    )
    
    args = parser.parse_args()
    
    # Verificar se pelo menos um comando foi especificado
    if not any([args.send, args.listen, args.qr_only]):
        parser.print_help()
        sys.exit(1)
    
    try:
        # Configurar cliente
        config = Config(
            headless=args.headless,
            timeout=args.timeout,
            debug=args.debug
        )
        
        client = WhatsAppClient(config=config)
        
        # Conectar
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
            
            # Executar comandos
            if args.send:
                phone, message = args.send
                print(f"📤 Enviando mensagem para {phone}...")
                
                success = client.send_message(phone, message)
                if success:
                    print("✅ Mensagem enviada com sucesso!")
                else:
                    print("❌ Falha ao enviar mensagem")
                    sys.exit(1)
            
            elif args.listen:
                print("🎧 Escutando mensagens... (Ctrl+C para sair)")
                
                def on_message(msg):
                    print(f"📨 {msg.sender.phone}: {msg.content}")
                
                client.on_message = on_message
                client.wait_forever()
            
            elif args.qr_only:
                print("✅ QR Code gerado com sucesso!")
                print(f"🔑 Código: {qr_code}")
        
        else:
            print("❌ Falha na conexão")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupção do usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.disconnect()


if __name__ == "__main__":
    main()
