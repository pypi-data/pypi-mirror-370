"""
ltcodecs.padding_codec
----------------------

padding_codec encodes and decodes padding 
"""

from __future__ import annotations
from bitstring import BitArray, ConstBitStream
from .field_codec import FieldCodec


class PaddingCodec(FieldCodec):
    """
    padding codec
    """

    def __init__(self, num_bits, **kwargs) -> None:
        self.num_bits = int(num_bits)
        pass

    def encode(self, value=None) -> tuple[BitArray, None]:
        """
        encode padding

        :param value: the value to encode
        """
        value_bits = BitArray(uint=0, length=self.num_bits)
        return value_bits, None

    def decode(self, bits_to_decode: ConstBitStream) -> None:
        """
        decode padding

        :param bits_to_decode: the bitstream to decode
        """
        bits_to_decode.read(f"pad:{self.num_bits}")
        return None

    def min_length_bits(self) -> int:
        return self.num_bits

    def max_length_bits(self) -> int:
        return self.num_bits
