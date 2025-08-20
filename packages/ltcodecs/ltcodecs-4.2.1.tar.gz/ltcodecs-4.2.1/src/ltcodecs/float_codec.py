"""
ltcodecs.float_codec
-----------------------------

This module contains the the float codec
"""

from __future__ import annotations
from bitstring import ConstBitStream, Bits
from .field_codec import FieldCodec
from math import ceil, log2


class FloatCodec(FieldCodec):
    """
    codec for floating point numbers
    """

    def __init__(
        self, min_value: float, max_value: float, precision: int, **kwargs
    ) -> None:
        self.max_value = float(max_value)
        self.min_value = float(min_value)
        self.precision = int(precision)

        self.value_range = int(
            round(max_value - min_value, precision) * 10**precision
        )
        self.num_bits = ceil(log2(self.value_range))

    def encode(self, value: float) -> tuple[Bits, float]:
        """
        encode a float

        :param value: the value to encode
        """
        value = float(value)
        if value < self.min_value:
            value = self.min_value
        elif value > self.max_value:
            value = self.max_value

        encoded_value = int(
            round(value - self.min_value, self.precision) * 10**self.precision
        )
        # print(value, self.min_value, self.precision)
        rounded_value = (
            round(value - self.min_value, self.precision) + self.min_value
        )  # Used only for validation
        encoded_bits = Bits(uint=encoded_value, length=self.num_bits)

        return encoded_bits, rounded_value

    def decode(self, bits_to_decode: ConstBitStream) -> float:
        """
        decode a float

        :param bits_to_decode: the bitstream to decode
        """

        float_offset = (
            bits_to_decode.read(f"uint:{self.num_bits}") / 10**self.precision
        )
        value = self.min_value + float_offset
        return value

    @property
    def max_length_bits(self) -> int:
        return self.num_bits

    @property
    def min_length_bits(self) -> int:
        return self.num_bits
