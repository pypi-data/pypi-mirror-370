"""
Типы данных протокола
Содержит определения типов полей и перечислений
"""

class FieldType:
    """Типы полей в метаданных"""
    INT8 = 0
    INT16 = 1
    INT32 = 2
    INT64 = 3
    UINT8 = 4
    UINT16 = 5
    UINT32 = 6
    UINT64 = 7
    FLOAT = 8
    STRING = 9
    ENUM = 10
    ARRAY = 11
    BOOL = 12
    DATA_MAP = 13           # Мета в методанных, данные в данных
    DATA_MAP_ARRAY = 14     # Мета в методанных, в данных массив данных по мете из методанных
    META_DATA = 15          # В методанных только тип, в данных идет блоб мета+данные
    META_DATA_ARRAY = 16    # В методанных только тип, в данных идет массив из гибких блобов мета+данные

class Flags:
    """Флаги метаданных"""
    NONE = 0x00
    HAS_CRC = 0x01
    SYS_META = 0x02

class EnumType:
    """Тип для перечислений"""
    def __init__(self, value: int = 0):
        self._value = value

    def __int__(self) -> int:
        return self._value

    def __add__(self, other: 'EnumType') -> 'EnumType':
        return EnumType(self._value + int(other))

    def __eq__(self, other: 'EnumType') -> bool:
        return self._value == int(other) 