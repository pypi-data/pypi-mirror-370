"""
Utilitários para PyWhatsWeb
"""

import re
import phonenumbers
from typing import Optional, Tuple
from datetime import datetime, timezone
import pytz


def normalize_phone_number(phone: str, default_region: str = 'BR') -> str:
    """
    Normaliza número de telefone para formato E.164
    
    Args:
        phone: Número de telefone (qualquer formato)
        default_region: Região padrão para números sem código do país
        
    Returns:
        Número normalizado em formato E.164 (ex: +5511999999999)
        
    Raises:
        ValueError: Se o número for inválido
    """
    if not phone:
        raise ValueError("Número de telefone não pode ser vazio")
    
    # Remover caracteres especiais
    phone = re.sub(r'[^\d+]', '', phone)
    
    # Se já tem +, usar como está
    if phone.startswith('+'):
        try:
            parsed = phonenumbers.parse(phone)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError(f"Número inválido: {phone}")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception as e:
            raise ValueError(f"Erro ao parsear número {phone}: {e}")
    
    # Se não tem +, adicionar região padrão
    if not phone.startswith('+'):
        # Adicionar código do país se não presente
        if not phone.startswith('55'):  # Brasil
            phone = f"+55{phone}"
        else:
            phone = f"+{phone}"
    
    try:
        parsed = phonenumbers.parse(phone)
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError(f"Número inválido: {phone}")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception as e:
        raise ValueError(f"Erro ao parsear número {phone}: {e}")


def validate_phone_number(phone: str) -> Tuple[bool, str]:
    """
    Valida número de telefone
    
    Args:
        phone: Número de telefone
        
    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        normalized = normalize_phone_number(phone)
        return True, normalized
    except ValueError as e:
        return False, str(e)


def get_phone_info(phone: str) -> dict:
    """
    Obtém informações detalhadas do número de telefone
    
    Args:
        phone: Número de telefone normalizado
        
    Returns:
        Dicionário com informações do número
    """
    try:
        parsed = phonenumbers.parse(phone)
        
        return {
            'number': phone,
            'country_code': parsed.country_code,
            'national_number': parsed.national_number,
            'region': phonenumbers.region_code_for_number(parsed),
            'carrier': phonenumbers.carrier_name_for_number(parsed, 'pt'),
            'type': phonenumbers.number_type(parsed),
            'is_valid': phonenumbers.is_valid_number(parsed),
            'is_possible': phonenumbers.is_possible_number(parsed),
            'timezone': get_phone_timezone(parsed)
        }
    except Exception as e:
        return {
            'number': phone,
            'error': str(e),
            'is_valid': False
        }


def get_phone_timezone(parsed_number) -> Optional[str]:
    """
    Obtém timezone do número de telefone
    
    Args:
        parsed_number: Número parseado pelo phonenumbers
        
    Returns:
        Nome do timezone ou None
    """
    try:
        timezones = phonenumbers.time_zone_for_number(parsed_number)
        if timezones:
            return timezones[0]  # Primeiro timezone
        return None
    except:
        return None


def format_phone_for_display(phone: str, format_type: str = 'NATIONAL') -> str:
    """
    Formata número para exibição
    
    Args:
        phone: Número normalizado
        format_type: Tipo de formatação (NATIONAL, INTERNATIONAL, E164)
        
    Returns:
        Número formatado
    """
    try:
        parsed = phonenumbers.parse(phone)
        
        if format_type == 'NATIONAL':
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        elif format_type == 'INTERNATIONAL':
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        else:
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except:
        return phone


def generate_session_id(prefix: str = 'session', tenant_id: Optional[str] = None) -> str:
    """
    Gera ID único para sessão
    
    Args:
        prefix: Prefixo para o ID
        tenant_id: ID do tenant (opcional)
        
    Returns:
        ID único da sessão
    """
    import uuid
    import time
    
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    
    if tenant_id:
        return f"{prefix}_{tenant_id}_{timestamp}_{unique_id}"
    else:
        return f"{prefix}_{timestamp}_{unique_id}"


def validate_session_id(session_id: str) -> bool:
    """
    Valida formato do ID da sessão
    
    Args:
        session_id: ID da sessão
        
    Returns:
        True se válido, False caso contrário
    """
    # Padrão: session_[tenant_][timestamp]_[uuid]
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, session_id)) and len(session_id) <= 100


def get_current_timezone() -> str:
    """
    Obtém timezone atual do sistema
    
    Returns:
        Nome do timezone
    """
    try:
        return datetime.now().astimezone().tzinfo.zone or 'UTC'
    except:
        return 'UTC'


def format_timestamp(timestamp: datetime, timezone_name: str = 'America/Sao_Paulo') -> str:
    """
    Formata timestamp para timezone específico
    
    Args:
        timestamp: Timestamp
        timezone_name: Nome do timezone
        
    Returns:
        String formatada
    """
    try:
        tz = pytz.timezone(timezone_name)
        local_time = timestamp.astimezone(tz)
        return local_time.strftime('%Y-%m-%d %H:%M:%S %Z')
    except:
        return timestamp.isoformat()


# Constantes para validação
PHONE_REGEX = re.compile(r'^\+[1-9]\d{1,14}$')  # E.164
SESSION_ID_REGEX = re.compile(r'^[a-zA-Z0-9_-]{3,100}$')

# Timezones comuns no Brasil
BRAZIL_TIMEZONES = [
    'America/Sao_Paulo',      # Brasília (UTC-3)
    'America/Manaus',         # Manaus (UTC-4)
    'America/Belem',          # Belém (UTC-3)
    'America/Fortaleza',      # Fortaleza (UTC-3)
    'America/Recife',         # Recife (UTC-3)
    'America/Maceio',         # Maceió (UTC-3)
    'America/Aracaju',        # Aracaju (UTC-3)
    'America/Salvador',       # Salvador (UTC-3)
    'America/Vitoria',        # Vitória (UTC-3)
    'America/Rio_Branco'      # Rio Branco (UTC-5)
]
