"""
Сериализатор конфигураций в гибридный формат
Содержит функции для создания гибридных структур с метаданными и значениями
"""

from typing import Dict, Any

from ...core.serialization.meta import Meta
from ...models.converters.meta_utils import meta_to_json, data_to_json


def create_hybrid_structure(meta: Meta, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Создает гибридную структуру конфигурации с частью 'descriptor' и 'values'.
    Это предоставляет всю необходимую информацию для UI, сохраняя значения простыми для backend.
    
    Args:
        meta: Объект Meta с метаданными конфигурации
        data: Словарь с данными конфигурации
        
    Returns:
        Словарь с гибридной структурой конфигурации
    """
    meta_json = meta_to_json(meta)
    data_json = data_to_json(meta, data)

    # 1. Строим meta
    meta_fields = {}
    if "fields" in meta_json:
        for field in meta_json["fields"]:
            field_key = field.get("key")
            if not field_key:
                continue
            
            field_info = {"type": field.get("type")}
            if "enum_values" in field:
                field_info["options"] = field["enum_values"]
            meta_fields[field_key] = field_info

    result_meta = {
        "uuid": meta_json.get("uuid"),
        "uuid_desc": meta_json.get("uuid_desc"),
        "name": meta_json.get("name"),
        "fields": meta_fields
    }

    # 2. Строим values (уплощенная data)
    values = {}
    if "data" in data_json and "fields" in data_json["data"]:
        for field in data_json["data"]["fields"]:
            if "value" in field:
                field_key = field.get("key")
                if not field_key:
                    continue
                
                # Обрабатываем вложенную структуру массива
                if isinstance(field["value"], dict) and "array" in field["value"]:
                    values[field_key] = field["value"]["array"]
                else:
                    values[field_key] = field["value"]
    
    return {
        "meta": result_meta,
        "values": values
    }


def create_simple_config_structure(meta: Meta, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Создает простую структуру конфигурации без разделения на meta и values.
    Полезно для случаев, когда нужна полная информация в одном объекте.
    
    Args:
        meta: Объект Meta с метаданными конфигурации
        data: Словарь с данными конфигурации
        
    Returns:
        Словарь с простой структурой конфигурации
    """
    meta_json = meta_to_json(meta)
    data_json = data_to_json(meta, data)
    
    return {
        "meta": meta_json,
        "data": data_json.get("data", {})
    }


def extract_config_values(meta: Meta, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Извлекает только значения из конфигурации, без метаданных.
    
    Args:
        meta: Объект Meta с метаданными конфигурации
        data: Словарь с данными конфигурации
        
    Returns:
        Словарь только со значениями конфигурации
    """
    data_json = data_to_json(meta, data)
    values = {}
    
    if "data" in data_json and "fields" in data_json["data"]:
        for field in data_json["data"]["fields"]:
            if "value" in field:
                field_key = field.get("key")
                if not field_key:
                    continue
                
                if isinstance(field["value"], dict) and "array" in field["value"]:
                    values[field_key] = field["value"]["array"]
                else:
                    values[field_key] = field["value"]
    
    return values


def extract_config_meta(meta: Meta) -> Dict[str, Any]:
    """
    Извлекает только метаданные конфигурации.
    
    Args:
        meta: Объект Meta с метаданными конфигурации
        
    Returns:
        Словарь с метаданными конфигурации
    """
    meta_json = meta_to_json(meta)
    
    meta_fields = {}
    if "fields" in meta_json:
        for field in meta_json["fields"]:
            field_key = field.get("key")
            if not field_key:
                continue
            
            field_info = {"type": field.get("type")}
            if "enum_values" in field:
                field_info["options"] = field["enum_values"]
            meta_fields[field_key] = field_info

    return {
        "uuid": meta_json.get("uuid"),
        "uuid_desc": meta_json.get("uuid_desc"),
        "name": meta_json.get("name"),
        "fields": meta_fields
    } 