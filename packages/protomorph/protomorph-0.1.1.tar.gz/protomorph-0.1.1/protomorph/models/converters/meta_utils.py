"""
Утилиты для работы с Meta объектами и JSON
Содержит функции конвертации между Meta объектами и JSON форматом
"""

import json
from typing import Dict, Any, List, Optional

from ...core.serialization.meta import Meta, MetaData
from ...core.protocol.types import FieldType, EnumType, Flags

def is_system_meta(meta_json: dict) -> bool:
    """
    Определяет, является ли мета системной 
    """
   
    # Флаг системной меты уже установлен
    if meta_json.get("flags", 0) & Flags.SYS_META:
        return True
        
    return False

def get_field_name(field_type: int) -> str:
    """
    Конвертирует тип поля в строковое представление
    
    Args:
        field_type: Числовой тип поля из FieldType
        
    Returns:
        Строковое представление типа поля
    """
    type_mapping = {
        FieldType.INT8: "int8",
        FieldType.INT16: "int16", 
        FieldType.INT32: "int32",
        FieldType.INT64: "int64",
        FieldType.UINT8: "uint8",
        FieldType.UINT16: "uint16",
        FieldType.UINT32: "uint32",
        FieldType.UINT64: "uint64",
        FieldType.FLOAT: "float",
        FieldType.STRING: "string",
        FieldType.ENUM: "enum",
        FieldType.ARRAY: "array",
        FieldType.BOOL: "bool",
        FieldType.DATA_MAP: "data_map",
        FieldType.DATA_MAP_ARRAY: "data_map_array",
        FieldType.META_DATA: "meta_data",
        FieldType.META_DATA_ARRAY: "meta_data_array",
    }
    return type_mapping.get(field_type, "unknown")

def get_field_type_from_string(field_type_str: str) -> int:
    """
    Конвертирует строковое представление типа поля в числовое
    
    Args:
        field_type_str: Строковое представление типа поля
        
    Returns:
        Числовой тип поля из FieldType
        
    Raises:
        ValueError: Если тип поля неизвестен
    """
    type_mapping = {
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
        "meta_data_array": FieldType.META_DATA_ARRAY,
    }
    
    field_type = type_mapping.get(field_type_str)
    if field_type is None:
        raise ValueError(f"Unknown field type: {field_type_str}")
    return field_type

def meta_to_json(meta: Meta) -> dict:
    """
    Конвертирует объект Meta в JSON формат
    
    Args:
        meta: Объект Meta для конвертации
        
    Returns:
        Словарь с JSON представлением Meta
    """
    fields_json = []
    
    for field in meta.fields():
        field_json = {
            "key": field.name,
            "type": get_field_name(field.type)
        }
        
        # Добавляем enum_values для enum полей
        if field.type == FieldType.ENUM and field.enum_mapping:
            field_json["enum_values"] = field.enum_mapping
        
        # Добавляем вложенную мету для сложных типов
        if field.meta:
            field_json["meta"] = meta_to_json(field.meta)
        
        fields_json.append(field_json)
    
    return {
        "uuid": str(meta.uuid()),
        "uuid_desc": str(meta.uuidCfgDescr()),
        "instance": meta.instance(),
        "name": meta.name(),
        "id": meta.id(),
        "fields": fields_json
    }

def json_to_meta(meta_json: dict) -> Meta:
    """
    Конвертирует JSON в объект Meta
    
    Args:
        meta_json: Словарь с JSON представлением Meta
        
    Returns:
        Объект Meta
    """
    import uuid as uuid_module
    
    # Извлекаем UUID
    uuid_str = meta_json.get("uuid", "")
    uuid_obj = uuid_module.UUID(uuid_str) if uuid_str else uuid_module.uuid4()
    
    # Извлекаем UUID описания
    uuid_desc_str = meta_json.get("uuid_desc", "")
    uuid_desc_obj = uuid_module.UUID(uuid_desc_str) if uuid_desc_str else uuid_module.uuid4()
    
    # Создаем мета
    meta = Meta(
        name=meta_json.get("name", ""),
        uuid_obj=uuid_obj,
        uuidCfgDescr=uuid_desc_obj,
        instance=meta_json.get("instance", 0)
    )
    
    # Устанавливаем ID
    meta.set_id(meta_json.get("id", 0))
    
    # Добавляем поля
    fields = meta_json.get("fields", [])
    for field_json in fields:
        field_name = field_json.get("key", "")
        field_type_str = field_json.get("type", "int32")
        field_type = get_field_type_from_string(field_type_str)
        
        # Обработка enum
        enum_mapping = None
        if field_type == FieldType.ENUM:
            enum_mapping = field_json.get("enum_values", {})
        
        # Обработка вложенной меты
        nested_meta = None
        if "meta" in field_json:
            nested_meta = json_to_meta(field_json["meta"])
        
        # Добавляем поле
        meta.add_field(field_name, field_type, enum_mapping, nested_meta)
    
    return meta

def data_to_json(meta, data: dict) -> dict:
    """
    Конвертирует данные в JSON формат
    
    Args:
        meta: Объект Meta
        data: Словарь с данными
        
    Returns:
        Словарь с JSON представлением данных
    """
    fields_json = []
    
    for field in meta.fields():
        field_name = field.name
        field_value = data.get(field_name)
        
        field_json = {
            "key": field_name,
            "value": field_value
        }
        
        fields_json.append(field_json)
    
    return {
        "uuid_desc": str(meta.uuidCfgDescr()),
        "instance": meta.instance(),
        "fields": fields_json
    }

def archive_data_to_json(arch, meta: Meta, data: dict) -> dict:
    """
    Конвертирует архивные данные в JSON формат
    
    Args:
        arch: Архивные данные
        meta: Объект Meta
        data: Словарь с данными
        
    Returns:
        Словарь с JSON представлением архивных данных
    """
    # Пока возвращаем базовую структуру
    # В будущем можно добавить специфичную для архива логику
    return data_to_json(meta, data) 