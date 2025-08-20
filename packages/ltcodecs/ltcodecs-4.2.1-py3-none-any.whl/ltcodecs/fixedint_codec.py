"""
ltcodecs.fixedint_codec
-----------------------

This module contains classes for fixed width integer codecs
"""

from .varint_codec import VarintCodec


class FixedIntCodec(VarintCodec):
    """
    FixedIntCodec base class
    """

    def __init__(
        self,
        num_bits: int,
        signed: bool = False,
        min_value: int = None,
        resolution: int = 1,
        little_endian: bool = False,
        **kwargs
    ):
        self.num_bits = num_bits
        if min_value:
            self.min_value = int(min_value)
        else:
            if signed:
                self.min_value = -1 * resolution * 2 ** (self.num_bits - 1)
            else:
                self.min_value = 0
        self.max_value = self.min_value + (2**self.num_bits * resolution)
        self.resolution = int(resolution)
        self.signed = signed
        self.little_endian = little_endian


class Int8Codec(FixedIntCodec):
    """
    metaclass for int8 codec
    """

    def __init__(self, **kwargs):
        super(Int8Codec, self).__init__(num_bits=8, signed=True)


class Int16Codec(FixedIntCodec):
    """
    metaclass for int16 codec
    """

    def __init__(self, **kwargs):
        super(Int16Codec, self).__init__(num_bits=16, signed=True)


class Int32Codec(FixedIntCodec):
    """
    metaclass for int32 codec
    """

    def __init__(self, **kwargs):
        super(Int32Codec, self).__init__(num_bits=32, signed=True)


class Int64Codec(FixedIntCodec):
    """
    metaclass for int64 codec
    """

    def __init__(self, **kwargs):
        super(Int64Codec, self).__init__(num_bits=64, signed=True)


class UInt8Codec(FixedIntCodec):
    """
    metaclass for uint8 codec
    """

    def __init__(self, **kwargs):
        super(UInt8Codec, self).__init__(num_bits=8, signed=False)


class UInt16Codec(FixedIntCodec):
    """
    metaclass for uint16 codec
    """

    def __init__(self, **kwargs):
        super(UInt16Codec, self).__init__(num_bits=16, signed=False)


class UInt32Codec(FixedIntCodec):
    """
    metaclass for uint32 codec
    """

    def __init__(self, **kwargs):
        super(UInt32Codec, self).__init__(num_bits=32, signed=False)


class UInt64Codec(FixedIntCodec):
    """
    metaclass for uint64 codec
    """

    def __init__(self, **kwargs):
        super(UInt32Codec, self).__init__(num_bits=64, signed=False)
