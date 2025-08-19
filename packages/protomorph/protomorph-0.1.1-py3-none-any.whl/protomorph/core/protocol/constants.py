"""
Общие константы и перечисления протокола
Содержит все повторяющиеся enum'ы и константы из различных модулей
"""

from enum import IntEnum

class Version(IntEnum):
    """Версии протокола"""
    V1 = 1
    V2 = 2
    LastVersion = V2
    Unknown = 255

class MessageCategory(IntEnum):
    """Категории сообщений"""
    Meta = 0
    Data = 1
    Control = 2
    System = 3
    Config = 4
    Ping = 5
    File = 6
    Auth = 7
    Unknown = 255

class AckStatus(IntEnum):
    """Статусы подтверждения"""
    Success = 0
    InvalidData = 1
    CrcError = 2
    NotFound = 3
    InternalError = 4
    InvalidUuid = 5
    Error = 6
    MoreData = 7
    ConfigTooLarge = 8  # Новый статус для больших конфигов
    ChunkRequested = 9  # Новый статус для запроса части
    Unknown = 255

class ConfigType(IntEnum):
    """Типы конфигурационных сообщений"""
    GetConfig = 0
    SetConfig = 1
    ConfigAck = 2
    GetAllConfig = 3
    GetConfigHash = 4
    DeleteConfig = 5
    GetConfigCrc = 6      # Новый тип для получения CRC32
    GetConfigChunk = 7    # Новый тип для получения части

class CommandType(IntEnum):
    """Типы командных сообщений"""
    Command = 0
    CommandResponse = 1

class AuthMessageType(IntEnum):
    """Типы сообщений аутентификации"""
    HashAndData = 0
    MetaAndData = 1
    Ack = 2
    NoMeta = 3

class AuthStatus(IntEnum):
    """Статусы аутентификации"""
    Success = 0
    Error = 1

class FileMessageType(IntEnum):
    """Типы файловых сообщений"""
    ListRequest = 0
    ListResponse = 1
    AttrRequest = 2
    AttrResponse = 3
    ReadRequest = 4
    ReadResponse = 5
    WriteRequest = 6
    WriteResponse = 7
    DeleteRequest = 8
    DeleteResponse = 9

class LogMessageType(IntEnum):
    """Типы сообщений логов"""
    HF = 0
    SO = 1
    WD = 2
    SRSR = 3
    ASSERT = 4
    ERROR = 64
    WARNING = 65

class PingMessageType(IntEnum):
    """Типы Ping сообщений"""
    Ping = 0
    PingAck = 1

class MetaMessageType(IntEnum):
    """Типы Meta сообщений"""
    MetaData = 0
    MetaAck = 1

class DataMessageType(IntEnum):
    """Типы Data сообщений"""
    Data = 0
    DataAck = 1

# Константы для работы с пакетами
MIN_PACKET_SIZE = 9  # Минимальный размер пакета: версия(1) + категория(1) + messageId(2) + тип(1) + payloadLength(2) + CRC(2)
HEADER_SIZE = 7      # Размер заголовка: версия(1) + категория(1) + messageId(2) + тип(1) + payloadLength(2)
CRC_SIZE = 2         # Размер CRC

# Константы для работы с UUID
UUID_SIZE = 16       # Размер UUID в байтах

# Константы для работы с файлами
MAX_FILENAME_SIZE = 255
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB

# Константы для работы с сетью
DEFAULT_TCP_HOST = "localhost"
DEFAULT_TCP_PORT = 8080
DEFAULT_TCP_TIMEOUT = 30
MAX_RECONNECT_ATTEMPTS = 5 