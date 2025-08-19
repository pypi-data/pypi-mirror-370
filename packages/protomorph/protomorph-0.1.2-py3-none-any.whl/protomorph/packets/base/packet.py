"""
Базовый класс для работы с сетевыми пакетами
Содержит общую логику для всех типов пакетов
"""

import struct
from typing import Optional, Tuple
from abc import ABC, abstractmethod

from ...core.protocol.constants import (
    Version, MessageCategory, MIN_PACKET_SIZE, HEADER_SIZE, CRC_SIZE
)
from ...core.utils.crc import CRC16

class Packet(ABC):
    """Базовый класс для всех пакетов протокола"""
    
    def __init__(self, version: int, category: int, message_id: int, 
                 type_val: int, payload_length: int = 0):
        self.version = version
        self.category = category
        self.message_id = message_id
        self.type = type_val
        self.payload_length = payload_length
    
    @abstractmethod
    def pack(self) -> bytes:
        """Упаковывает пакет в байты"""
        pass
    
    @staticmethod
    @abstractmethod
    def unpack(data: bytes) -> 'Packet':
        """Распаковывает пакет из байтов"""
        pass
    
    @staticmethod
    def create_header(version: int, category: int, message_id: int, 
                     type_val: int, payload_length: int) -> bytes:
        """Создает заголовок пакета"""
        return struct.pack("<BBHBH", version, category, message_id, type_val, payload_length)
    
    @staticmethod
    def unpack_header(data: bytes) -> Tuple[int, int, int, int, int]:
        """Распаковывает заголовок пакета"""
        if len(data) < HEADER_SIZE:
            raise ValueError("Недостаточно данных для заголовка")
        
        return struct.unpack("<BBHBH", data[:HEADER_SIZE])
    
    @staticmethod
    def add_crc(packet: bytes) -> bytes:
        """Добавляет CRC к пакету"""
        crc = CRC16.crc(packet)
        return packet + struct.pack("<H", crc)
    
    @staticmethod
    def validate_crc(data: bytes) -> bool:
        """Проверяет CRC пакета"""
        if len(data) < CRC_SIZE:
            return False
        
        received_crc = struct.unpack("<H", data[-CRC_SIZE:])[0]
        calculated_crc = CRC16.crc(data[:-CRC_SIZE])
        return received_crc == calculated_crc
    
    @staticmethod
    def validate_packet_size(data: bytes) -> bool:
        """Проверяет минимальный размер пакета"""
        return len(data) >= MIN_PACKET_SIZE
    
    @staticmethod
    def validate_packet_category(data: bytes, expected_category: int) -> bool:
        """Проверяет категорию пакета"""
        try:
            _, category, _, _, _ = Packet.unpack_header(data)
            return category == expected_category
        except ValueError:
            return False
    
    @staticmethod
    def get_payload(data: bytes) -> bytes:
        """Извлекает полезную нагрузку из пакета"""
        if len(data) < HEADER_SIZE + CRC_SIZE:
            return b''
        return data[HEADER_SIZE:-CRC_SIZE] 