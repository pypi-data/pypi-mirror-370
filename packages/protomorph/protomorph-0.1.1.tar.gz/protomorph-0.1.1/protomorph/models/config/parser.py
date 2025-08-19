"""
Парсер конфигураций из бинарных данных
Содержит функции для парсинга конфигураций из различных бинарных форматов
"""

import struct
import logging
from typing import Dict, Any, Optional

from ...core.serialization.meta import Meta
from ...core.serialization.serializer import Serializer
from .serializer import create_hybrid_structure

logger = logging.getLogger(__name__)


def parse_config_payload(payload: bytes) -> Dict[str, Any]:
    """
    Парсит бинарный payload, содержащий одну или несколько конфигурационных блоков,
    в словарь используя гибридную структуру.
    
    Args:
        payload: Бинарные данные с конфигурациями
        
    Returns:
        Словарь с конфигурациями в гибридном формате
    """
    all_configs_map = {}
    current_offset = 0
    
    while current_offset < len(payload):
        if current_offset + 2 > len(payload):
            logger.warning("Incomplete block size at offset %d", current_offset)
            break
        
        block_size = struct.unpack("<H", payload[current_offset:current_offset+2])[0]
        current_offset += 2

        if current_offset + block_size > len(payload):
            logger.warning("Incomplete block at offset %d, expected %d bytes", current_offset, block_size)
            break
        
        block_data = payload[current_offset:current_offset+block_size]
        current_offset += block_size
        
        try:
            meta = Meta.unpack(block_data)
            if not meta.name():
                logger.warning("Failed to unpack meta data in block")
                continue
            meta_size = len(meta.pack())
            
            data = Serializer.deserialize(meta, block_data[meta_size:])
            
            config_name = str(meta.uuid())
            if config_name:
                config_key = f"{config_name}_{meta.instance()}"
                all_configs_map[config_key] = create_hybrid_structure(meta, data)
        except Exception as e:
            logger.error(f"Error parsing block at offset {current_offset - block_size}: {e}")
            continue
            
    return all_configs_map


def parse_single_config_from_blob(all_data: bytes) -> Dict[str, Any]:
    """
    Парсит бинарный blob, который не структурирован с размерами блоков.
    Используется для случая, когда одна большая конфигурация загружается по частям.
    
    Args:
        all_data: Бинарные данные конфигурации
        
    Returns:
        Словарь с конфигурациями в гибридном формате
    """
    configs = {}
    current_offset = 0
    
    while current_offset < len(all_data):
        try:
            meta = Meta.unpack(all_data[current_offset:])
            if not meta or not meta.name():
                logger.warning("Failed to unpack meta data, stopping processing")
                break
            meta_size = len(meta.pack())
            
            data = Serializer.deserialize(meta, all_data[current_offset + meta_size:])
            
            config_name = str(meta.uuid())
            if config_name:
                config_key = f"{config_name}_{meta.instance()}"
                configs[config_key] = create_hybrid_structure(meta, data)
            
            current_offset += meta_size + len(Serializer.serialize(meta, data))
        except Exception as e:
            logger.error(f"Error processing data at offset {current_offset}: {e}")
            break
            
    return configs


def parse_config_with_fallback(payload: bytes) -> Dict[str, Any]:
    """
    Парсит конфигурацию с автоматическим выбором метода парсинга.
    Сначала пытается использовать блочный парсинг, затем парсинг единого blob.
    
    Args:
        payload: Бинарные данные конфигурации
        
    Returns:
        Словарь с конфигурациями в гибридном формате
    """
    # Сначала пробуем блочный парсинг
    configs = parse_config_payload(payload)
    
    # Если не получилось, пробуем парсинг единого blob
    if not configs:
        logger.info("Block parsing failed, trying single blob parsing.")
        configs = parse_single_config_from_blob(payload)
    
    return configs 