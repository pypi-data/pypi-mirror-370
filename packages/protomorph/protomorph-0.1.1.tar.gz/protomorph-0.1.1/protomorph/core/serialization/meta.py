"""
Класс Meta для работы с метаданными
Содержит логику сериализации и десериализации метаданных
"""

import hashlib
import struct
from typing import List, Dict, Any, Optional
import uuid as uuid_module

from ..protocol.types import FieldType, Flags
from ..utils.crc import CRC16
from .varint import Varint

class MetaField:
    """Поле метаданных"""
    def __init__(self, name: str = "", field_type: int = FieldType.INT32, 
                 enum_mapping: Optional[Dict[str, int]] = None, meta: Optional['Meta'] = None):
        self.name = name
        self.type = field_type
        self.enum_mapping = enum_mapping if enum_mapping else {}
        self.meta = meta
        self.field_id = 0

class MetaData:
    def __init__(self, meta: Optional['Meta'] = None, data: Optional[Dict[str, Any]] = None):
        self._meta = meta
        self._data = data if data else {}

    def meta(self) -> 'Meta':
        return self._meta

    def data(self) -> Dict[str, Any]:
        return self._data

    def pack(self, recursion_counter: int = 0) -> bytearray:
        """Сериализует MetaData в байтовый массив."""
        if not self._meta:
            return bytearray()
        
        meta_bytes = self._meta.pack(recursion_counter)
        from .serializer import Serializer
        data_bytes = Serializer.serialize(self._meta, self._data, recursion_counter)
        return meta_bytes + data_bytes

    @staticmethod
    def unpack(buffer: bytes, recursion_counter: int = 0) -> Optional['MetaData']:
        """Десериализует MetaData из байтового массива."""
        if not buffer:
            return None
        
        # Сначала десериализуем мету
        meta = Meta.unpack(buffer, recursion_counter)
        if not meta:
            return None
        
        # Вычисляем размер меты
        meta_size = Meta.get_packet_meta_size(buffer)
        if meta_size >= len(buffer):
            return None
        
        # Десериализуем данные
        data_buffer = buffer[meta_size:]
        from .serializer import Serializer
        data = Serializer.deserialize(meta, data_buffer, recursion_counter)
        
        return MetaData(meta, data)

class Meta:
    META_MAGIC = 0x5343484D
    MAX_META_NAME_SIZE = 254
    VERSION = 8
    MAX_FIELDS_COUNT = 100
    MAX_RECURSION_COUNT = 3

    def __init__(self, name: str = "", uuid_obj: Optional[uuid_module.UUID] = None, uuidCfgDescr: Optional[uuid_module.UUID] = None, instance: int = 0):
        self._name = name
        self._uuid = uuid_obj if uuid_obj else uuid_module.UUID('00000000-0000-0000-0000-000000000000')
        self._uuidCfgDescr = uuidCfgDescr if uuidCfgDescr else uuid_module.UUID('00000000-0000-0000-0000-000000000000')
        self._instance = instance & 0xFF
        self._id = 0
        self._hash = b'\x00' * 32
        self._fields: List[MetaField] = []
        self._flags = Flags.NONE
        if name or uuid_obj:
            self._update_hash()

    def _update_hash(self):
        """Вычисляет хэш на основе UUID, instance и полей."""
        hasher = hashlib.sha256()
        
        hasher.update(self._uuid.bytes)
        hasher.update(struct.pack('<B', self._instance))

        for field in sorted(self._fields, key=lambda x: x.name):
            hasher.update(field.name.encode())
            hasher.update(struct.pack('<B', field.type))
            if field.type == FieldType.ENUM:
                for key, value in sorted(field.enum_mapping.items()):
                    hasher.update(key.encode())
                    hasher.update(struct.pack('<B', value))
            if field.meta:
                hasher.update(field.meta.hash_bytes())                
        
        self._hash = hasher.digest()

    def add_field(self, name: str, field_type: int, enum_mapping: Optional[Dict[str, int]] = None, meta: Optional['Meta'] = None) -> bool:
        """Добавляет поле в мета-описание."""
        if field_type == FieldType.ENUM and not enum_mapping:
            print(f"Ошибка: ENUM field must have a mapping of possible values.")
            return False
        
        if (field_type == FieldType.DATA_MAP or field_type == FieldType.DATA_MAP_ARRAY) and not meta:
            print(f"Ошибка: Meta field must have a meta")
            return False

        updated = False
        for field in self._fields:
            if field.name == name:
                if field.type != field_type:
                    field.type = field_type
                    updated = True
                if enum_mapping:
                    for key, value in enum_mapping.items():
                        if key not in field.enum_mapping:
                            field.enum_mapping[key] = value
                            updated = True
                if meta and field.meta != meta:
                    field.meta = meta
                    updated = True
                break

        if not updated:
            self._fields.append(MetaField(name, field_type, enum_mapping, meta))

        self._fields.sort(key=lambda x: x.name)
        for i, field in enumerate(self._fields):
            field.field_id = i
        self._update_hash()
        return True

    def pack(self, recursion_counter: int = 0) -> bytearray:
        """Сериализует мета-описание в байтовый массив с учетом флага CRC."""
        if recursion_counter > self.MAX_RECURSION_COUNT:
            print("Ошибка: Recursion limit reached")
            return bytearray()
        
        buffer = bytearray()
        header = struct.pack(
            "<IBBH16s16sBI32sIB", self.META_MAGIC, self.VERSION, self._flags, 0, self._uuid.bytes,
            self._uuidCfgDescr.bytes, self._instance, self._id, self._hash, len(self._fields), len(self._name)
        )
        buffer.extend(header)
        buffer.extend(self._name.encode()[:self.MAX_META_NAME_SIZE])

        for field in self._fields:
            name_bytes = field.name.encode()
            buffer.extend(struct.pack("<I", len(name_bytes)))
            buffer.extend(name_bytes)
            buffer.extend(struct.pack("<B", field.type))
            if field.type == FieldType.ENUM:
                buffer.extend(struct.pack("<I", len(field.enum_mapping)))
                for key, value in field.enum_mapping.items():
                    key_bytes = key.encode()
                    buffer.extend(struct.pack("<I", len(key_bytes)))
                    buffer.extend(key_bytes)
                    buffer.extend(struct.pack("<B", value))
            elif field.type == FieldType.DATA_MAP or field.type == FieldType.DATA_MAP_ARRAY:
                if field.meta:
                    field_meta_bytes = field.meta.pack(recursion_counter + 1)
                    buffer.extend(struct.pack("<I", len(field_meta_bytes)))
                    buffer.extend(field_meta_bytes)
                else:
                    buffer.extend(struct.pack("<I", 0))

        # Обновляем size
        header_size = struct.calcsize("<IBBH16s16sBI32sIB")
        buffer[6:8] = struct.pack("<H", len(buffer) - header_size)
        return buffer

    def pack_with_crc(self, crc: Optional[list] = None) -> bytearray:
        """Сериализует мета-описание с CRC16."""
        buffer = self.pack()
        flags = self._flags | Flags.HAS_CRC
        buffer[2] = flags
        
        crc16 = CRC16.crc(buffer)
        buffer.extend(struct.pack("<H", crc16))
        if crc is not None:
            crc.append(crc16)
        return buffer

    def set_id(self, id: int):
        self._id = id & 0xFFFFFFFF

    def set_name(self, name: str):
        self._name = name
        self._update_hash()

    def set_instance(self, instance: int):
        self._instance = instance & 0xFFFF
        self._update_hash()

    def id(self) -> int:
        return self._id

    def uuid(self) -> uuid_module.UUID:
        return self._uuid

    def uuidCfgDescr(self) -> uuid_module.UUID:
        return self._uuidCfgDescr

    def instance(self) -> int:
        return self._instance

    def fields(self) -> List[MetaField]:
        return self._fields

    def name(self) -> str:
        return self._name
    
    def hash(self) -> str:
        return self._hash.hex()
    
    def hash_bytes(self) -> bytes:
        return self._hash

    def flags(self) -> int:
        return self._flags

    def is_system_meta(self) -> bool:
        return bool(self._flags & Flags.SYS_META)

    @staticmethod
    def get_packet_meta_size(buffer: bytes) -> int:
        """Получает размер метаданных в пакете"""
        if len(buffer) < 4:
            return 0
        
        try:
            magic, version, flags, size = struct.unpack("<IBBH", buffer[:8])
            if magic != Meta.META_MAGIC:
                return 0
            
            # Базовый размер заголовка
            header_size = 8 + 16 + 16 + 1 + 4 + 32 + 4 + 1  # magic, version, flags, size, uuid, uuidCfgDescr, instance, id, hash, fields_count, name_length
            
            if len(buffer) < header_size:
                return 0
            
            # Читаем количество полей и длину имени
            fields_count, name_length = struct.unpack("<IB", buffer[header_size-5:header_size])
            
            # Размер имени
            name_size = min(name_length, Meta.MAX_META_NAME_SIZE)
            current_size = header_size + name_size
            
            # Читаем поля
            for i in range(fields_count):
                if current_size + 4 > len(buffer):
                    return 0
                
                field_name_length = struct.unpack("<I", buffer[current_size:current_size+4])[0]
                current_size += 4 + field_name_length
                
                if current_size + 1 > len(buffer):
                    return 0
                
                field_type = buffer[current_size]
                current_size += 1
                
                if field_type == FieldType.ENUM:
                    if current_size + 4 > len(buffer):
                        return 0
                    enum_count = struct.unpack("<I", buffer[current_size:current_size+4])[0]
                    current_size += 4
                    
                    for j in range(enum_count):
                        if current_size + 4 > len(buffer):
                            return 0
                        enum_key_length = struct.unpack("<I", buffer[current_size:current_size+4])[0]
                        current_size += 4 + enum_key_length + 1
                
                elif field_type in [FieldType.DATA_MAP, FieldType.DATA_MAP_ARRAY]:
                    if current_size + 4 > len(buffer):
                        return 0
                    meta_size = struct.unpack("<I", buffer[current_size:current_size+4])[0]
                    current_size += 4 + meta_size
            
            return current_size
            
        except struct.error:
            return 0

    @staticmethod
    def unpack(buffer: bytes, recursion_counter: int = 0, crc: Optional[list] = None) -> Optional['Meta']:
        """Десериализует мета-описание из байтового массива."""
        if recursion_counter > Meta.MAX_RECURSION_COUNT:
            print("Ошибка: Recursion limit reached")
            return None
        
        if len(buffer) < 8:
            return None
        
        try:
            magic, version, flags, size = struct.unpack("<IBBH", buffer[:8])
            if magic != Meta.META_MAGIC:
                return None
            
            if version != Meta.VERSION:
                print(f"Ошибка: Unsupported version {version}")
                return None
            
            # Проверяем CRC если есть флаг
            if flags & Flags.HAS_CRC:
                if len(buffer) < size + 2:
                    return None
                expected_crc = struct.unpack("<H", buffer[size:size+2])[0]
                calculated_crc = CRC16.crc(buffer[:size])
                if expected_crc != calculated_crc:
                    print(f"Ошибка: CRC mismatch {expected_crc} != {calculated_crc}")
                    return None
                if crc is not None:
                    crc.append(expected_crc)
            
            # Читаем UUID
            uuid_bytes = bytes(buffer[8:24])
            uuid_obj = uuid_module.UUID(bytes=uuid_bytes)
            
            # Читаем UUID описания
            uuid_desc_bytes = bytes(buffer[24:40])
            uuid_desc_obj = uuid_module.UUID(bytes=uuid_desc_bytes)
            
            # Читаем остальные поля
            instance, meta_id, hash_bytes, fields_count, name_length = struct.unpack("<BI32sIB", buffer[40:82])
            
            # Читаем имя
            name = buffer[82:82+name_length].decode('utf-8', errors='ignore')
            
            # Создаем объект Meta
            meta = Meta(name, uuid_obj, uuid_desc_obj, instance)
            meta._id = meta_id
            meta._hash = hash_bytes
            meta._flags = flags
            
            # Читаем поля
            current_offset = 82 + name_length
            for i in range(fields_count):
                if current_offset + 4 > len(buffer):
                    return None
                
                field_name_length = struct.unpack("<I", buffer[current_offset:current_offset+4])[0]
                current_offset += 4
                
                if current_offset + field_name_length > len(buffer):
                    return None
                
                field_name = buffer[current_offset:current_offset+field_name_length].decode('utf-8', errors='ignore')
                current_offset += field_name_length
                
                if current_offset + 1 > len(buffer):
                    return None
                
                field_type = buffer[current_offset]
                current_offset += 1
                
                enum_mapping = None
                field_meta = None
                
                if field_type == FieldType.ENUM:
                    if current_offset + 4 > len(buffer):
                        return None
                    enum_count = struct.unpack("<I", buffer[current_offset:current_offset+4])[0]
                    current_offset += 4
                    
                    enum_mapping = {}
                    for j in range(enum_count):
                        if current_offset + 4 > len(buffer):
                            return None
                        enum_key_length = struct.unpack("<I", buffer[current_offset:current_offset+4])[0]
                        current_offset += 4
                        
                        if current_offset + enum_key_length > len(buffer):
                            return None
                        enum_key = buffer[current_offset:current_offset+enum_key_length].decode('utf-8', errors='ignore')
                        current_offset += enum_key_length
                        
                        if current_offset + 1 > len(buffer):
                            return None
                        enum_value = buffer[current_offset]
                        current_offset += 1
                        
                        enum_mapping[enum_key] = enum_value
                
                elif field_type in [FieldType.DATA_MAP, FieldType.DATA_MAP_ARRAY]:
                    if current_offset + 4 > len(buffer):
                        return None
                    meta_size = struct.unpack("<I", buffer[current_offset:current_offset+4])[0]
                    current_offset += 4
                    
                    if meta_size > 0:
                        if current_offset + meta_size > len(buffer):
                            return None
                        field_meta = Meta.unpack(buffer[current_offset:current_offset+meta_size], recursion_counter + 1)
                        current_offset += meta_size
                
                meta.add_field(field_name, field_type, enum_mapping, field_meta)
            
            return meta
            
        except struct.error as e:
            print(f"Ошибка при распаковке мета: {e}")
            return None

    def get_field_type(self, field_name: str) -> Optional[int]:
        """Возвращает тип поля по имени."""
        for field in self._fields:
            if field.name == field_name:
                return field.type
        return None
