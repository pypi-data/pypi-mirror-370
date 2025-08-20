"""
ltcodecs.bool_codec
---------------------

This module contains the BoolCodec class, which is used to encode and decode bools.
"""

from __future__ import annotations
from bitstring import BitArray, ConstBitStream, Bits
from .field_codec import FieldCodec


class BoolCodec(FieldCodec):
    """
    codec for bools
    """

    def __init__(self, **kwargs) -> None:
        pass

    def encode(self, value: bool) -> tuple[Bits, bool]:
        """
        encode a bool

        :param value: the bool to encode
        """
        value = bool(value)
        value_bits = BitArray(bool=value)
        return value_bits, value

    def decode(self, bits_to_decode: ConstBitStream) -> bool:
        """
        decode a bool

        :param bits_to_decode: the bits to decode
        """

        value = bits_to_decode.read("bool")
        return value

    @property
    def min_length_bits(self) -> int:
        return 1

    @property
    def max_length_bits(self) -> int:
        return 1
