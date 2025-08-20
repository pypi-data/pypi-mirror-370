"""
variable_len_array_codec.py
---------------------------

module for VariableLenArrayCodec
"""

from __future__ import annotations
from typing import Any
from bitstring import BitArray, ConstBitStream
from .field_codec import FieldCodec
from .varint_codec import VarintCodec
import ltcodecs as ltcodecs
from .exceptions import EncodingFailed


class VariableLenArrayCodec(FieldCodec):
    """
    codec for variable-length array

    Args:
        element_type: codec to use to encode each element of the array
        max_length: maximum number of elements to encode
        element_params: Codec parameters dictionary to use for the element codec
        nullable: If this is True, use a bit to indicate if the array is empty.  This allows encoding an empty array
            with a single bit.
    """

    def __init__(
        self, element_type: str, max_length: int, element_params=None, nullable=False, **kwargs
    ) -> None:
        self.max_length = max_length
        self.nullable = nullable
        if not self.nullable:
            self.length_codec = VarintCodec(min_value=0, max_value=self.max_length)
        else:
            # If we are nullable, we don't need to encode length 0, since it is handled by the nullable flag
            self.length_codec = VarintCodec(min_value=1, max_value=self.max_length)
        print("element_type", element_type)
        if element_params:
            self.element_field_codec = ltcodecs.field_codec_classes[element_type](
                **element_params
            )
        else:
            self.element_field_codec = ltcodecs.field_codec_classes[element_type]()

    def encode(self, value: list) -> tuple[BitArray, list[Any]]:
        """
        encodes list of elements
        """
        value_bits = BitArray()
        encoded_value_list = []

        if self.nullable:
            value_bits.append(BitArray(bool=(len(value) > 0)))

        if len(value) > 0 or not self.nullable:
            value = value[0 : self.max_length]
            length_bits, _ = self.length_codec.encode(len(value))
            value_bits.append(length_bits)
            for element in value:
                (
                    element_bits,
                    element_value,
                ) = self.element_field_codec.encode(element)

                value_bits.append(element_bits)
                encoded_value_list.append(element_value)
        return value_bits, encoded_value_list

    def decode(self, bits_to_decode: ConstBitStream) -> list:
        """
        decodes list of elements from bits
        """
        not_null = True
        if self.nullable:
            not_null = bits_to_decode.read('bool')

        decoded_list = []
        if not_null:
            num_elements = self.length_codec.decode(bits_to_decode)
            for i in range(num_elements):
                element = self.element_field_codec.decode(bits_to_decode)
                decoded_list.append(element)
        return decoded_list

    @property
    def min_length_bits(self) -> int:
        if self.nullable:
            return 1
        else:
            return self.length_codec.max_length_bits

    @property
    def max_length_bits(self) -> int:
        length_bits = self.length_codec.max_length_bits + (
            self.max_length * self.element_field_codec.max_length_bits
        )
        if self.nullable:
            length_bits += 1
        return length_bits
