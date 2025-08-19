"""
Zigzag кодирование
Содержит класс для кодирования/декодирования знаковых целых чисел
"""

class Zigzag:
    @staticmethod
    def encode_32(x: int) -> int:
        """
        Кодирует 32-битное знаковое целое число в Zigzag-формат.
        Возвращает 32-битное беззнаковое целое число.
        """
        return ((x << 1) ^ (x >> 31)) & 0xFFFFFFFF

    @staticmethod
    def decode_32(n: int) -> int:
        """
        Декодирует 32-битное беззнаковое целое число из Zigzag-формата.
        Возвращает 32-битное знаковое целое число.
        """
        result = (n >> 1) ^ (-(n & 1))
        if result & 0x80000000:  # Если установлен старший бит
            result |= ~0xFFFFFFFF  # Устанавливаем все старшие биты
        return result

    @staticmethod
    def encode_16(value: int) -> int:
        """
        Кодирует 16-битное знаковое целое число в Zigzag-формат.
        Возвращает 16-битное беззнаковое целое число.
        """
        return ((value << 1) ^ (value >> 15)) & 0xFFFF

    @staticmethod
    def decode_16(value: int) -> int:
        """
        Декодирует 16-битное беззнаковое целое число из Zigzag-формата.
        Возвращает 16-битное знаковое целое число.
        """
        result = (value >> 1) ^ (-(value & 1))
        # Ограничиваем диапазон до int16
        result = (result + 2**15) % 2**16 - 2**15
        return result

    @staticmethod
    def encode_64(x: int) -> int:
        """
        Кодирует 64-битное знаковое целое число в Zigzag-формат.
        Возвращает 64-битное беззнаковое целое число.
        """
        return ((x << 1) ^ (x >> 63)) & 0xFFFFFFFFFFFFFFFF

    @staticmethod
    def decode_64(n: int) -> int:
        """
        Декодирует 64-битное беззнаковое целое число из Zigzag-формата.
        Возвращает 64-битное знаковое целое число.
        """
        result = (n >> 1) ^ (-(n & 1))
        # Ограничиваем диапазон до int64
        result = (result + 2**63) % 2**64 - 2**63
        return result

    # Алиасы для обратной совместимости
    @staticmethod
    def encode(x: int) -> int:
        """Кодирует 32-битное значение (для обратной совместимости)."""
        return Zigzag.encode_32(x)

    @staticmethod
    def decode(n: int) -> int:
        """Декодирует 32-битное значение (для обратной совместимости)."""
        return Zigzag.decode_32(n) 