"""
ltcodecs.fixed_len_array_codec
------------------------------

This module contains the FixedLenArrayCodec class, which is used to encode and decode fixed length arrays.
"""

from __future__ import annotations
from bitstring import BitArray, ConstBitStream, Bits
from .field_codec import FieldCodec
import ltcodecs as ltcodecs
from typing import List
from .exceptions import EncodingFailed


class FixedLenArrayCodec(FieldCodec):
    """
    codec for fixed length arrays
    """

    def __init__(
        self, element_type: str, length: int, element_params=None, **kwargs
    ) -> None:
        self.length = length
        if element_params:
            self.element_field_codec = ltcodecs.field_codec_classes[element_type](
                **element_params
            )
        else:
            self.element_field_codec = ltcodecs.field_codec_classes[element_type]()

    def encode(self, value: List) -> tuple[Bits, List]:
        """
        encode a fixed length array

        :param value: the fixed length array to encode
        """
        value = value[0 : self.length]
        value_bits = BitArray()
        encoded_value_list = []
        for element in value:
            (
                element_bits,
                element_value,
            ) = self.element_field_codec.encode(element)

            value_bits.append(element_bits)
            encoded_value_list.append(element_value)
        return value_bits, encoded_value_list

    def decode(self, bits_to_decode: ConstBitStream) -> List:
        """
        decode a fixed length array

        :param bits_to_decode: the bits to decode
        """

        decoded_list = []
        for i in range(self.length):
            element = self.element_field_codec.decode(bits_to_decode)
            decoded_list.append(element)
        return decoded_list

    @property
    def min_length_bits(self) -> int:
        return self.length * self.element_field_codec.max_length_bits

    @property
    def max_length_bits(self) -> int:
        return self.length * self.element_field_codec.max_length_bits
