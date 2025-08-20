"""
ltcodecs.string_enum_codec
--------------------------

This module contains the StringEnumCodec class, which is used to encode and decode string enums.
"""
from __future__ import annotations
from bitstring import ConstBitStream
from .varint_codec import VarintCodec
from .field_codec import FieldCodec
from typing import List, Optional
from .exceptions import EncodingFailed


class StringEnumCodec(FieldCodec):
    """
    codec for string enums
    """

    def __init__(
        self,
        entries: List[str],
        unknown_value: Optional[str] = None,
        case_sensitive: bool = False,
        strip: bool = False,
        **kwargs,
    ) -> None:
        if case_sensitive:
            self.entries = entries
        else:
            self.entries = [e.lower() for e in entries]
        self.case_sensitive = case_sensitive
        self.strip = strip

        if isinstance(unknown_value, str):
            self.unknown_value = unknown_value
            min_value = -1
        else:
            self.unknown_value = None
            min_value = 0

        self.string_index_codec = VarintCodec(
            min_value=min_value, max_value=len(self.entries)
        )

    def encode(self, value: str) -> tuple[ConstBitStream, str]:
        """
        encode a string enum

        :param value: the string to encode
        """

        if not self.case_sensitive:
            value = value.lower()
        if self.strip:
            value = value.strip()

        if value in self.entries:
            index = self.entries.index(value)
            compressed_value = self.entries[index]
        else:
            if self.unknown_value:
                index = -1
                compressed_value = self.unknown_value
            else:
                index = 0
                compressed_value = self.entries[index]
                raise EncodingFailed(
                    f"Failed to encode unknown string {value}, not in {self.entries}"
                )

        encoded_index, _ = self.string_index_codec.encode(index)

        return encoded_index, compressed_value

    def decode(self, encoded_bits: ConstBitStream) -> str:
        """
        decode a string enum from a bitstream

        :param encoded_bits: the bitstream to decode
        """

        index = self.string_index_codec.decode(encoded_bits)
        if index < 0:
            return self.unknown_value
        else:
            return self.entries[index]

    @property
    def max_length_bits(self) -> int:
        return self.string_index_codec.max_length_bits

    @property
    def min_length_bits(self) -> int:
        return self.string_index_codec.max_length_bits
