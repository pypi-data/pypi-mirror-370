"""
Класс ConfigPacket для работы с конфигурационными пакетами
Содержит логику формирования и разбора пакетов конфигураций
"""

import struct
from typing import Optional

from ...core.protocol.constants import (
    Version, MessageCategory, ConfigType, AckStatus, HEADER_SIZE
)
from ...core.utils.crc import CRC16
from ..base.packet import Packet

class ConfigPacket(Packet):
    """Класс для работы с конфигурационными пакетами"""
    
    def __init__(self, type_val: int, request_type: int, uuid: Optional[bytes] = None, 
                 instance: int = 0, message_id: int = 0, payload: Optional[bytes] = None, 
                 status: Optional[int] = None):
        self.version = Version.LastVersion
        self.category = MessageCategory.Config
        self.message_id = message_id
        self.type = type_val
        self.uuid = uuid if uuid is not None else b'\x00' * 16
        self.instance = instance
        self.payload = payload or b''
        self.request_type = request_type

        # payload_length includes uuid (16), instance (2), and for ConfigAck: requestType (1) + status (1)
        if type_val == ConfigType.ConfigAck:
            self.payload_length = 2  # requestType + status
            if request_type in (ConfigType.GetConfigHash, ConfigType.GetAllConfig, ConfigType.GetConfigCrc):
                self.payload_length += len(self.payload)
            elif request_type in (ConfigType.GetConfig, ConfigType.DeleteConfig, ConfigType.SetConfig, ConfigType.GetConfigChunk, ConfigType.GetConfigCrc):
                self.payload_length += 16 + 2 + len(self.payload)  # uuid + instance + payload
            else:
                self.payload_length += len(self.payload)  # только payload для других типов
        elif type_val in (ConfigType.GetAllConfig, ConfigType.GetConfigHash, ConfigType.SetConfig):
            self.payload_length = len(self.payload)
        elif type_val == ConfigType.GetConfigChunk:
            self.payload_length = 16 + 2 + len(self.payload)  # uuid + instance + payload (payload содержит offset + size)
        elif type_val == ConfigType.GetConfigCrc:
            self.payload_length = 16 + 2  # uuid + instance (без payload)
        else:
            self.payload_length = 16 + 2 + len(self.payload)
        
        self.status = status if status is not None else (AckStatus.Success if type_val == ConfigType.ConfigAck else None)

    def pack(self) -> bytes:
        """Упаковывает пакет в байты"""
        # Создаем заголовок пакета
        packet = self.create_header(
            self.version, self.category, self.message_id, 
            self.type, self.payload_length
        )
        
        if self.type == ConfigType.ConfigAck:
            packet += struct.pack("<BB", self.request_type, self.status)
            # Для ConfigAck uuid/instance идут ДО status для SetConfig
            if self.request_type in (ConfigType.GetConfig, ConfigType.DeleteConfig, ConfigType.SetConfig, ConfigType.GetConfigChunk, ConfigType.GetConfigCrc):
                packet += struct.pack("<16sH", self.uuid, self.instance)
            # payload (если есть)
            packet += self.payload
        elif self.type in (ConfigType.GetConfig, ConfigType.DeleteConfig, ConfigType.GetConfigCrc):
            packet += struct.pack("<16sH", self.uuid, self.instance)
            packet += self.payload
        elif self.type == ConfigType.GetConfigChunk:
            packet += struct.pack("<16sH", self.uuid, self.instance)
            # offset + size (если payload есть)
            if self.payload and len(self.payload) >= 6:
                packet += self.payload[:6]
            else:
                packet += b'\x00' * 6
        else:
            packet += self.payload

        # Добавляем CRC к пакету
        return self.add_crc(packet)

    @staticmethod
    def unpack(data: bytes) -> 'ConfigPacket':
        """Распаковывает пакет из байтов"""
        if len(data) < 9:  # Minimum header size: version (1) + category (1) + messageId (2) + type (1) + payloadLength (2) + crc (2)
            raise ValueError("Response too short")

        # Валидируем пакет
        if not ConfigPacket.validate_packet_category(data, MessageCategory.Config):
            raise ValueError("Invalid packet")

        # Распаковываем заголовок
        version, category, message_id, type_val, payload_length = ConfigPacket.unpack_header(data)
        
        offset = HEADER_SIZE
        request_type = ConfigType.GetConfig
        status = None
        uuid_bytes = b'\x00' * 16
        instance = 0

        if type_val == ConfigType.ConfigAck:
            if len(data) < 10:  # Minimum size for ConfigAck: header (7) + requestType (1) + status (1) + crc (2)
                raise ValueError("Response too short")
            request_type = struct.unpack("<B", data[offset:offset+1])[0]
            offset += 1
            status = struct.unpack("<B", data[offset:offset+1])[0]
            offset += 1
            # Для ConfigAck uuid/instance идут ПОСЛЕ status
            if request_type in (ConfigType.GetConfig, ConfigType.DeleteConfig, ConfigType.SetConfig, ConfigType.GetConfigChunk, ConfigType.GetConfigCrc):
                if offset + 18 <= len(data) - 2:  # uuid(16) + instance(2) + crc(2)
                    uuid_bytes = data[offset:offset+16]
                    offset += 16
                    instance = struct.unpack("<H", data[offset:offset+2])[0]
                    offset += 2
        elif type_val in (ConfigType.GetAllConfig, ConfigType.GetConfigHash, ConfigType.GetConfigCrc):
             if len(data) < 9: # Minimum size for GetAllConfig: header (7) + crc (2)
                raise ValueError("Response too short")
        elif type_val == ConfigType.GetConfigChunk:
            if len(data) < 31:  # header (7) + uuid (16) + instance (2) + offset (4) + size (2) + crc (2)
                raise ValueError("Response too short")
        else:
            if len(data) < 25:  # Minimum size for others: header (7) + uuid (16) + instance (2) + crc (2)
                raise ValueError("Response too short")

        if type_val == ConfigType.GetConfigChunk:
            uuid_bytes = data[offset:offset+16]
            offset += 16
            instance = struct.unpack("<H", data[offset:offset+2])[0]
            offset += 2
            # offset + size (6 байт)
            offset += 6
        elif type_val in (ConfigType.GetConfig, ConfigType.DeleteConfig, ConfigType.GetConfigCrc):
            uuid_bytes = data[offset:offset+16]
            offset += 16
            instance = struct.unpack("<H", data[offset:offset+2])[0]
            offset += 2
        # payload
        payload = data[offset:-2] if offset < len(data) - 2 else b''
        
        return ConfigPacket(type_val, request_type, uuid_bytes, instance, message_id, payload, status)

    @classmethod
    def create_get_all_config_packet(cls, message_id: int = 0, offset: int = 0, size: int = 2048) -> 'ConfigPacket':
        """
        Создает пакет для запроса всех конфигураций
        
        Args:
            message_id: ID сообщения
            offset: Смещение для пагинации
            size: Размер запрашиваемых данных
            
        Returns:
            ConfigPacket для GetAllConfig
        """
        payload = struct.pack('<IH', offset, size)
        return cls(ConfigType.GetAllConfig, ConfigType.GetAllConfig, message_id=message_id, payload=payload)

    @classmethod
    def create_get_config_chunk_packet(cls, uuid: bytes, instance: int, offset: int, size: int, message_id: int = 0) -> 'ConfigPacket':
        """
        Создает пакет для запроса части конфигурации
        
        Args:
            uuid: UUID конфигурации
            instance: Инстанс конфигурации
            offset: Смещение в данных
            size: Размер запрашиваемой части
            message_id: ID сообщения
            
        Returns:
            ConfigPacket для GetConfigChunk
        """
        payload = struct.pack('<IH', offset, size)
        return cls(ConfigType.GetConfigChunk, ConfigType.GetConfigChunk, uuid, instance, message_id, payload)

    @classmethod
    def create_get_config_hash_packet(cls, message_id: int = 0) -> 'ConfigPacket':
        """
        Создает пакет для запроса хеша конфигурации
        
        Args:
            message_id: ID сообщения
            
        Returns:
            ConfigPacket для GetConfigHash
        """
        return cls(ConfigType.GetConfigHash, ConfigType.GetConfigHash, message_id=message_id)

    @classmethod
    def create_get_config_crc_packet(cls, uuid: bytes, instance: int, message_id: int = 0) -> 'ConfigPacket':
        """
        Создает пакет для запроса CRC конфигурации
        
        Args:
            uuid: UUID конфигурации
            instance: Инстанс конфигурации
            message_id: ID сообщения
            
        Returns:
            ConfigPacket для GetConfigCrc
        """
        return cls(ConfigType.GetConfigCrc, ConfigType.GetConfigCrc, uuid, instance, message_id)

    def get_total_size_from_config_too_large(self) -> Optional[int]:
        """
        Извлекает общий размер конфигурации из ответа ConfigTooLarge
        
        Returns:
            Общий размер конфигурации или None, если размер не найден
        """
        if (self.type == ConfigType.ConfigAck and 
            self.status == AckStatus.ConfigTooLarge and 
            self.payload and len(self.payload) >= 4):
            return struct.unpack('<I', self.payload[:4])[0]
        return None

    def is_success_response(self) -> bool:
        """
        Проверяет, является ли ответ успешным
        
        Returns:
            True, если ответ успешный
        """
        return (self.type == ConfigType.ConfigAck and 
                self.status in (AckStatus.Success, AckStatus.MoreData))

    def is_config_too_large_response(self) -> bool:
        """
        Проверяет, является ли ответ ConfigTooLarge
        
        Returns:
            True, если ответ ConfigTooLarge
        """
        return (self.type == ConfigType.ConfigAck and 
                self.status == AckStatus.ConfigTooLarge)