"""
ltcodecs.bytes_codec
---------------------

This module contains the BytesCodec class, which is used to encode and decode bytes.
"""

from __future__ import annotations
from bitstring import BitArray, ConstBitStream, Bits
from .field_codec import FieldCodec
from .varint_codec import VarintCodec
from .exceptions import EncodingFailed


class BytesCodec(FieldCodec):
    """
    codec for bytes
    """

    def __init__(self, max_length: int, fail_on_overflow=False, **kwargs) -> None:
        self.max_length = max_length
        self.length_codec = VarintCodec(min_value=0, max_value=self.max_length)
        self.fail_on_overflow = fail_on_overflow

    def encode(self, value: bytes) -> tuple[Bits, bytes]:
        """
        encode bytes

        :param value: the bytes to encode
        """
        if self.fail_on_overflow and len(value) > self.max_length:
            raise EncodingFailed(
                f"BytesCodec: value with length {len(value)} is too long to encode (codec max_length={self.max_length}"
            )
        value = value[0 : self.max_length]
        length_bits, _ = self.length_codec.encode(len(value))
        value_bits = BitArray(bytes=value)
        value_bits.prepend(length_bits)
        return value_bits, value

    def decode(self, bits_to_decode: ConstBitStream) -> bytes:
        """
        decode bytes

        :param bits_to_decode: the bits to decode
        """
        num_bytes = self.length_codec.decode(bits_to_decode)
        value = bits_to_decode.read("bytes:" + str(num_bytes))
        return value

    @property
    def min_length_bits(self) -> int:
        return self.length_codec.max_length_bits

    @property
    def max_length_bits(self) -> int:
        return self.length_codec.max_length_bits + (8 * self.max_length)
