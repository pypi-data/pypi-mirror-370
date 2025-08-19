"""
Класс Config для работы с конфигурациями
Содержит логику сериализации конфигураций в бинарный формат и вычисления хешей
"""

import hashlib
import json
import struct
import logging
import os
import uuid
from typing import Dict, Any, List, Union, Tuple, Optional

from ...core.serialization.meta import Meta, MetaData
from ...models.converters.meta_utils import is_system_meta, meta_to_json
from ...core.serialization.serializer import Serializer
from ...core.protocol.types import FieldType, EnumType, Flags
from ...core.utils.crc import CRC32

# Константы для маппинга типов
TYPE_MAPPING = {
    "int8": FieldType.INT8,
    "int16": FieldType.INT16,
    "int32": FieldType.INT32,
    "int64": FieldType.INT64,
    "uint8": FieldType.UINT8,
    "uint16": FieldType.UINT16,
    "uint32": FieldType.UINT32,
    "uint64": FieldType.UINT64,
    "float": FieldType.FLOAT,
    "string": FieldType.STRING,
    "enum": FieldType.ENUM,
    "array": FieldType.ARRAY,
    "bool": FieldType.BOOL,
    "data_map": FieldType.DATA_MAP,
    "data_map_array": FieldType.DATA_MAP_ARRAY,
    "meta_data": FieldType.META_DATA,
    "meta_data_array": FieldType.META_DATA_ARRAY
}

logger = logging.getLogger(__name__)

class Config:
    """
    Класс для работы с конфигурациями Protomorph.
    Поддерживает сериализацию конфигураций в бинарный формат.
    """
    
    def __init__(self, data: Union[Dict[str, Any], list]):
        """
        Инициализация конфигурации.
        
        Args:
            data: Словарь с данными конфигурации или список конфигураций
        """
        if isinstance(data, list):
            # Новая структура: массив объектов
            if not data:
                raise ValueError("Invalid data format: expected a non-empty list.")
            self.data = data
            self._validate_new_structure()
        elif isinstance(data, dict) and data:
            # Старая структура: словарь (для обратной совместимости)
            self.data = data
            self._validate_structure()
        else:
            raise ValueError("Invalid data format: expected a non-empty dictionary or list.")
        
        # Инициализируем кэш бинарных данных и хеша
        self._binary_cache = None
        self._binary_cache_valid = False
        self._hash_cache = None
        self._hash_cache_valid = False
    
    def _invalidate_cache(self) -> None:
        """Инвалидирует кэш бинарных данных и хеша при изменении конфигурации."""
        self._binary_cache = None
        self._binary_cache_valid = False
        self._hash_cache = None
        self._hash_cache_valid = False
    
    def _validate_structure(self) -> None:
        """Валидирует структуру данных конфигурации."""
        if not self._is_valid_structure():
            raise ValueError("Invalid config structure")
    
    def _is_valid_structure(self) -> bool:
        """Проверяет валидность структуры данных."""
        if not isinstance(self.data, dict):
            return False
        
        # Проверяем единичный конфиг
        if "hash" in self.data and "meta" in self.data and "data" in self.data:
            required_meta_fields = ["name", "id", "instance", "uuid", "uuid_desc", "fields"]
            required_data_fields = ["fields"]
            
            if not all(field in self.data["meta"] for field in required_meta_fields):
                logger.warning("Missing required meta fields")
                return False
            
            if not all(field in self.data["data"] for field in required_data_fields):
                logger.warning("Missing required data fields")
                return False
            
            return True
        
        # Проверяем множественные конфиги
        if len(self.data) > 0:
            for config_name, config_parts in self.data.items():
                if not isinstance(config_parts, list) or len(config_parts) != 2:
                    logger.warning(f"Invalid config format for '{config_name}'")
                    return False
                
                meta_json, data_json = config_parts
                if "meta" in meta_json:
                    meta_json = meta_json["meta"]
                if "data" in data_json:
                    data_json = data_json["data"]
                
                required_meta_fields = ["name", "id", "instance", "uuid", "uuid_desc", "fields"]
                if not all(field in meta_json for field in required_meta_fields):
                    logger.warning(f"Missing required meta fields in config '{config_name}'")
                    return False
            
            return True
        
        return False
    
    def _validate_new_structure(self) -> None:
        """Валидирует новую структуру данных конфигурации (массив объектов)."""
        if not self._is_valid_new_structure():
            raise ValueError("Invalid new config structure")
    
    def _is_valid_new_structure(self) -> bool:
        """Проверяет валидность новой структуры данных (массив объектов)."""
        if not isinstance(self.data, list):
            return False
        
        for config in self.data:
            if not isinstance(config, dict):
                return False
            
            # Проверяем обязательные поля
            required_fields = ["uuid", "uuid_desc", "instance", "name", "id", "fields", "data"]
            if not all(field in config for field in required_fields):
                return False
            
            # Проверяем, что fields - это список
            if not isinstance(config["fields"], list):
                return False
            
            # Проверяем, что data - это словарь
            if not isinstance(config["data"], dict):
                return False
        
        return True
    
    def is_single_config(self) -> bool:
        """Проверяет, является ли это единичным конфигом."""
        return "hash" in self.data and "meta" in self.data and "data" in self.data
    
    def is_multiple_configs(self) -> bool:
        """Проверяет, является ли это множественными конфигами."""
        if isinstance(self.data, list):
            return len(self.data) > 1
        return not self.is_single_config() and len(self.data) > 0
    
    def get_config_count(self) -> int:
        """Возвращает количество конфигов."""
        if self.is_single_config():
            return 1
        if isinstance(self.data, list):
            return len(self.data)
        return len(self.data)
    
    def _create_meta_from_json(self, meta_json: dict) -> Meta:
        """Создает объект Meta из JSON данных."""
        meta = Meta()
        meta.set_name(meta_json["name"])
        meta.set_id(meta_json["id"])
        meta.set_instance(meta_json["instance"])
        
        # Обрабатываем uuid
        uuid_str = meta_json["uuid"]
        if not uuid_str or uuid_str.strip() == "":
            logger.info(f"Empty UUID for config '{meta_json['name']}', using zero UUID")
            uuid_str = "00000000-0000-0000-0000-000000000000"
        
        # Обрабатываем uuid_desc
        uuid_desc_str = meta_json["uuid_desc"]
        if not uuid_desc_str or uuid_desc_str.strip() == "":
            logger.info(f"Empty UUID description for config '{meta_json['name']}', using zero UUID")
            uuid_desc_str = "00000000-0000-0000-0000-000000000000"
        
        # Создаем стандартные UUID объекты
        try:
            uuid_obj = uuid.UUID(uuid_str)
            uuid_desc_obj = uuid.UUID(uuid_desc_str)
        except ValueError as e:
            logger.error(f"Invalid UUID format: {e}")
            raise ValueError(f"Invalid UUID format in meta: {e}")
        
        # Устанавливаем UUID в Meta объект
        meta._uuid = uuid_obj
        meta._uuidCfgDescr = uuid_desc_obj
        
        # Устанавливаем флаги
        if "flags" in meta_json:
            meta._flags = meta_json["flags"]
        elif is_system_meta(meta_json):
            meta._flags = Flags.SYS_META
        
        return meta
    
    def _add_fields_to_meta(self, meta: Meta, fields_json: list, type_mapping: dict = None) -> None:
        """Добавляет поля в Meta объект из JSON."""
        if type_mapping is None:
            type_mapping = TYPE_MAPPING
        
        for field in fields_json:
            field_type_str = field["type"]
            field_type = type_mapping.get(field_type_str)
            if field_type is None:
                raise ValueError(f"Unknown field type: {field_type_str}")

            enum_map = None
            field_meta = None
            
            if field_type == FieldType.ENUM:
                enum_map = field.get("enum_values")
            elif field_type in [FieldType.DATA_MAP, FieldType.DATA_MAP_ARRAY]:
                if "meta" not in field:
                    raise ValueError(f"Field {field['key']} of type {field_type_str} must have 'meta' property")
                
                field_meta = self._create_meta_from_json(field["meta"])
                self._add_fields_to_meta(field_meta, field["meta"]["fields"], type_mapping)
            
            meta.add_field(field["key"], field_type, enum_mapping=enum_map, meta=field_meta)
    
    def _process_array_value(self, value) -> bytearray:
        """Обрабатывает значение массива и возвращает bytearray."""
        if isinstance(value, dict) and "array" in value:
            return bytearray(value["array"])
        elif isinstance(value, (bytes, bytearray)):
            return value
        elif isinstance(value, list):
            return bytearray(value)
        else:
            raise ValueError(f"Unexpected array value format: {type(value)}")
    
    def _process_meta_data_value(self, value: dict, type_mapping: dict) -> MetaData:
        """Обрабатывает значение META_DATA и возвращает MetaData объект."""
        if not (isinstance(value, dict) and "meta" in value and "data" in value):
            raise ValueError("META_DATA value must have 'meta' and 'data' properties")
        
        # Создаем вложенную мету
        nested_meta = self._create_meta_from_json(value["meta"])
        self._add_fields_to_meta(nested_meta, value["meta"]["fields"], type_mapping)
        
        # Создаем данные для вложенной меты
        nested_data = {}
        data_section = value["data"]
        if "data" in data_section:
            data_section = data_section["data"]
        
        for nested_field_data in data_section["fields"]:
            nested_field_name = nested_field_data["key"]
            nested_field_value = nested_field_data.get("value")
            if nested_field_value is not None:
                nested_field_type = nested_meta.get_field_type(nested_field_name)
                if nested_field_type == FieldType.ENUM:
                    nested_data[nested_field_name] = EnumType(nested_field_value)
                elif nested_field_type == FieldType.ARRAY:
                    nested_data[nested_field_name] = self._process_array_value(nested_field_value)
                else:
                    nested_data[nested_field_name] = nested_field_value
        
        return MetaData(nested_meta, nested_data)
    
    def _process_meta_data_array_value(self, value: list, type_mapping: dict) -> list:
        """Обрабатывает значение META_DATA_ARRAY и возвращает список MetaData объектов."""
        if not isinstance(value, list):
            raise ValueError("META_DATA_ARRAY value must be a list")
        
        meta_data_array = []
        for item in value:
            if isinstance(item, dict) and "meta" in item and "data" in item:
                meta_data_array.append(self._process_meta_data_value(item, type_mapping))
            else:
                logger.warning(f"Skipping invalid META_DATA_ARRAY item: {type(item)}")
        
        return meta_data_array
    
    def _process_data_map_value(self, value: dict) -> dict:
        """Обрабатывает значение DATA_MAP и возвращает словарь данных."""
        if not isinstance(value, dict):
            raise ValueError("DATA_MAP value must be a dictionary")
        
        data_map_data = {}
        for key, val in value.items():
            if isinstance(val, (int, float, str, bool, bytes, bytearray)):
                data_map_data[key] = val
            elif isinstance(val, list):
                data_map_data[key] = bytearray(val)
            else:
                logger.warning(f"Unsupported value type for DATA_MAP field '{key}': {type(val)}")
                data_map_data[key] = str(val)
        
        return data_map_data
    
    def _process_data_map_array_value(self, value) -> list:
        """Обрабатывает значение DATA_MAP_ARRAY и возвращает список словарей."""
        if isinstance(value, list):
            data_map_array = []
            for item in value:
                if isinstance(item, dict):
                    data_map_array.append(self._process_data_map_value(item))
                else:
                    logger.warning(f"Skipping invalid DATA_MAP_ARRAY item: {type(item)}")
            return data_map_array
        elif isinstance(value, dict):
            # Если значение - словарь, оборачиваем его в список
            logger.info("DATA_MAP_ARRAY received dict, wrapping in list")
            return [self._process_data_map_value(value)]
        else:
            raise ValueError(f"DATA_MAP_ARRAY value must be list or dict, got {type(value)}")
    
    def _process_field_value(self, field_type: FieldType, value, field_name: str, type_mapping: dict) -> any:
        """Обрабатывает значение поля в зависимости от его типа."""
        if value is None:
            return None
        
        try:
            if field_type == FieldType.ARRAY:
                return self._process_array_value(value)
            elif field_type == FieldType.ENUM:
                return EnumType(value)
            elif field_type == FieldType.META_DATA:
                return self._process_meta_data_value(value, type_mapping)
            elif field_type == FieldType.META_DATA_ARRAY:
                return self._process_meta_data_array_value(value, type_mapping)
            elif field_type == FieldType.DATA_MAP:
                return self._process_data_map_value(value)
            elif field_type == FieldType.DATA_MAP_ARRAY:
                return self._process_data_map_array_value(value)
            else:
                return value
        except Exception as e:
            logger.warning(f"Error processing field '{field_name}': {e}")
            return None
    
    def _create_data_dict(self, meta: Meta, data_values: dict, type_mapping: dict) -> dict:
        """Создает словарь данных из значений полей."""
        data_dict = {}
        
        for field in meta.fields():
            field_name = field.name
            value = data_values.get(field_name)
            
            if value is not None:
                processed_value = self._process_field_value(field.type, value, field_name, type_mapping)
                if processed_value is not None:
                    data_dict[field_name] = processed_value
        
        return data_dict
    
    def _process_single_config(self) -> bytearray:
        """Обрабатывает единичный конфиг (с полями hash, meta, data)."""
        logger.info("Processing single config with hash, meta, data fields")
        
        hash_hex = self.data["hash"]
        meta_json = self.data["meta"]
        data_json = self.data["data"]
        
        logger.info(f"Found hash: {hash_hex}")
        
        # Проверяем и дополняем поля в data_json
        if "uuid_desc" not in data_json:
            data_json["uuid_desc"] = meta_json.get("uuid_desc", "")
        if "instance" not in data_json:
            data_json["instance"] = meta_json.get("instance", 0)
        
        data_values = {field['key']: field.get('value') for field in data_json.get('fields', [])}
        
        # Создаем Meta объект
        meta = self._create_meta_from_json(meta_json)
        self._add_fields_to_meta(meta, meta_json["fields"])
        
        # Создаем словарь данных
        data_dict = self._create_data_dict(meta, data_values, TYPE_MAPPING)
        
        # Сериализуем
        meta_bytes = meta.pack()
        data_bytes = Serializer.serialize(meta, data_dict)
        
        return meta_bytes + data_bytes
    
    def _process_multiple_configs(self) -> bytearray:
        """Обрабатывает множественные конфиги."""
        logger.info(f"Processing {len(self.data)} configs")
        
        all_combined_data = bytearray()
        has_multiple_configs = len(self.data) > 1
        
        for config_name, config_parts in self.data.items():
            logger.info(f"Processing config: {config_name}")
            
            if not isinstance(config_parts, list) or len(config_parts) != 2:
                logger.warning(f"Skipping invalid format for '{config_name}'. Expected [meta, data]")
                continue
            
            meta_json, data_json = config_parts
            
            # Проверяем заголовки
            if "meta" in meta_json:
                meta_json = meta_json["meta"]
            if "data" in data_json:
                data_json = data_json["data"]
            
            # Проверяем и дополняем поля
            if "uuid_desc" not in data_json:
                data_json["uuid_desc"] = meta_json.get("uuid_desc", "")
            if "instance" not in data_json:
                data_json["instance"] = meta_json.get("instance", 0)
            
            data_values = {field['key']: field.get('value') for field in data_json.get('fields', [])}
            
            # Создаем Meta объект
            meta = self._create_meta_from_json(meta_json)
            self._add_fields_to_meta(meta, meta_json["fields"])
            
            # Создаем словарь данных
            data_dict = self._create_data_dict(meta, data_values, TYPE_MAPPING)
            
            # Сериализуем
            meta_bytes = meta.pack()
            data_bytes = Serializer.serialize(meta, data_dict)
            combined_data = meta_bytes + data_bytes
            
            # Добавляем размер для множественных конфигов
            if has_multiple_configs:
                config_size = len(combined_data)
                size_bytes = struct.pack('<H', config_size)
                all_combined_data.extend(size_bytes)
            
            all_combined_data.extend(combined_data)
        
        return all_combined_data
    
    @staticmethod
    def _extract_data_values_static(meta, data) -> dict:
        """
        Извлекает значения данных из словаря данных, исключая метаданные.
        
        Args:
            meta: Объект Meta
            data: Словарь данных
            
        Returns:
            Словарь только со значениями данных
        """
        data_values = {}
        for field in meta.fields():
            field_name = field.name
            if field_name in data:
                value = data[field_name]
                
                # Обрабатываем специальные типы
                if field.type == FieldType.ENUM:
                    if isinstance(value, EnumType):
                        data_values[field_name] = int(value)
                    else:
                        data_values[field_name] = value
                elif field.type == FieldType.ARRAY:
                    if isinstance(value, (bytes, bytearray)):
                        data_values[field_name] = list(value)
                    else:
                        data_values[field_name] = value
                else:
                    data_values[field_name] = value
        
        return data_values
    
    def _process_new_single_config(self) -> bytearray:
        """Обрабатывает единичный конфиг в новой структуре (массив с одним объектом)."""
        logger.info("Processing new single config structure")
        
        config = self.data[0]
        meta_json = {
            "uuid": config["uuid"],
            "uuid_desc": config["uuid_desc"],
            "instance": config["instance"],
            "name": config["name"],
            "id": config["id"],
            "fields": config["fields"]
        }
        data_values = config["data"]
        
        # Создаем Meta объект
        meta = self._create_meta_from_json(meta_json)
        self._add_fields_to_meta(meta, meta_json["fields"])
        
        # Создаем словарь данных
        data_dict = self._create_data_dict(meta, data_values, TYPE_MAPPING)
        
        # Сериализуем
        meta_bytes = meta.pack()
        data_bytes = Serializer.serialize(meta, data_dict)
        
        return meta_bytes + data_bytes
    
    def _process_new_multiple_configs(self) -> bytearray:
        """Обрабатывает множественные конфиги в новой структуре (массив объектов)."""
        logger.info(f"Processing {len(self.data)} new configs")
        
        all_combined_data = bytearray()
        
        for config in self.data:
            logger.info(f"Processing config: {config['name']} (UUID: {config['uuid']})")
            
            meta_json = {
                "uuid": config["uuid"],
                "uuid_desc": config["uuid_desc"],
                "instance": config["instance"],
                "name": config["name"],
                "id": config["id"],
                "fields": config["fields"]
            }
            data_values = config["data"]
            
            # Создаем Meta объект
            meta = self._create_meta_from_json(meta_json)
            self._add_fields_to_meta(meta, meta_json["fields"])
            
            # Создаем словарь данных
            data_dict = self._create_data_dict(meta, data_values, TYPE_MAPPING)
            
            # Сериализуем
            meta_bytes = meta.pack()
            data_bytes = Serializer.serialize(meta, data_dict)
            combined_data = meta_bytes + data_bytes
            
            # Для множественных конфигов ВСЕГДА добавляем префикс размера
            config_size = len(combined_data)
            size_bytes = struct.pack('<H', config_size)
            all_combined_data.extend(size_bytes)
            
            all_combined_data.extend(combined_data)
        
        return all_combined_data
    
    def _generate_binary_data(self) -> bytearray:
        """
        Генерирует бинарные данные с кэшированием.
        
        Returns:
            bytearray с бинарными данными
        """
        # Проверяем кэш
        if self._binary_cache_valid and self._binary_cache is not None:
            logger.debug("Using cached binary data")
            return self._binary_cache
        
        # Генерируем новые бинарные данные
        logger.debug("Generating new binary data")
        if isinstance(self.data, list):
            # Новая структура: массив объектов
            if len(self.data) == 1:
                result = self._process_new_single_config()
                logger.info("New single config detected: no size prefixes")
            else:
                result = self._process_new_multiple_configs()
                logger.info("New multiple configs detected: size prefixes added")
        else:
            # Старая структура: словарь
            if self.is_single_config():
                result = self._process_single_config()
                logger.info("Old single config detected: no size prefixes")
            else:
                result = self._process_multiple_configs()
                logger.info("Old multiple configs detected: size prefixes added")
        
        # Сохраняем в кэш
        self._binary_cache = result
        self._binary_cache_valid = True
        
        return result
    
    def serialize(self) -> bytearray:
        """
        Сериализует конфигурацию в бинарный формат.
        
        Returns:
            bytearray с бинарными данными
        """
        return self._generate_binary_data()
    
    def update_data(self, new_data: Union[Dict[str, Any], list]) -> None:
        """
        Обновляет данные конфигурации и инвалидирует кэш.
        
        Args:
            new_data: Новые данные конфигурации
        """
        if isinstance(new_data, list):
            if not new_data:
                raise ValueError("Invalid data format: expected a non-empty list.")
            self.data = new_data
            self._validate_new_structure()
        elif isinstance(new_data, dict) and new_data:
            self.data = new_data
            self._validate_structure()
        else:
            raise ValueError("Invalid data format: expected a non-empty dictionary or list.")
        
        # Инвалидируем кэш при изменении данных
        self._invalidate_cache()
    
    def get_binary_size(self) -> int:
        """
        Возвращает размер бинарных данных без их генерации, если кэш валиден.
        
        Returns:
            Размер бинарных данных в байтах
        """
        if self._binary_cache_valid and self._binary_cache is not None:
            return len(self._binary_cache)
        else:
            # Генерируем данные для получения размера
            binary_data = self._generate_binary_data()
            return len(binary_data)
    
    def calculate_hash(self, verbose: bool = False, return_big_endian: bool = False) -> Union[str, Tuple[str, str]]:
        """
        Вычисляет SHA256-хеш конфигурации по алгоритму calc_config_hash.py.
        
        Args:
            verbose: Если True, выводит детальную информацию о каждом блоке
            return_big_endian: Если True, возвращает кортеж (little_endian, big_endian), иначе только little_endian
            
        Returns:
            Little-endian хеш в hex формате или кортеж (little_endian_hash, big_endian_hash)
        """
        # Проверяем кэш хеша (только для не-verbose режима)
        if not verbose and self._hash_cache_valid and self._hash_cache is not None:
            logger.debug("Using cached hash")
            if return_big_endian:
                return self._hash_cache[0], self._hash_cache[1]
            else:
                return self._hash_cache[0]

        hash_obj = hashlib.sha256()

        # Источник бинарных данных для хеширования:
        # 1) если конфигурация создана из бинаря (from_binary_data), используем исходные байты
        # 2) иначе используем сериализацию текущего объекта
        if hasattr(self, "_original_binary_data") and isinstance(self._original_binary_data, (bytes, bytearray)):
            binary_data = bytes(self._original_binary_data)
            # Детектируем наличие префиксов размеров, как в from_binary_data
            has_size_prefixes = False
            if len(binary_data) >= 2:
                first_size = struct.unpack('<H', binary_data[0:2])[0]
                if first_size > 0 and first_size < len(binary_data) - 2:
                    has_size_prefixes = True
        else:
            # Используем кэшированные бинарные данные
            binary_data = self._generate_binary_data()
            # Для множественных конфигов ВСЕГДА есть префиксы размеров
            has_size_prefixes = self.is_multiple_configs()

        current_offset = 0
        idx = 0
        blocks = []  # (uuid_bytes, instance, size, crcDt, original_idx)

        while current_offset < len(binary_data):
            if has_size_prefixes:
                # Для множественных конфигов - читаем размер блока
                if current_offset + 2 > len(binary_data):
                    if verbose:
                        print(f"Блок {idx}: недостаточно данных для чтения размера блока")
                    break

                block_size = struct.unpack('<H', binary_data[current_offset:current_offset+2])[0]
                current_offset += 2

                if current_offset + block_size > len(binary_data):
                    if verbose:
                        print(f"Блок {idx}: недостаточно данных для чтения блока, size={block_size}")
                    break

                block_data = binary_data[current_offset:current_offset+block_size]
                current_offset += block_size
            else:
                # Для единичного конфига - весь блок
                block_data = binary_data[current_offset:]
                current_offset = len(binary_data)

            # Извлекаем uuid и instance через Meta.unpack
            meta = Meta.unpack(bytes(block_data))
            if not meta:
                if verbose:
                    print(f"Блок {idx}: не удалось распаковать метаданные")
                continue

            uuid_bytes = meta.uuid().bytes
            instance = meta.instance()
            size = len(block_data)
            crcDt = CRC32.crc(block_data)

            blocks.append((uuid_bytes, instance, size, crcDt, idx))
            idx += 1

        # Сортируем блоки по UUID, чтобы исключить зависимость от исходного порядка
        blocks.sort(key=lambda x: x[0])

        # Обновляем хеш по отсортированным блокам
        for uuid_bytes, instance, size, crcDt, original_idx in blocks:
            hash_obj.update(uuid_bytes)
            hash_obj.update(struct.pack('<H', instance))
            hash_obj.update(struct.pack('<I', size))
            hash_obj.update(struct.pack('<I', crcDt))

            if verbose:
                print(f"config[{original_idx}]: uuid={uuid_bytes.hex()}, instance={instance}, size={size}, crcDt=0x{crcDt:08X}")
        
        # Вычисляем хеши в обоих форматах
        hash_bytes = hash_obj.digest()
        hash_le = hash_bytes[::-1]  # Обратный порядок байт (little-endian)
        
        # Сохраняем в кэш (только для не-verbose режима)
        if not verbose:
            self._hash_cache = (hash_le.hex(), hash_obj.hexdigest())
            self._hash_cache_valid = True
        
        if return_big_endian:
            return hash_le.hex(), hash_obj.hexdigest()
        else:
            return hash_le.hex()
    
    @classmethod
    def from_binary_data(cls, binary_data: bytes) -> 'Config':
        """
        Десериализует бинарные данные в объект Config.
        
        Args:
            binary_data: Бинарные данные конфигурации
            
        Returns:
            Список конфигураций в новом формате
        """
        all_configs_map = {}
        current_offset = 0
        
        # Проверяем, есть ли префиксы размеров (множественные конфигурации)
        has_size_prefixes = False
        if len(binary_data) >= 2:
            # Пытаемся прочитать первый размер
            first_size = struct.unpack('<H', binary_data[0:2])[0]
            # Если размер выглядит разумным (не слишком большой), считаем что это множественные конфигурации
            if first_size > 0 and first_size < len(binary_data) - 2:
                has_size_prefixes = True
        
        if has_size_prefixes:
            logger.info("Обнаружены множественные конфигурации с префиксами размеров")
            while current_offset < len(binary_data):
                # Читаем размер блока (2 байта)
                if current_offset + 2 > len(binary_data):
                    logger.warning(f"Недостаточно данных для чтения размера блока на позиции {current_offset}")
                    break
                block_size = struct.unpack('<H', binary_data[current_offset:current_offset+2])[0]
                current_offset += 2
                
                # Проверяем, что у нас достаточно данных для блока
                if current_offset + block_size > len(binary_data):
                    logger.warning(f"Неполный блок на позиции {current_offset}, ожидалось {block_size} байт")
                    break
                
                # Извлекаем данные блока
                block_data = binary_data[current_offset:current_offset+block_size]
                current_offset += block_size
                
                # Обрабатываем блок данных
                try:
                    meta = Meta.unpack(bytes(block_data))
                    if not meta.name():
                        logger.warning("Не удалось распаковать метаданные в блоке")
                        continue
                    meta_size = len(meta.pack())
                    
                    data = Serializer.deserialize(meta, block_data[meta_size:])
                    
                    # Проверяем, является ли UUID пустым (все нули)
                    uuid_str = str(meta.uuid())
                    if uuid_str == "00000000-0000-0000-0000-000000000000":
                        uuid_str = ""
                    
                    # Проверяем, является ли UUID описания пустым
                    uuid_desc_str = str(meta.uuidCfgDescr())
                    if uuid_desc_str == "00000000-0000-0000-0000-000000000000":
                        uuid_desc_str = ""
                    
                    # Создаем объект конфигурации в новом формате
                    config_obj = {
                        "uuid": uuid_str,
                        "uuid_desc": uuid_desc_str,
                        "instance": meta.instance(),
                        "name": meta.name(),
                        "id": meta.id(),
                        "fields": meta_to_json(meta)["fields"],
                        "data": Config._extract_data_values_static(meta, data)
                    }
                    
                    all_configs_map[f"{uuid_str}_{meta.instance()}"] = config_obj
                    system_info = " [СИСТЕМНАЯ]" if meta.is_system_meta() else ""
                    logger.info(f"Обработана конфигурация: {uuid_str}_{meta.instance()}{system_info}")
                    
                except Exception as e:
                    logger.error(f"Ошибка при обработке блока на позиции {current_offset - block_size}: {e}")
                    continue
        else:
            logger.info("Обрабатывается одиночная конфигурация")
            try:
                meta = Meta.unpack(bytes(binary_data))
                if not meta.name():
                    logger.error("Не удалось распаковать метаданные")
                    return {}
                
                meta_size = len(meta.pack())
                data = Serializer.deserialize(meta, binary_data[meta_size:])
                
                # Проверяем, является ли UUID пустым (все нули)
                uuid_str = str(meta.uuid())
                if uuid_str == "00000000-0000-0000-0000-000000000000":
                    uuid_str = ""
                
                # Проверяем, является ли UUID описания пустым
                uuid_desc_str = str(meta.uuidCfgDescr())
                if uuid_desc_str == "00000000-0000-0000-0000-000000000000":
                    uuid_desc_str = ""
                
                # Создаем объект конфигурации в новом формате
                config_obj = {
                    "uuid": uuid_str,
                    "uuid_desc": uuid_desc_str,
                    "instance": meta.instance(),
                    "name": meta.name(),
                    "id": meta.id(),
                    "fields": meta_to_json(meta)["fields"],
                                            "data": Config._extract_data_values_static(meta, data)
                }
                
                all_configs_map[f"{uuid_str}_{meta.instance()}"] = config_obj
                system_info = " [СИСТЕМНАЯ]" if meta.is_system_meta() else ""
                logger.info(f"Обработана конфигурация: {uuid_str}_{meta.instance()}{system_info}")
                
            except Exception as e:
                logger.error(f"Ошибка при обработке данных: {e}")
                return {}
        
        logger.info(f"Обработано конфигураций: {len(all_configs_map)}")
        # Возвращаем объект Config со списком конфигураций в новом формате
        # и сохраняем исходные бинарные данные для точного расчёта хеша
        instance = cls(list(all_configs_map.values()))
        try:
            instance._original_binary_data = bytes(binary_data)
        except Exception:
            instance._original_binary_data = None
        return instance
    
    @classmethod
    def from_binary_file(cls, file_path: str) -> 'Config':
        """
        Загружает конфигурации из бинарного файла.
        
        Args:
            file_path: Путь к бинарному файлу
            
        Returns:
            Объект Config с загруженными конфигурациями
        """
        try:
            with open(file_path, 'rb') as f:
                binary_data = f.read()
            
            logger.info(f"Файл прочитан, размер: {len(binary_data)} байт")
            return cls.from_binary_data(binary_data)
            
        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Ошибка при чтении файла: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Возвращает текущие данные конфигурации в виде словаря.
        
        Returns:
            Словарь с данными конфигурации
        """
        return self.data
    
    def to_json_string(self, indent: int = 4) -> str:
        """
        Сериализует конфигурацию в JSON строку.
        
        Args:
            indent: Отступ для форматирования JSON
            
        Returns:
            JSON строка
        """
        return json.dumps(self.data, ensure_ascii=False, indent=indent)
    
    def to_json_file(self, output_filename: str, indent: int = 4) -> None:
        """
        Сохраняет конфигурацию в JSON файл.
        
        Args:
            output_filename: Путь к выходному JSON файлу
            indent: Отступ для форматирования JSON
        """
        # Создаем папку для выходного файла, если она не существует
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                logger.info(f"Создана папка: {output_dir}")
            except Exception as e:
                logger.error(f"Ошибка при создании папки {output_dir}: {e}")
                raise
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=indent)
        
        logger.info(f"Успешно создан JSON файл: {output_filename}")
    
    def save(self, output_filename: str) -> None:
        """
        Сохраняет конфигурацию в бинарный файл.
        
        Args:
            output_filename: Путь к выходному файлу
        """
        # Создаем папку для выходного файла, если она не существует
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                logger.info(f"Created directory: {output_dir}")
            except Exception as e:
                logger.error(f"Error creating directory {output_dir}: {e}")
                raise
        
        # Сериализуем и сохраняем
        binary_data = self.serialize()
        
        with open(output_filename, "wb") as f:
            f.write(binary_data)
        
        logger.info(f"Successfully created binary file: {output_filename}")
        logger.info(f"Total size: {len(binary_data)} bytes")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """
        Создает объект Config из словаря.
        
        Args:
            data: Словарь с данными конфигурации
            
        Returns:
            Объект Config
        """
        return cls(data)
    
    @classmethod
    def from_json_string(cls, json_str: str) -> 'Config':
        """
        Создает объект Config из JSON строки.
        
        Args:
            json_str: JSON строка
            
        Returns:
            Объект Config
        """
        try:
            data = json.loads(json_str)
            return cls(data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
    
    @classmethod
    def from_file(cls, file_path: str, file_format: str = "auto") -> 'Config':
        """
        Создает объект Config из файла.
        
        Args:
            file_path: Путь к файлу
            file_format: Формат файла ("json", "yaml", или "auto" для автоопределения)
            
        Returns:
            Объект Config
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"File read, size: {len(content)} characters")
        
        if file_format == "auto":
            # Автоопределение формата по расширению
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.json', '.js']:
                file_format = "json"
            elif ext in ['.yml', '.yaml']:
                file_format = "yaml"
            else:
                # Пробуем определить по содержимому
                if content.strip().startswith('{') or content.strip().startswith('['):
                    file_format = "json"
                else:
                    file_format = "yaml"
            
            logger.info(f"Auto-detected format: {file_format}")
        
        # Парсим данные
        if file_format == "json":
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                raise ValueError(f"Invalid JSON format: {e}")
        elif file_format == "yaml":
            try:
                import yaml
                data = yaml.safe_load(content)
            except ImportError:
                logger.error("PyYAML is not installed. Install it with: pip install PyYAML")
                raise ImportError("PyYAML is required for YAML processing")
            except yaml.YAMLError as e:
                logger.error(f"YAML parsing error: {e}")
                raise ValueError(f"Invalid YAML format: {e}")
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
        
        return cls(data)