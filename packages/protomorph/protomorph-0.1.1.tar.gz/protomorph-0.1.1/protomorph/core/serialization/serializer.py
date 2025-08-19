"""
Класс Serializer для сериализации и десериализации данных
Содержит логику преобразования данных согласно мета-описанию
"""

import struct
from typing import Dict, Any, Optional, List
import uuid as uuid_module

from ..protocol.types import FieldType, EnumType
from .meta import Meta, MetaData
from .varint import Varint
from .zigzag import Zigzag

class Serializer:
    @staticmethod
    def serialize(meta: Meta, data: Dict[str, Any], recursion_counter: int = 0) -> bytearray:
        """Сериализует данные согласно мета-описанию."""
        if recursion_counter > Meta.MAX_RECURSION_COUNT:
            print("Ошибка: Recursion limit reached")
            return bytearray()
        
        buffer = bytearray()
        flags = 0  # NONE = 0x00
        header = struct.pack("<BB", meta.VERSION, flags)
        buffer.extend(header)
        
        meta_id = Varint.encode(meta.id())
        buffer.extend(meta_id)

        for name, value in data.items():
            field = next((f for f in meta.fields() if f.name == name), None)
            if not field:
                print(f"Ошибка: Wrong field name: {name}")
                return bytearray()

            field_id = Varint.encode(field.field_id)
            buffer.extend(field_id)

            if field.type == FieldType.INT8 and isinstance(value, int):
                buffer.extend(struct.pack("<b", value))
            elif field.type == FieldType.INT16 and isinstance(value, int):
                encoded = Varint.encode(Zigzag.encode_16(value))
                buffer.extend(encoded)
            elif field.type == FieldType.INT32 and isinstance(value, int):
                encoded = Varint.encode(Zigzag.encode_32(value))
                buffer.extend(encoded)
            elif field.type == FieldType.INT64 and isinstance(value, int):
                encoded = Varint.encode(Zigzag.encode_64(value))
                buffer.extend(encoded)
            elif field.type == FieldType.UINT8 and isinstance(value, int):
                buffer.extend(struct.pack("<B", value))
            elif field.type == FieldType.UINT16 and isinstance(value, int):
                encoded = Varint.encode(value)
                buffer.extend(encoded)
            elif field.type == FieldType.UINT32 and isinstance(value, int):
                encoded = Varint.encode(value)
                buffer.extend(encoded)
            elif field.type == FieldType.UINT64 and isinstance(value, int):
                encoded = Varint.encode(value)
                buffer.extend(encoded)
            elif field.type == FieldType.FLOAT and isinstance(value, float):
                buffer.extend(struct.pack("<f", value))
            elif field.type == FieldType.STRING and isinstance(value, str):
                length = Varint.encode(len(value))
                buffer.extend(length)
                buffer.extend(value.encode())
            elif field.type == FieldType.ENUM:
                if isinstance(value, str):
                    enum_value = field.enum_mapping.get(value)
                    if enum_value is None:
                        print(f"Ошибка: Invalid ENUM value {value} for field: {name}")
                        return bytearray()
                    buffer.extend(struct.pack("<B", enum_value))
                elif isinstance(value, (EnumType, int)):
                    enum_value = int(value) & 0xFF
                    buffer.extend(struct.pack("<B", enum_value))
            elif field.type == FieldType.ARRAY and isinstance(value, (bytes, bytearray)):
                length = Varint.encode(len(value))
                buffer.extend(length)
                buffer.extend(value)
            elif field.type == FieldType.BOOL and isinstance(value, bool):
                buffer.extend(struct.pack("<B", value))
            elif field.type == FieldType.DATA_MAP and isinstance(value, dict):
                if not field.meta:
                    print(f"Ошибка: Meta field must have a meta for field: {name}")
                    return bytearray()
                data_packed = Serializer.serialize(field.meta, value, recursion_counter + 1)
                length = Varint.encode(len(data_packed))
                buffer.extend(length)
                buffer.extend(data_packed)
            elif field.type == FieldType.DATA_MAP_ARRAY and isinstance(value, list):
                if not field.meta:
                    print(f"Ошибка: Meta field must have a meta for field: {name}")
                    return bytearray()
                count = Varint.encode(len(value))
                buffer.extend(count)
                for data_item in value:
                    if not isinstance(data_item, dict):
                        print(f"Ошибка: Invalid DataMapArray element for field: {name}")
                        return bytearray()
                    data_packed = Serializer.serialize(field.meta, data_item, recursion_counter + 1)
                    length = Varint.encode(len(data_packed))
                    buffer.extend(length)
                    buffer.extend(data_packed)
            elif field.type == FieldType.META_DATA and isinstance(value, MetaData):
                print(f"[DEBUG] SERIALIZE META_DATA: field={name}, meta_id={value.meta().id()}")
                meta_data_packed = value.pack(recursion_counter + 1)
                length = Varint.encode(len(meta_data_packed))
                print(f"[DEBUG] SERIALIZE META_DATA: field={name}, len={len(meta_data_packed)}, varint={list(length)}")
                buffer.extend(length)
                buffer.extend(meta_data_packed)
            elif field.type == FieldType.META_DATA_ARRAY and isinstance(value, list):
                count = Varint.encode(len(value))
                print(f"[DEBUG] SERIALIZE META_DATA_ARRAY: field={name}, count={len(value)}, varint={list(count)}")
                buffer.extend(count)
                for meta_data in value:
                    if not isinstance(meta_data, MetaData):
                        print(f"Ошибка: Invalid MetaDataArray element for field: {name}")
                        return bytearray()
                    print(f"[DEBUG] SERIALIZE META_DATA_ARRAY ITEM: field={name}, meta_id={meta_data.meta().id()}")
                    meta_data_packed = meta_data.pack(recursion_counter + 1)
                    length = Varint.encode(len(meta_data_packed))
                    print(f"[DEBUG] SERIALIZE META_DATA_ARRAY ITEM: field={name}, item_len={len(meta_data_packed)}, varint={list(length)}")
                    buffer.extend(length)
                    buffer.extend(meta_data_packed)
            else:
                print(f"Ошибка: Type mismatch for field: {name}")
                return bytearray()
        
        data_size = Varint.encode(len(buffer) - struct.calcsize("<BB"))
        buffer[2:2] = data_size
        return buffer

    @staticmethod
    def serialize_with_crc(meta: Meta, data: Dict[str, Any], crc: Optional[list] = None) -> bytearray:
        """Сериализует данные с CRC16."""
        buffer = Serializer.serialize(meta, data)
        
        if len(buffer) < 2:
            print("Ошибка: Buffer too small")
            return bytearray()
        
        # Устанавливаем флаг HAS_CRC
        buffer[1] = 1  # HAS_CRC = 0x01
        
        # Вычисляем CRC16
        crc16 = CRC16.crc(buffer)
        buffer.extend(struct.pack("<H", crc16))
        if crc is not None:
            crc.append(crc16)
        return buffer

    @staticmethod
    def deserialize(meta: Meta, buffer: bytes, recursion_counter: int = 0, crc: Optional[list] = None) -> Dict[str, Any]:
        """Десериализует данные согласно мета-описанию."""
        if recursion_counter > Meta.MAX_RECURSION_COUNT:
            print("Ошибка: Recursion limit reached")
            return {}
        
        if len(buffer) < struct.calcsize("<BB") + 2:  # header + min_size(size) + min_size(metaId)
            print("Ошибка: Buffer too small")
            return {}

        version, flags = struct.unpack("<BB", buffer[:2])
        if version != meta.VERSION:
            print("Ошибка: Unsupported version")
            return {}

        offset = 2
        data_size, size_bytes = Varint.decode(buffer, offset)
        offset += size_bytes
        data_size += 3

        if data_size > len(buffer):
            print("Ошибка: Invalid data size")
            return {}

        check_crc = bool(flags & 0x01) or (crc is not None)
        if check_crc:
            ref_crc = crc[0] if crc else struct.unpack("<H", buffer[offset + data_size: offset + data_size + 2])[0]
            computed_crc = CRC16.crc(buffer[:offset + data_size])
            if ref_crc != computed_crc:
                print("Ошибка: CRC16 mismatch")
                return {}

        meta_id, decoded_bytes = Varint.decode(buffer, offset)
        offset += decoded_bytes
        if meta.id() != meta_id:
            print(f"Ошибка: Invalid meta ID {meta_id}")
            return {}

        data = {}
        while offset < data_size:
            field_id, decoded_bytes = Varint.decode(buffer, offset)
            offset += decoded_bytes
            field = next((f for f in meta.fields() if f.field_id == field_id), None)
            if not field:
                print(f"Ошибка: Wrong field ID: {field_id}")
                return {}

            if field.type == FieldType.INT8:
                value = struct.unpack("<b", buffer[offset:offset+1])[0]
                offset += 1
                data[field.name] = value
            elif field.type == FieldType.INT16:
                value, decoded_bytes = Varint.decode(buffer, offset)
                offset += decoded_bytes
                data[field.name] = Zigzag.decode_16(value)
            elif field.type == FieldType.INT32:
                value, decoded_bytes = Varint.decode(buffer, offset)
                offset += decoded_bytes
                data[field.name] = Zigzag.decode_32(value)
            elif field.type == FieldType.INT64:
                value, decoded_bytes = Varint.decode(buffer, offset)
                offset += decoded_bytes
                data[field.name] = Zigzag.decode_64(value)
            elif field.type == FieldType.UINT8:
                value = struct.unpack("<B", buffer[offset:offset+1])[0]
                offset += 1
                data[field.name] = value
            elif field.type == FieldType.UINT16:
                value, decoded_bytes = Varint.decode(buffer, offset)
                offset += decoded_bytes
                data[field.name] = value
            elif field.type == FieldType.UINT32:
                value, decoded_bytes = Varint.decode(buffer, offset)
                offset += decoded_bytes
                data[field.name] = value
            elif field.type == FieldType.UINT64:
                value, decoded_bytes = Varint.decode(buffer, offset)
                offset += decoded_bytes
                data[field.name] = value
            elif field.type == FieldType.FLOAT:
                value = struct.unpack("<f", buffer[offset:offset+4])[0]
                offset += 4
                data[field.name] = value
            elif field.type == FieldType.STRING:
                length, decoded_bytes = Varint.decode(buffer, offset)
                offset += decoded_bytes
                value = buffer[offset:offset + length].decode()
                offset += length
                data[field.name] = value
            elif field.type == FieldType.ENUM:
                enum_value = struct.unpack("<B", buffer[offset:offset+1])[0]
                offset += 1
                for key, val in field.enum_mapping.items():
                    if val == enum_value:
                        data[field.name] = EnumType(enum_value)
                        break
                else:
                    print(f"Ошибка: Invalid ENUM value for field: {field.name}")
                    return {}
            elif field.type == FieldType.ARRAY:
                length, decoded_bytes = Varint.decode(buffer, offset)
                offset += decoded_bytes
                value = buffer[offset:offset + length]
                offset += length
                data[field.name] = value
            elif field.type == FieldType.BOOL:
                value = struct.unpack("<B", buffer[offset:offset+1])[0] != 0
                offset += 1
                data[field.name] = value
            elif field.type == FieldType.DATA_MAP:
                length, decoded_bytes = Varint.decode(buffer, offset)
                offset += decoded_bytes
                data_map_buffer = buffer[offset:offset + length]
                offset += length
                if not field.meta:
                    print(f"Ошибка: Meta field must have a meta for field: {field.name}")
                    return {}
                data_map = Serializer.deserialize(field.meta, data_map_buffer, recursion_counter + 1)
                if not data_map:
                    print(f"Ошибка: Failed to deserialize DataMap for field: {field.name}")
                    return {}
                data[field.name] = data_map
            elif field.type == FieldType.DATA_MAP_ARRAY:
                count, decoded_bytes = Varint.decode(buffer, offset)
                offset += decoded_bytes
                data_map_array = []
                for i in range(count):
                    length, decoded_bytes = Varint.decode(buffer, offset)
                    offset += decoded_bytes
                    data_map_buffer = buffer[offset:offset + length]
                    offset += length
                    if not field.meta:
                        print(f"Ошибка: Meta field must have a meta for field: {field.name}")
                        return {}
                    data_map = Serializer.deserialize(field.meta, data_map_buffer, recursion_counter + 1)
                    if not data_map:
                        print(f"Ошибка: Failed to deserialize DataMapArray element for field: {field.name}")
                        return {}
                    data_map_array.append(data_map)
                data[field.name] = data_map_array
            elif field.type == FieldType.META_DATA:
                length, decoded_bytes = Varint.decode(buffer, offset)
                print(f"[DEBUG] DESERIALIZE META_DATA: field={field.name}, offset={offset}, length={length}, decoded_bytes={decoded_bytes}")
                offset += decoded_bytes
                meta_data_buffer = buffer[offset:offset + length]
                print(f"[DEBUG] DESERIALIZE META_DATA: field={field.name}, meta_data_buffer_len={len(meta_data_buffer)}")
                offset += length
                meta_data = MetaData.unpack(meta_data_buffer, recursion_counter + 1)
                if meta_data:
                    print(f"[DEBUG] DESERIALIZE META_DATA: field={field.name}, unpacked meta_id={meta_data.meta().id()}")
                if not meta_data:
                    print(f"Ошибка: Failed to unpack MetaData for field: {field.name}")
                    return {}
                data[field.name] = meta_data
            elif field.type == FieldType.META_DATA_ARRAY:
                count, decoded_bytes = Varint.decode(buffer, offset)
                print(f"[DEBUG] DESERIALIZE META_DATA_ARRAY: field={field.name}, offset={offset}, count={count}, decoded_bytes={decoded_bytes}")
                offset += decoded_bytes
                meta_data_array = []
                for i in range(count):
                    length, decoded_bytes = Varint.decode(buffer, offset)
                    print(f"[DEBUG] DESERIALIZE META_DATA_ARRAY ITEM: field={field.name}, item={i}, offset={offset}, length={length}, decoded_bytes={decoded_bytes}")
                    offset += decoded_bytes
                    meta_data_buffer = buffer[offset:offset + length]
                    print(f"[DEBUG] DESERIALIZE META_DATA_ARRAY ITEM: field={field.name}, item={i}, meta_data_buffer_len={len(meta_data_buffer)}")
                    offset += length
                    meta_data = MetaData.unpack(meta_data_buffer, recursion_counter + 1)
                    if meta_data:
                        print(f"[DEBUG] DESERIALIZE META_DATA_ARRAY ITEM: field={field.name}, item={i}, unpacked meta_id={meta_data.meta().id()}")
                    if not meta_data:
                        print(f"Ошибка: Failed to unpack MetaDataArray element for field: {field.name}")
                        return {}
                    meta_data_array.append(meta_data)
                data[field.name] = meta_data_array
            else:
                print("Ошибка: Unsupported field type")
                return {}

        if not data:
            print(f"Ошибка: deserialize: No data available ({meta.id()})")
        return data

    @staticmethod
    def get_meta_id_from_packet(packet: bytes) -> int:
        """Извлекает ID мета-описания из пакета."""
        if not packet:
            return 0xFFFFFFFF
        header_size = struct.calcsize("<BB")
        if len(packet) < header_size + 1:
            return 0xFFFFFFFF
        data_size, size_bytes = Varint.decode(packet, header_size)
        if header_size + size_bytes >= len(packet):
            return 0xFFFFFFFF
        meta_id, _ = Varint.decode(packet, header_size + size_bytes)
        return meta_id

    @staticmethod
    def get_packet(data: bytes, offset: int = 0) -> bytes:
        """Извлекает один пакет из данных."""
        header_size = struct.calcsize("<BB")
        while offset < len(data):
            if offset + header_size >= len(data):
                offset += 1
                continue
            data_size, size_bytes = Varint.decode(data, offset + header_size)
            total_size = header_size + size_bytes + data_size + (2 if data[offset + 1] & 0x01 else 0)
            if offset + total_size > len(data):
                offset += 1
                continue
            return data[offset:offset + total_size]
        return b""

