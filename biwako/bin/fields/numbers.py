from .base import Field


# Endianness options

class BigEndian:
    def encode(self, value, size):
        return bytes((value >> (size - i - 1) * 8) & 0xff for i in range(size))

    def decode(self, value, size):
        return sum(v * 0x100 ** (size - i - 1) for i, v in enumerate(value[:size]))


class LittleEndian:
    def encode(self, value, size):
        return bytes((value >> i * 8) & 0xff for i in range(size))

    def decode(self, value, size):
        return sum(v * 0x100 ** i for i, v in enumerate(value[:size]))


# Signed Number Representations

class SignMagnitude:
    def encode(self, value, size):
        if value > (1 << (size * 8)) - 1:
            raise ValueError("Value is too large to encode.")
        if value < 0:
            # Set the sign to negative
            return -value | (1 << (size * 8 - 1))
        return value

    def decode(self, value, size):
        if value >> (size * 8 - 1):
            # The sign is negative
            return -(value ^ (2 ** (size * 8 - 1)))
        return value


class OnesComplement:
    def encode(self, value, size):
        if value > (1 << (size * 8)) - 1:
            raise ValueError("Value is too large to encode.")
        if value < 0:
            # Value is negative
            return ~(-value) & (2 ** (size * 8) - 1)
        return value

    def decode(self, value, size):
        if value >> (size * 8 - 1):
            # Value is negative
            return -(~value & (2 ** (size * 8) - 1))
        return value


class TwosComplement:
    def encode(self, value, size):
        if value > (1 << (size * 8 - 1)) - 1:
            raise ValueError("Value is too large to encode.")
        if value < 0:
            # Value is negative
            return (~(-value) & (2 ** (size * 8) - 1)) + 1
        return value

    def decode(self, value, size):
        if value > 2 ** (size * 8 - 1) - 1:
            # Value is negative
            return -(~value & (2 ** (size * 8) - 1)) - 1
        return value


# Numeric types

class Integer(Field):
    def __init__(self, *args, signed=True, endianness=BigEndian(),
                 signing=TwosComplement(), **kwargs):
        self.endianness = endianness
        self.signed = signed
        self.signing = signing
        super(Integer, self).__init__(*args, **kwargs)

    def encode(self, value):
        if self.signed:
            value = self.signing.encode(value, self.size)
        elif value < 0:
            raise ValueError("Value cannot be negative.")
        if value > (1 << (self.size * 8)) - 1:
            raise ValueError("Value is large for this field.")
        return self.endianness.encode(value, self.size)

    def decode(self, value):
        value = self.endianness.decode(value, self.size)
        if self.signed:
            value = self.signing.decode(value, self.size)
        return value


class PositiveInteger(Integer):
    def __init__(self, *args, signed=False, **kwargs):
        super(PositiveInteger, self).__init__(*args, signed=signed, **kwargs)


class Byte(Integer):
    def __init__(self, *args, size=1, **kwargs):
        super(Byte, self).__init__(*args, size=size, **kwargs)


