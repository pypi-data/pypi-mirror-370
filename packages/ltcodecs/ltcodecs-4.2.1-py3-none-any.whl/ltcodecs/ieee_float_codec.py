"""
ltcodecs.ieee_float_codec
-------------------------

ieee_float_codec encodes and decodes IEEE floating point numbers
"""

from __future__ import annotations
from bitstring import ConstBitStream, Bits
from .field_codec import FieldCodec


class IeeeFloatCodec(FieldCodec):
    """
    codec for IEEE floating point numbers
    """

    def __init__(self, num_bits=32, **kwargs):
        if num_bits not in (32, 64):
            raise ValueError(
                "Only 32 or 64 bit widths are supported for IEEE floating point codecs"
            )
        self.num_bits = num_bits

    def encode(self, value: float) -> tuple[Bits, float]:
        """
        encode value

        :param value: the value to encode
        """

        value = float(value)
        encoded_bits = Bits(float=value, length=self.num_bits)
        encoded_value = encoded_bits.float
        return encoded_bits, encoded_value

    def decode(self, bits_to_decode: ConstBitStream):
        """
        decode value

        :param bits_to_decode: the bitstream to decode
        """

        value = bits_to_decode.read(f"floatbe:{self.num_bits}")
        return value

    @property
    def max_length_bits(self):
        return self.num_bits

    @property
    def min_length_bits(self):
        return self.num_bits


class IeeeFloat32Codec(IeeeFloatCodec):
    """
    metaclass for IEEE 32 bit floating point numbers
    """

    def __init__(self, **kwargs):
        super(IeeeFloat32Codec, self).__init__(num_bits=32)


class IeeeFloat64Codec(IeeeFloatCodec):
    """
    metaclass for IEEE 64 bit floating point numbers
    """

    def __init__(self, **kwargs):
        super(IeeeFloat64Codec, self).__init__(num_bits=64)
