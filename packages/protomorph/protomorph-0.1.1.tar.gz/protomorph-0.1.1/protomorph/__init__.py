"""
Protomorph - библиотека для работы с протоколом Protomorph

Основные компоненты:
- core: базовые типы и сериализация
- packets: сетевые пакеты
- models: высокоуровневые модели данных
- transport: транспортный уровень
"""

# Экспорт основных классов
from .core.serialization.meta import Meta, MetaData, MetaField
from .core.serialization.serializer import Serializer
from .models.converters.meta_utils import data_to_json, meta_to_json, json_to_meta
from .core.protocol.constants import (
    Version, MessageCategory, ConfigType, AckStatus,
    PingMessageType, AuthMessageType, AuthStatus
)
from .core.protocol.types import FieldType, Flags
from .core.utils.crc import CRC32
from .core.packet_utils import validate_packet_complete, create_simple_response, create_ack_response
from .core.json_utils import convert_bytes_for_json, prepare_data_for_json, create_hello_payload
from .packets.base.packet import Packet
from .packets.messages.config import ConfigPacket
from .packets.messages.auth import AuthPacket
from .models.config import (
    Config, 
    parse_config_payload, 
    parse_single_config_from_blob, 
    parse_config_with_fallback,
    create_hybrid_structure,
    create_simple_config_structure,
    extract_config_values,
    extract_config_meta
)

__version__ = "0.1.0"
__all__ = [
    "Meta", "MetaData", "MetaField", "Serializer",
    "Version", "MessageCategory", "ConfigType", "AckStatus", "FieldType", "Flags", "CRC32",
    "PingMessageType", "AuthMessageType", "AuthStatus",
    "validate_packet_complete", "create_simple_response", "create_ack_response",
    "convert_bytes_for_json", "prepare_data_for_json", "create_hello_payload",
    "data_to_json", "meta_to_json", "json_to_meta",
    "ConfigPacket", "AuthPacket", "Config",
    "parse_config_payload", 
    "parse_single_config_from_blob", 
    "parse_config_with_fallback",
    "create_hybrid_structure",
    "create_simple_config_structure",
    "extract_config_values",
    "extract_config_meta"
]
