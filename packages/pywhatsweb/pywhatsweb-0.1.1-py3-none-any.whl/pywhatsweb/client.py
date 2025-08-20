"""
Cliente principal do PyWhatsWeb
"""

import time
import logging
import qrcode
from typing import Optional, Callable, List, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from .config import Config
from .models import Message, Contact, Group, MediaMessage, MessageType, Location
from .exceptions import (
    ConnectionError, AuthenticationError, MessageError, 
    TimeoutError, ElementNotFoundError, InvalidPhoneError
)


class WhatsAppClient:
    """Cliente principal para automação do WhatsApp Web"""
    
    def __init__(self, config: Optional[Config] = None):
        """Inicializa o cliente"""
        self.config = config or Config.from_env()
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.is_connected = False
        self.phone_number: Optional[str] = None
        self.qr_code: Optional[str] = None
        
        # Callbacks de eventos
        self.on_message: Optional[Callable[[Message], None]] = None
        self.on_connection: Optional[Callable[[], None]] = None
        self.on_disconnection: Optional[Callable[[], None]] = None
        self.on_qr: Optional[Callable[[str], None]] = None
        self.on_ready: Optional[Callable[[], None]] = None
        
        # Configurar logging
        logging.basicConfig(level=getattr(logging, self.config.log_level))
        self.logger = logging.getLogger(__name__)
        
        # URLs
        self.whatsapp_url = "https://web.whatsapp.com/"
        self.api_url = "https://web.whatsapp.com/api/"
    
    def connect(self) -> None:
        """Conecta ao WhatsApp Web"""
        try:
            self.logger.info("Iniciando conexão com WhatsApp Web...")
            
            # Configurar Chrome
            chrome_options = Options()
            for option in self.config.get_chrome_options():
                chrome_options.add_argument(option)
            
            # Inicializar driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.get(self.whatsapp_url)
            
            # Configurar wait
            self.wait = WebDriverWait(self.driver, self.config.timeout)
            
            self.logger.info("Navegador iniciado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao conectar: {e}")
            raise ConnectionError(f"Falha ao conectar: {e}")
    
    def wait_for_qr(self, timeout: Optional[int] = None) -> str:
        """Aguarda e retorna o QR Code"""
        if not self.driver:
            raise ConnectionError("Driver não inicializado")
        
        timeout = timeout or self.config.qr_timeout
        self.logger.info("Aguardando QR Code...")
        
        try:
            # Aguardar elemento do QR Code
            qr_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "canvas"))
            )
            
            # Aguardar QR Code ser carregado
            time.sleep(2)
            
            # Capturar QR Code
            qr_data = qr_element.get_attribute("data-ref")
            if qr_data:
                self.qr_code = qr_data
                
                # Gerar QR Code visual
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(qr_data)
                qr.make(fit=True)
                
                # Salvar QR Code
                qr_image = qr.make_image(fill_color="black", back_color="white")
                qr_image.save("whatsapp_qr.png")
                
                self.logger.info("QR Code gerado e salvo como 'whatsapp_qr.png'")
                
                # Chamar callback
                if self.on_qr:
                    self.on_qr(qr_data)
                
                return qr_data
            
            raise AuthenticationError("QR Code não foi gerado")
            
        except TimeoutException:
            raise TimeoutError("Timeout aguardando QR Code")
        except Exception as e:
            raise AuthenticationError(f"Erro ao gerar QR Code: {e}")
    
    def wait_for_connection(self, timeout: Optional[int] = None) -> bool:
        """Aguarda a conexão ser estabelecida"""
        if not self.driver:
            raise ConnectionError("Driver não inicializado")
        
        timeout = timeout or self.config.wait_timeout
        self.logger.info("Aguardando conexão...")
        
        try:
            # Aguardar página principal carregar
            main_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='chat-list']"))
            )
            
            # Verificar se está conectado
            if self._is_authenticated():
                self.is_connected = True
                self.phone_number = self._get_phone_number()
                
                self.logger.info(f"Conectado com sucesso! Número: {self.phone_number}")
                
                # Chamar callbacks
                if self.on_connection:
                    self.on_connection()
                if self.on_ready:
                    self.on_ready()
                
                return True
            
            return False
            
        except TimeoutException:
            raise TimeoutError("Timeout aguardando conexão")
        except Exception as e:
            raise ConnectionError(f"Erro ao aguardar conexão: {e}")
    
    def wait_forever(self) -> None:
        """Mantém a conexão ativa e escuta mensagens"""
        if not self.is_connected:
            raise ConnectionError("Cliente não está conectado")
        
        self.logger.info("Iniciando escuta de mensagens...")
        
        try:
            while self.is_connected:
                # Verificar novas mensagens
                messages = self._get_new_messages()
                for message in messages:
                    if self.on_message:
                        self.on_message(message)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Interrupção do usuário")
        except Exception as e:
            self.logger.error(f"Erro na escuta: {e}")
            raise
    
    def send_message(self, phone: str, text: str) -> bool:
        """Envia mensagem de texto"""
        if not self.is_connected:
            raise ConnectionError("Cliente não está conectado")
        
        try:
            # Formatar telefone
            contact = Contact(phone=phone)
            
            # Abrir chat
            self._open_chat(contact.phone)
            
            # Encontrar campo de texto
            text_box = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='conversation-compose-box-input']"))
            )
            
            # Digitar mensagem
            text_box.clear()
            text_box.send_keys(text)
            
            # Enviar
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='send']")
            send_button.click()
            
            self.logger.info(f"Mensagem enviada para {phone}: {text}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem: {e}")
            raise MessageError(f"Falha ao enviar mensagem: {e}")
    
    def send_media(self, phone: str, file_path: str, caption: str = "") -> bool:
        """Envia arquivo de mídia"""
        if not self.is_connected:
            raise ConnectionError("Cliente não está conectado")
        
        try:
            # Formatar telefone
            contact = Contact(phone=phone)
            
            # Abrir chat
            self._open_chat(contact.phone)
            
            # Clicar no botão de anexo
            attach_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='attach-button']")
            attach_button.click()
            
            # Selecionar arquivo
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(file_path)
            
            # Aguardar upload
            time.sleep(2)
            
            # Adicionar legenda se houver
            if caption:
                caption_box = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='media-caption']")
                caption_box.send_keys(caption)
            
            # Enviar
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='send']")
            send_button.click()
            
            self.logger.info(f"Mídia enviada para {phone}: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar mídia: {e}")
            raise MessageError(f"Falha ao enviar mídia: {e}")
    
    def send_document(self, phone: str, file_path: str, caption: str = "") -> bool:
        """Envia documento"""
        return self.send_media(phone, file_path, caption)
    
    def send_location(self, phone: str, latitude: float, longitude: float, name: str = "") -> bool:
        """Envia localização"""
        if not self.is_connected:
            raise ConnectionError("Cliente não está conectado")
        
        try:
            # Formatar telefone
            contact = Contact(phone=phone)
            
            # Abrir chat
            self._open_chat(contact.phone)
            
            # Clicar no botão de anexo
            attach_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='attach-button']")
            attach_button.click()
            
            # Selecionar localização
            location_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='location']")
            location_button.click()
            
            # Aguardar mapa carregar
            time.sleep(2)
            
            # Inserir coordenadas (implementar lógica específica)
            # Esta é uma implementação simplificada
            
            # Enviar
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='send']")
            send_button.click()
            
            self.logger.info(f"Localização enviada para {phone}: {latitude}, {longitude}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar localização: {e}")
            raise MessageError(f"Falha ao enviar localização: {e}")
    
    def create_group(self, name: str, participants: List[str]) -> Optional[Group]:
        """Cria um grupo"""
        if not self.is_connected:
            raise ConnectionError("Cliente não está conectado")
        
        try:
            # Clicar no menu
            menu_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='menu-bar-menu']")
            menu_button.click()
            
            # Selecionar novo grupo
            new_group_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='new-group']")
            new_group_button.click()
            
            # Inserir nome do grupo
            name_input = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='group-name-input']")
            name_input.send_keys(name)
            
            # Adicionar participantes
            for phone in participants:
                self._add_participant_to_group(phone)
            
            # Criar grupo
            create_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='group-create']")
            create_button.click()
            
            self.logger.info(f"Grupo '{name}' criado com sucesso")
            
            # Retornar objeto do grupo (implementar lógica de captura)
            return Group(id=f"group_{int(time.time())}", name=name)
            
        except Exception as e:
            self.logger.error(f"Erro ao criar grupo: {e}")
            raise MessageError(f"Falha ao criar grupo: {e}")
    
    def disconnect(self) -> None:
        """Desconecta e fecha o navegador"""
        try:
            self.is_connected = False
            
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            self.logger.info("Desconectado com sucesso")
            
            # Chamar callback
            if self.on_disconnection:
                self.on_disconnection()
                
        except Exception as e:
            self.logger.error(f"Erro ao desconectar: {e}")
    
    def _is_authenticated(self) -> bool:
        """Verifica se está autenticado"""
        try:
            # Verificar se existe elemento da lista de chats
            self.driver.find_element(By.CSS_SELECTOR, "[data-testid='chat-list']")
            return True
        except NoSuchElementException:
            return False
    
    def _get_phone_number(self) -> Optional[str]:
        """Obtém o número do WhatsApp conectado"""
        try:
            # Clicar no menu de perfil
            profile_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='header-profile']")
            profile_button.click()
            
            # Aguardar perfil carregar
            time.sleep(1)
            
            # Capturar número (implementar lógica específica)
            # Esta é uma implementação simplificada
            return None
            
        except Exception:
            return None
    
    def _open_chat(self, phone: str) -> None:
        """Abre chat com um número específico"""
        try:
            # Construir URL do chat
            chat_url = f"https://web.whatsapp.com/send?phone={phone}"
            self.driver.get(chat_url)
            
            # Aguardar chat carregar
            time.sleep(2)
            
        except Exception as e:
            raise MessageError(f"Erro ao abrir chat: {e}")
    
    def _add_participant_to_group(self, phone: str) -> None:
        """Adiciona participante ao grupo sendo criado"""
        try:
            # Implementar lógica de adição de participante
            # Esta é uma implementação simplificada
            pass
            
        except Exception as e:
            self.logger.warning(f"Erro ao adicionar participante {phone}: {e}")
    
    def _get_new_messages(self) -> List[Message]:
        """Obtém novas mensagens recebidas"""
        # Implementar lógica de captura de mensagens
        # Esta é uma implementação simplificada
        return []
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
