"""
ltcodecs.linspace_float_codec
-----------------------------

This module contains the the linspace float codec
"""

from __future__ import annotations
from math import ceil, log2
from bitstring import ConstBitStream, Bits

from .field_codec import FieldCodec


class LinspaceFloatCodec(FieldCodec):
    """
    LinspaceFloatCodec
    """

    def __init__(
        self,
        min_value: float,
        max_value: float,
        resolution: float = None,
        num_values: int = None,
        num_bits: int = None,
        **kwargs,
    ):
        self.max_value = float(max_value)
        self.min_value = float(min_value)
        self.value_range = max_value - min_value
        if num_values or num_bits:
            if resolution:
                raise ValueError(
                    "LinspaceFloatCodec supports setting only one of num_values, num_bits, or resolution."
                )
            if num_bits:
                if num_values:
                    raise ValueError(
                        "LinspaceFloatCodec supports setting either num_values or num_bits, not both."
                    )
                if num_bits < 1:
                    raise ValueError(
                        f"LinspaceFloatCodec requires at least 1 bit (num_bits >= 1), you specified num_bits={num_bits}"
                    )
                num_values = 2**num_bits
            if num_values < 2:
                raise ValueError(
                    f"LinspaceFloatCodec requires at least 2 values (num_values >= 2), you specified num_values={num_values}"
                )
            resolution = self.value_range / (num_values - 1)

        self.resolution = float(resolution)

        self.num_values = self.value_range // self.resolution + 1
        # if the max value isn't an integer multiple of the resolution from the min value, it won't be encoded.
        self.num_bits = ceil(log2(self.num_values))

    def encode(self, value: float) -> tuple[Bits, float]:
        """
        encode value

        :param value: the value to encode
        """
        value = float(value)
        if value < self.min_value:
            value = self.min_value
        elif value > self.max_value:
            value = self.max_value
        offset = value - self.min_value
        discretized_offset = int(offset // self.resolution)
        encoded_value = self.min_value + (discretized_offset * self.resolution)
        encoded_bits = Bits(uint=discretized_offset, length=self.num_bits)
        return encoded_bits, encoded_value

    def decode(self, bits_to_decode: ConstBitStream) -> float:
        """
        decode bits_to_decode into a value
        """
        discretized_offset = bits_to_decode.read(f"uint:{self.num_bits}")
        value = self.min_value + (discretized_offset * self.resolution)
        return value

    @property
    def max_length_bits(self) -> int:
        return self.num_bits

    @property
    def min_length_bits(self) -> int:
        return self.num_bits
