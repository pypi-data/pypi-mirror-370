"""
abstract base class for field codecs
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from bitstring import ConstBitStream, Bits
from typing import Any


class FieldCodec(ABC):
    """
    abstract base class for field codecs
    """

    def __init__(self, **kwargs) -> None:
        pass

    @abstractmethod
    def encode(self, value: Any) -> tuple[Bits, Any]:
        """
        encodes value

        :param value: value to encode
        """
        pass

    @abstractmethod
    def decode(self, bits_to_decode: ConstBitStream) -> Any:
        """
        decodes value

        :param bits_to_decode: ConstBitStream to decode
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
