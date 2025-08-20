"""
ltcodecs.LzmaCodec
---------------------

This module contains the LzmaCodec class, which is used to encode and decode bytes using LZMA.
"""

from __future__ import annotations
import lzma
from bitstring import ConstBitStream, Bits, BitArray
from .field_codec import FieldCodec
from .exceptions import EncodingFailed
from .varint_codec import VarintCodec


class LzmaCodec(FieldCodec):
    """
    LZMA codec for bytes
    """

    def __init__(self, max_length: int, **kwargs) -> None:
        self.max_length = max_length
        self.length_codec = VarintCodec(min_value=0, max_value=self.max_length)

        self.filter = [
            {"id": lzma.FILTER_DELTA, "dist": 5},
            {"id": lzma.FILTER_LZMA2, "preset": 6 | lzma.PRESET_DEFAULT},
        ]

    def encode(self, value: bytes) -> tuple[Bits, bytes]:
        """
        encode bytes

        :param value: the bytes to encode
        """

        try:
            compressed = lzma.compress(
                value, format=lzma.FORMAT_RAW, filters=self.filter
            )
        except lzma.LZMAError as err:
            raise EncodingFailed("LZMA encoding failed") from err

        if len(compressed) > self.max_length:
            raise EncodingFailed(
                f"LzmaCodec: compressed bytes (length {len(compressed)} are too long to encode (max length {self.max_length})"
            )
        length_bits, _ = self.length_codec.encode(len(compressed))
        value_bits = BitArray(bytes=compressed)
        value_bits.prepend(length_bits)
        return value_bits, value

    def decode(self, bits_to_decode: ConstBitStream) -> bytes:
        """
        decode a bool

        :param bits_to_decode: the bits to decode
        """
        try:
            num_bytes = self.length_codec.decode(bits_to_decode)
            value = lzma.decompress(
                bits_to_decode.read("bytes:" + str(num_bytes)),
                format=lzma.FORMAT_RAW,
                filters=self.filter,
            )
        except lzma.LZMAError as err:
            raise EncodingFailed("LZMA decoding failed") from err

        return value

    @property
    def min_length_bits(self) -> int:
        return self.length_codec.max_length_bits

    @property
    def max_length_bits(self) -> int:
        return self.length_codec.max_length_bits + (8 * self.max_length)
