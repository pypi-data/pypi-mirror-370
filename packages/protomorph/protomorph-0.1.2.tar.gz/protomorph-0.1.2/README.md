# Protomorph Python Library

Библиотека для работы с протоколом Protomorph на Python.

## Описание

Protomorph - это библиотека для сериализации/десериализации данных, работы с сетевыми пакетами и высокоуровневыми моделями данных в рамках протокола Protomorph.

## Установка

```bash
pip install protomorph
```

Для разработки:
```bash
pip install protomorph[dev]
```

Для веб-интерфейса:
```bash
pip install protomorph[web]
```

## Структура библиотеки

```
protomorph/
├── core/                    # Базовые компоненты
│   ├── protocol/           # Константы и типы протокола
│   ├── serialization/      # Сериализация/десериализация
│   └── utils/              # Утилиты (CRC, хеши)
├── packets/                # Сетевые пакеты
│   ├── base/               # Базовые классы пакетов
│   └── messages/           # Конкретные типы пакетов
├── models/                 # Высокоуровневые модели
│   ├── config/             # Модели конфигураций
│   └── converters/         # Конвертеры форматов
└── transport/              # Транспортный уровень
    └── nats/               # NATS клиент
```

## Быстрый старт

### Работа с метаданными

```python
from protomorph import Meta, Serializer

# Создание метаданных
meta = Meta("MyConfig")
meta.add_field("name", FieldType.STRING)
meta.add_field("value", FieldType.INT32)

# Данные
data = {"name": "test", "value": 42}

# Сериализация
binary_data = Serializer.serialize(meta, data)

# Десериализация
deserialized_data = Serializer.deserialize(meta, binary_data)
```

### Работа с конфигурационными пакетами

```python
from protomorph import ConfigPacket, ConfigType, AckStatus

# Создание пакета запроса
request = ConfigPacket(
    type_val=ConfigType.GetConfig,
    request_type=ConfigType.GetConfig,
    uuid=b'\x00' * 16,
    instance=0
)

# Упаковка пакета
packet_bytes = request.pack()

# Распаковка ответа
response = ConfigPacket.unpack(response_bytes)
```

## Основные компоненты

### Core

- **Meta**: Класс для работы с метаданными
- **Serializer**: Сериализация/десериализация данных
- **FieldType**: Типы полей данных
- **CRC16/CRC32**: Вычисление контрольных сумм

### Packets

- **ConfigPacket**: Пакеты конфигураций
- **AuthMessage**: Пакеты аутентификации
- **CommandPacket**: Командные пакеты

### Models

- **Config**: Высокоуровневая модель конфигурации
- **meta_to_json/data_to_json**: Конвертеры в JSON

## Примеры использования

### Device-Comm сервис

```python
import asyncio
from protomorph import ConfigPacket, ConfigType, Meta, Serializer

async def handle_config_request(msg):
    # Парсим запрос
    request = ConfigPacket.unpack(msg.data)
    
    if request.type == ConfigType.GetConfig:
        # Получаем конфигурацию
        config_data = await fetch_config_from_api(request.uuid)
        
        # Создаем ответ
        meta = Meta.unpack(config_data)
        data = Serializer.deserialize(meta, config_data[len(meta.pack()):])
        
        # Отправляем ответ
        response = ConfigPacket(
            type_val=ConfigType.ConfigAck,
            request_type=ConfigType.GetConfig,
            uuid=request.uuid,
            instance=request.instance,
            status=AckStatus.Success,
            payload=config_data
        )
        
        await msg.respond(response.pack())
```

### API сервис

```python
from protomorph import Config, Meta

# Создание конфигурации из JSON
config = Config.from_dict(json_data)

# Вычисление хеша
config_hash = config.calculate_hash()

# Сериализация в бинарный формат
binary_data = config.serialize()

# Сохранение в объектное хранилище
await object_storage.save(config_hash, binary_data)
```

## Разработка

### Установка для разработки

```bash
git clone https://github.com/protomorph/protomorph-python.git
cd protomorph-python
pip install -e .[dev]
```

### Запуск тестов

```bash
pytest
```

### Форматирование кода

```bash
black .
flake8 .
mypy .
```

## Лицензия

MIT License

## Поддержка

- Документация: https://protomorph.readthedocs.io/
- Issues: https://github.com/protomorph/protomorph-python/issues
- Discussions: https://github.com/protomorph/protomorph-python/discussions 