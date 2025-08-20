"""
ltcodecs.ccl_latlon_codec
-------------------------

ccl_latlon_codec encodes and decodes CCL latitude and longitude values
"""

from __future__ import annotations
from bitstring import ConstBitStream, Bits
from .field_codec import FieldCodec
from math import ceil, log2


class CclLatLonCodec(FieldCodec):
    """
    codec for CCL latitude and longitude values
    """

    def __init__(self, **kwargs) -> None:
        pass

    def encode(self, value: float) -> tuple[Bits, float]:
        """
        encode value

        :param value: the value to encode
        """

        encoded_value = int(value * ((2**23 - 1) / 180.0))
        encoded_bits = Bits(intle=encoded_value, length=24)

        return encoded_bits, encoded_value

    def decode(self, bits_to_decode: ConstBitStream) -> float:
        """
        decode value

        :param bits_to_decode: the bitstream to decode
        """

        scale = bits_to_decode.read("intle:24")
        value = scale * (180.0 / (2**23 - 1))
        return value

    @property
    def max_length_bits(self) -> int:
        return 24

    @property
    def min_length_bits(self) -> int:
        return 24
