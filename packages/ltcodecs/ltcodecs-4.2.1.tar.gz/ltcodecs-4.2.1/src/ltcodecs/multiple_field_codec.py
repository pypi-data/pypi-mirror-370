"""
abstract base class for codecs that encode multiple fields
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from bitstring import ConstBitStream, Bits
from typing import Any


class MultipleFieldCodec(ABC):
    """
    abstract base class for field codecs
    """

    def __init__(self, **kwargs) -> None:
        pass

    @abstractmethod
    def encode_multiple(self, value: Any, message_dict: dict) -> tuple[Bits, bool, dict]:
        """
        encodes multiple fields

        :param value: the "primary" value to encode
        :param message_dict: the full message from which the additional fields to encode may be read
        """
        pass

    @abstractmethod
    def decode_multiple(self, bits_to_decode: ConstBitStream) -> tuple[Any, dict]:
        """
        decodes multiple values

        Args:
            bits_to_decode: ConstBitStream to decode

        Returns:
            value: the value of the "primary" decoded field
            values_dict: Dictionary with other decoded field name: value pairs
        """
        pass

    @property
    @abstractmethod
    def max_length_bits(self) -> int:
        pass

    @property
    @abstractmethod
    def min_length_bits(self) -> int:
        pass
