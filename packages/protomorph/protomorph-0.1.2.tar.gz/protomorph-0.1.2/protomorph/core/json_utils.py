"""
Утилиты для работы с JSON данными
Содержит функции для конвертации данных в JSON формат
"""

from typing import Any, Dict, List, Union


def convert_bytes_for_json(obj: Any) -> Any:
    """
    Конвертирует bytes объекты в hex строки для JSON сериализации
    
    Args:
        obj: Объект для конвертации
        
    Returns:
        Объект с конвертированными bytes в hex строки
    """
    if isinstance(obj, bytes):
        return obj.hex()
    elif isinstance(obj, dict):
        return {k: convert_bytes_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_bytes_for_json(item) for item in obj]
    else:
        return obj


def prepare_data_for_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Подготавливает данные для JSON сериализации
    
    Args:
        data: Словарь с данными
        
    Returns:
        Словарь с данными, готовыми для JSON сериализации
    """
    return convert_bytes_for_json(data)


def create_hello_payload(device_imei: str, data: Dict[str, Any], 
                        schema_version: int = 1) -> Dict[str, Any]:
    """
    Создает payload для hello сообщения
    
    Args:
        device_imei: IMEI устройства
        data: Данные устройства
        schema_version: Версия схемы
        
    Returns:
        Словарь с hello payload
    """
    from datetime import datetime
    
    return {
        "schema_version": schema_version,
        "device_imei": device_imei,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **prepare_data_for_json(data)
    } 