"""
Класс AuthPacket для работы с пакетами авторизации
Содержит логику формирования и разбора пакетов авторизации
"""

import struct
from typing import Optional

from ...core.protocol.constants import (
    Version, MessageCategory, AuthMessageType, AuthStatus, HEADER_SIZE
)
from ...core.utils.crc import CRC16
from ..base.packet import Packet


class AuthPacket(Packet):
    """Класс для работы с пакетами авторизации"""
    
    def __init__(self, type_val: int, message_id: int = 0, payload: Optional[bytes] = None, 
                 status: Optional[int] = None):
        self.version = Version.LastVersion
        self.category = MessageCategory.Auth
        self.message_id = message_id
        self.type = type_val
        self.payload = payload or b''
        
        # payload_length для Auth пакетов
        if type_val in (AuthMessageType.HashAndData, AuthMessageType.MetaAndData):
            self.payload_length = len(self.payload)
        else:  # Ack, NoMeta
            self.payload_length = 1  # status
        
        self.status = status if status is not None else (AuthStatus.Success if type_val in (AuthMessageType.Ack, AuthMessageType.NoMeta) else None)

    def pack(self) -> bytes:
        """Упаковывает пакет в байты"""
        # Создаем заголовок пакета
        packet = struct.pack(
            "<BBHBH",
            self.version,
            self.category,
            self.message_id,
            self.type,
            self.payload_length
        )
        
        if self.type in (AuthMessageType.HashAndData, AuthMessageType.MetaAndData):
            packet += self.payload
        else:
            packet += struct.pack("<B", self.status)

        # Добавляем CRC к пакету
        crc = CRC16.crc(packet)
        return packet + struct.pack("<H", crc)

    @staticmethod
    def unpack(data: bytes) -> 'AuthPacket':
        """Распаковывает пакет из байтов"""
        if len(data) < 9:  # Minimum header size
            raise ValueError("Response too short")

        # Валидируем пакет
        if not AuthPacket.validate_packet_category(data, MessageCategory.Auth):
            raise ValueError("Invalid packet")

        # Распаковываем заголовок
        version, category, message_id, type_val, payload_length = AuthPacket.unpack_header(data)
        
        offset = HEADER_SIZE
        payload = b''
        status = None

        if type_val in (AuthMessageType.HashAndData, AuthMessageType.MetaAndData):
            payload = data[offset:-2]  # Все данные кроме CRC
        else:
            if len(data) < offset + 3:  # header + status + crc
                raise ValueError("Response too short")
            status = struct.unpack("<B", data[offset:offset+1])[0]
        
        return AuthPacket(type_val, message_id, payload, status)

    @classmethod
    def create_ack_response(cls, message_id: int, status: int = AuthStatus.Success) -> 'AuthPacket':
        """
        Создает ACK ответный пакет
        
        Args:
            message_id: ID сообщения
            status: Статус ответа
            
        Returns:
            AuthPacket для ACK
        """
        return cls(AuthMessageType.Ack, message_id, status=status)

    @classmethod
    def create_no_meta_response(cls, message_id: int) -> 'AuthPacket':
        """
        Создает NoMeta ответный пакет
        
        Args:
            message_id: ID сообщения
            
        Returns:
            AuthPacket для NoMeta
        """
        return cls(AuthMessageType.NoMeta, message_id, status=AuthStatus.Error)

    @classmethod
    def create_hash_and_data_packet(cls, message_id: int, hash_bytes: bytes, data_bytes: bytes) -> 'AuthPacket':
        """
        Создает HashAndData пакет
        
        Args:
            message_id: ID сообщения
            hash_bytes: Байты хеша (32 байта)
            data_bytes: Байты данных
            
        Returns:
            AuthPacket для HashAndData
        """
        payload = hash_bytes + data_bytes
        return cls(AuthMessageType.HashAndData, message_id, payload)

    @classmethod
    def create_meta_and_data_packet(cls, message_id: int, meta_bytes: bytes, data_bytes: bytes) -> 'AuthPacket':
        """
        Создает MetaAndData пакет
        
        Args:
            message_id: ID сообщения
            meta_bytes: Байты метаданных
            data_bytes: Байты данных
            
        Returns:
            AuthPacket для MetaAndData
        """
        payload = meta_bytes + data_bytes
        return cls(AuthMessageType.MetaAndData, message_id, payload) 