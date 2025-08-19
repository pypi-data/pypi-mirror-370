"""
Базовые тесты для библиотеки Protomorph
"""

import pytest
from protomorph import (
    Meta, Serializer, ConfigPacket, ConfigType, AckStatus, 
    FieldType, Version, MessageCategory
)

def test_meta_creation():
    """Тест создания метаданных"""
    meta = Meta("TestConfig")
    meta.add_field("name", FieldType.STRING)
    meta.add_field("value", FieldType.INT32)
    
    assert meta.name() == "TestConfig"
    assert len(meta.fields()) == 2
    assert meta.fields()[0].name == "name"
    assert meta.fields()[0].type == FieldType.STRING
    assert meta.fields()[1].name == "value"
    assert meta.fields()[1].type == FieldType.INT32

def test_serialization():
    """Тест сериализации и десериализации"""
    meta = Meta("TestConfig")
    meta.add_field("name", FieldType.STRING)
    meta.add_field("value", FieldType.INT32)
    
    data = {"name": "test", "value": 42}
    
    # Сериализация
    binary_data = Serializer.serialize(meta, data)
    assert len(binary_data) > 0
    
    # Десериализация
    deserialized_data = Serializer.deserialize(meta, binary_data)
    assert deserialized_data["name"] == "test"
    assert deserialized_data["value"] == 42

def test_config_packet():
    """Тест создания конфигурационного пакета"""
    packet = ConfigPacket(
        type_val=ConfigType.GetConfig,
        request_type=ConfigType.GetConfig,
        uuid=b'\x00' * 16,
        instance=0
    )
    
    assert packet.version == Version.LastVersion
    assert packet.category == MessageCategory.Config
    assert packet.type == ConfigType.GetConfig
    
    # Упаковка пакета
    packet_bytes = packet.pack()
    assert len(packet_bytes) > 0
    
    # Распаковка пакета
    unpacked_packet = ConfigPacket.unpack(packet_bytes)
    assert unpacked_packet.type == ConfigType.GetConfig
    assert unpacked_packet.request_type == ConfigType.GetConfig
    assert unpacked_packet.instance == 0

def test_meta_pack_unpack():
    """Тест упаковки и распаковки метаданных"""
    meta = Meta("TestConfig")
    meta.add_field("name", FieldType.STRING)
    meta.add_field("value", FieldType.INT32)
    
    # Упаковка
    packed_meta = meta.pack()
    assert len(packed_meta) > 0
    
    # Распаковка
    unpacked_meta = Meta.unpack(packed_meta)
    assert unpacked_meta is not None
    assert unpacked_meta.name() == "TestConfig"
    assert len(unpacked_meta.fields()) == 2

if __name__ == "__main__":
    pytest.main([__file__]) 