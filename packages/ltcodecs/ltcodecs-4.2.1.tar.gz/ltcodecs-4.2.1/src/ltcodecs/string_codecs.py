"""
ltcodecs.string_codecs
----------------------

This module contains codecs for encoding and decoding strings.
"""

from __future__ import annotations
from bitstring import BitArray, Bits, ConstBitStream
from .varint_codec import VarintCodec
from .field_codec import FieldCodec


def to_sixbit_ascii(character: str) -> int:
    """
    return the sixbit code corresponding to the ascii character

    :param character: the character to convert
    """
    upper_character = character.upper()
    ascii_code = int(upper_character.encode("ascii")[0])

    if ascii_code >= 0x40 and ascii_code <= 0x5F:
        sixbit_code = ascii_code - 0x40
    elif ascii_code >= 0x20 and ascii_code <= 0x3F:
        sixbit_code = ascii_code
    else:
        sixbit_code = 0x3F  # out of bounds values are encoded as '?'

    return sixbit_code


def from_sixbit_ascii(sixbit_code: int) -> str:
    """
    return the ascii character corresponding to the sixbit code

    :param sixbit_code: the sixbit code to convert
    """
    ascii_code = sixbit_code + 0x40 if sixbit_code <= 0x1F else sixbit_code

    return bytes([ascii_code]).decode("ascii")


class AsciiStringCodec(FieldCodec):
    """
    codec for encoding and decoding ascii strings
    """

    def __init__(
        self, max_length: int = 128, bits_per_char: int = 7, tail=False, **kwargs
    ) -> None:
        self.max_length = int(max_length)
        self.bits_per_char = bits_per_char
        self.tail = tail
        self.string_len_codec = VarintCodec(min_value=0, max_value=max_length)

    def encode(self, value: str) -> tuple[Bits, str]:
        """
        encode a string into a bitstream

        :param value: the string to encode
        """
        if not self.tail:
            value = value[0 : self.max_length]
        else:
            value = value[-self.max_length :]
        length_bits, _ = self.string_len_codec.encode(len(value))
        encoded_bits = BitArray()
        encoded_bits.append(length_bits)

        string_bytes = value.encode("ascii")
        if self.bits_per_char == 7:
            compressed_bytes = bytearray()
            for sb in string_bytes:
                if sb > 0x7F:
                    # Replace out of bounds values with "?"
                    sb = 0x3F
                compressed_bytes.append(sb)
                encoded_bits.append(Bits(bytes=[sb], length=7, offset=1))
        elif self.bits_per_char == 6:
            compressed_bytes = bytearray()
            for sb in string_bytes:
                sixbit_value = to_sixbit_ascii(sb)
                compressed_byte = from_sixbit_ascii(sixbit_value).encode("ascii")
                compressed_bytes.extend(compressed_byte)
                encoded_bits.append(Bits(bytes=[sixbit_value], length=6, offset=2))
        else:
            encoded_bits.append(Bits(bytes=value))
            compressed_bytes = string_bytes

        compressed_string = compressed_bytes.decode("ascii")
        return encoded_bits, compressed_string

    def decode(self, encoded_bits: ConstBitStream) -> str:
        """
        decode a string from a bitstream

        :param encoded_bits: the bitstream to decode
        """
        num_chars = self.string_len_codec.decode(encoded_bits)
        if self.bits_per_char == 7:
            string_bytes = bytearray()
            for i in range(num_chars):
                char_byte = encoded_bits.read("uint:7").to_bytes(1, "big")[0]
                string_bytes.append(char_byte)
        elif self.bits_per_char == 6:
            new_string = ""
            for i in range(num_chars):
                sixbit_code = encoded_bits.read("uint:6").to_bytes(1, "big")[0]
                new_string += from_sixbit_ascii(sixbit_code)
            return new_string
        else:
            string_bytes = encoded_bits.read(f"bytes:{num_chars}")
        return string_bytes.decode("ascii")

    @property
    def max_length_bits(self) -> int:
        return self.string_len_codec.max_length_bits + (
            self.max_length * self.bits_per_char
        )

    @property
    def min_length_bits(self) -> int:
        return self.string_len_codec.max_length_bits
