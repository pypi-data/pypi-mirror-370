"""
Утилиты для работы с пакетами
Содержит функции валидации и создания пакетов
"""

import struct
from typing import Tuple

from .protocol.constants import Version, MessageCategory, AckStatus
from .utils.crc import CRC16
from ..packets.base.packet import Packet


def validate_packet_complete(data: bytes, expected_category: int, expected_type: int = None) -> bool:
    """
    Валидирует полный пакет
    
    Args:
        data: Бинарные данные пакета
        expected_category: Ожидаемая категория сообщения
        expected_type: Ожидаемый тип сообщения (опционально)
        
    Returns:
        True, если пакет валиден
    """
    if len(data) < 9:  # Minimum header size
        return False
    
    try:
        version, category, message_id, type_val, payload_length = Packet.unpack_header(data)
        
        if category != expected_category:
            return False
            
        if expected_type is not None and type_val != expected_type:
            return False
            
        # Проверяем CRC
        if len(data) < 9:  # header + crc
            return False
            
        calculated_crc = CRC16.crc(data[:-2])
        packet_crc = struct.unpack("<H", data[-2:])[0]
        
        return calculated_crc == packet_crc
        
    except Exception:
        return False


def create_simple_response(version: int, category: int, message_id: int, 
                          type_val: int, status: int = AckStatus.Success) -> bytes:
    """
    Создает простой ответный пакет
    
    Args:
        version: Версия протокола
        category: Категория сообщения
        message_id: ID сообщения
        type_val: Тип сообщения
        status: Статус ответа
        
    Returns:
        Байты пакета
    """
    # Создаем заголовок
    header = struct.pack("<BBHBB", version, category, message_id, type_val, 1)  # payload_length = 1 (status)
    
    # Добавляем статус
    payload = struct.pack("<B", status)
    
    # Добавляем CRC
    packet = header + payload
    crc = CRC16.crc(packet)
    
    return packet + struct.pack("<H", crc)


def create_ack_response(version: int, category: int, message_id: int, 
                       type_val: int, status: int) -> bytes:
    """
    Создает ACK ответный пакет
    
    Args:
        version: Версия протокола
        category: Категория сообщения
        message_id: ID сообщения
        type_val: Тип сообщения
        status: Статус ответа
        
    Returns:
        Байты пакета
    """
    return create_simple_response(version, category, message_id, type_val, status) 