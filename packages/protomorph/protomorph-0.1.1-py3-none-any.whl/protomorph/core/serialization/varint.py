"""
Varint кодирование
Содержит класс для кодирования/декодирования переменной длины целых чисел
"""

class Varint:
    @staticmethod
    def encode(num: int) -> bytearray:
        """
        Кодирует число uint32 в формат varint.
        Возвращает bytearray с закодированными байтами.
        """
        encoded = bytearray()
        while num > 0x7F:  # Пока остаются биты, которые не влезают в 7 бит
            encoded.append((num & 0x7F) | 0x80)  # Устанавливаем старший бит в 1
            num >>= 7  # Сдвигаем число на 7 бит вправо
        encoded.append(num & 0x7F)  # Последний байт (старший бит = 0)
        return encoded

    @staticmethod
    def decode(data: bytes, start: int = 0) -> tuple[int, int]:
        """
        Декодирует varint из массива байтов, начиная с позиции start.
        Возвращает кортеж (декодированное число, количество прочитанных байтов).
        """
        num = 0
        shift = 0
        bytes_read = 0

        for i in range(start, len(data)):
            byte = data[i]
            bytes_read += 1
            num |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:  # Если старший бит 0, конец
                break
            shift += 7

        return num, bytes_read 