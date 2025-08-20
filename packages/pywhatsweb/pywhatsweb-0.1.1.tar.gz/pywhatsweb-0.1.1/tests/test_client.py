"""
Testes para o cliente WhatsApp
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pywhatsweb import WhatsAppClient, Config
from pywhatsweb.exceptions import ConnectionError, AuthenticationError


class TestWhatsAppClient:
    """Testes para a classe WhatsAppClient"""
    
    def test_init_with_default_config(self):
        """Testa inicialização com configuração padrão"""
        client = WhatsAppClient()
        assert client.config is not None
        assert client.is_connected is False
        assert client.driver is None
    
    def test_init_with_custom_config(self):
        """Testa inicialização com configuração customizada"""
        config = Config(headless=True, timeout=60)
        client = WhatsAppClient(config=config)
        assert client.config.headless is True
        assert client.config.timeout == 60
    
    def test_init_with_env_config(self):
        """Testa inicialização com configuração de ambiente"""
        with patch.dict('os.environ', {
            'WHATSAPP_HEADLESS': 'true',
            'WHATSAPP_TIMEOUT': '45'
        }):
            client = WhatsAppClient()
            assert client.config.headless is True
            assert client.config.timeout == 45
    
    def test_connect_success(self):
        """Testa conexão bem-sucedida"""
        client = WhatsAppClient()
        
        # Mock do driver
        mock_driver = Mock()
        mock_driver.get.return_value = None
        
        with patch('selenium.webdriver.Chrome') as mock_chrome:
            mock_chrome.return_value = mock_driver
            client.connect()
            
            assert client.driver is not None
            assert client.wait is not None
            mock_driver.get.assert_called_once_with("https://web.whatsapp.com/")
    
    def test_connect_failure(self):
        """Testa falha na conexão"""
        client = WhatsAppClient()
        
        with patch('selenium.webdriver.Chrome', side_effect=Exception("Driver error")):
            with pytest.raises(ConnectionError):
                client.connect()
    
    def test_disconnect_success(self):
        """Testa desconexão bem-sucedida"""
        client = WhatsAppClient()
        client.driver = Mock()
        client.is_connected = True
        
        client.disconnect()
        
        assert client.is_connected is False
        assert client.driver is None
    
    def test_disconnect_no_driver(self):
        """Testa desconexão sem driver"""
        client = WhatsAppClient()
        client.is_connected = False
        
        # Não deve dar erro
        client.disconnect()
    
    def test_context_manager(self):
        """Testa uso como context manager"""
        with patch('selenium.webdriver.Chrome') as mock_chrome:
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            
            with WhatsAppClient() as client:
                assert client.driver is not None
            
            # Deve ter chamado disconnect
            mock_driver.quit.assert_called_once()


class TestConfig:
    """Testes para a classe Config"""
    
    def test_default_values(self):
        """Testa valores padrão"""
        config = Config()
        assert config.headless is False
        assert config.timeout == 30
        assert config.user_data_dir == "./whatsapp_data"
        assert config.debug is False
    
    def test_custom_values(self):
        """Testa valores customizados"""
        config = Config(
            headless=True,
            timeout=60,
            debug=True
        )
        assert config.headless is True
        assert config.timeout == 60
        assert config.debug is True
    
    def test_chrome_options_default(self):
        """Testa opções padrão do Chrome"""
        config = Config()
        options = config.get_chrome_options()
        
        assert "--no-sandbox" in options
        assert "--disable-dev-shm-usage" in options
        assert "--disable-blink-features=AutomationControlled" in options
    
    def test_chrome_options_headless(self):
        """Testa opções do Chrome em modo headless"""
        config = Config(headless=True)
        options = config.get_chrome_options()
        
        assert "--headless" in options
    
    def test_user_data_dir_creation(self, tmp_path):
        """Testa criação do diretório de dados"""
        data_dir = tmp_path / "whatsapp_data"
        config = Config(user_data_dir=str(data_dir))
        
        assert data_dir.exists()
        assert data_dir.is_dir()


class TestModels:
    """Testes para os modelos de dados"""
    
    def test_contact_phone_formatting(self):
        """Testa formatação de telefone"""
        from pywhatsweb.models import Contact
        
        # Testa telefone com código do país
        contact = Contact(phone="5511999999999")
        assert contact.phone == "5511999999999"
        
        # Testa telefone sem código do país
        contact = Contact(phone="11999999999")
        assert contact.phone == "5511999999999"
        
        # Testa telefone com caracteres especiais
        contact = Contact(phone="(11) 99999-9999")
        assert contact.phone == "5511999999999"
    
    def test_contact_validation(self):
        """Testa validação de contato"""
        from pywhatsweb.models import Contact
        
        with pytest.raises(ValueError):
            Contact(phone="")
    
    def test_message_validation(self):
        """Testa validação de mensagem"""
        from pywhatsweb.models import Message, Contact, MessageType
        
        sender = Contact(phone="5511999999999")
        recipient = Contact(phone="5511888888888")
        
        # Mensagem válida
        message = Message(
            id="test",
            content="Teste",
            sender=sender,
            recipient=recipient
        )
        assert message.content == "Teste"
        
        # Mensagem sem conteúdo deve dar erro
        with pytest.raises(ValueError):
            Message(
                id="test",
                content="",
                sender=sender,
                recipient=recipient
            )
    
    def test_group_operations(self):
        """Testa operações de grupo"""
        from pywhatsweb.models import Group, Contact
        
        group = Group(id="test", name="Teste")
        contact = Contact(phone="5511999999999")
        
        # Adicionar participante
        group.add_participant(contact)
        assert contact in group.participants
        
        # Remover participante
        group.remove_participant(contact)
        assert contact not in group.participants
        
        # Verificar admin
        assert not group.is_admin(contact)
        group.admins.append(contact)
        assert group.is_admin(contact)


if __name__ == "__main__":
    pytest.main([__file__])
