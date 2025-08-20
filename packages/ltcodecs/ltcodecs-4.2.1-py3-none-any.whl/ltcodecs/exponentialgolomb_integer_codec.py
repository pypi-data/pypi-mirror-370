"""
ltcodecs.exponentialgolomb_integer_codec
---------------------

This module contains the ExponentialGolombIntegerCodec class, which uses Exponential-Golomb coding to encode
and decode integers.

"""

from __future__ import annotations

from math import ceil, log2

from bitstring import ConstBitStream, Bits
from .field_codec import FieldCodec


class ExponentialGolombIntegerCodec(FieldCodec):
    """
    An encoder and decoder using Exponential-Golomb coding for integer values.

    This codec operates based on Exponential-Golomb encoding, allowing efficient representation of
    integer values within a defined range using a variable-length encoding scheme. The encoding
    behavior (signed or unsigned, reversed or not) depends on the relationship between
    `min_value`, `max_value`, and `base_value`.

    Exponential-Golomb encoding is suited to encoding values that are more likely to be near the
    base value.  It encodes values near the base value more efficiently at the cost of less-efficient encoding
    of values further from the base value.

    :ivar min_value: Minimum value of the range supported by the codec. Used to constrain input.
    :type min_value: int
    :ivar max_value: Maximum value of the range supported by the codec. Used to constrain input.
    :type max_value: int
    :ivar resolution: Step size or granularity for encoding and decoding values. Defines the
        smallest possible difference between encoded values.
    :type resolution: int
    :ivar base_value: Reference value used to calculate offsets for encoding. Determines the
        codec's operational mode (e.g., signed/unsigned, reversed/non-reversed). Defaults to
        `min_value` if not specified during initialization.
    :type base_value: int
    """

    def __init__(
        self,
        min_value: int,
        max_value: int,
        resolution: int = 1,
        base_value: int | None = None,
        **kwargs,
    ) -> None:
        self.max_value = int(max_value)
        self.min_value = int(min_value)
        self.resolution = int(resolution)
        # If no base value is provided, default to the minimum value.
        if base_value:
            self.base_value = int(base_value)
        else:
            self.base_value = self.min_value

        if self.min_value > self.max_value:
            raise ValueError("ExponentialGolombIntegerCodec max_value must be greater than min_value")

        if self.base_value > self.max_value or self.base_value < self.min_value:
            raise ValueError("ExponentialGolombIntegerCodec base_value must be between min_value and max_value")

        if self.resolution < 1:
            raise ValueError("ExponentialGolombIntegerCodec resolution must be at least 1")

        # Figure out the mode of operation
        # We use unsigned encoding if the base value is eiter the minimum value or the maximum value.  In the case
        # where the base value is the same as the max value, we assume we should work "backwards", where values
        # closer to the maximum are encoded as smaller values.
        # If the base value falls between the min and max values, we use signed encoding.
        if self.min_value == self.base_value:
            self._is_signed = False
            self._is_reversed = False
        elif self.max_value == self.base_value:
            self._is_signed = False
            self._is_reversed = True
        else:
            self._is_signed = True
            self._is_reversed = False

        self._max_length_bits = max(len(self.encode(self.max_value)[0]), len(self.encode(self.min_value)[0]))

    def encode(self, value: int) -> tuple[Bits, int]:
        """
        Encodes the given integer value into a tuple consisting of an encoded representation
        and the compressed integer value. The value is clamped
        within the predefined range determined by `min_value` and `max_value`.

        :param value:
            The integer value to be encoded. This value is adjusted within the
            limits of `min_value` and `max_value` and then processed to generate
            its encoded counterpart.
        :return:
            A tuple containing the encoded representation (`Bits` object) and the
            encoded integer value
        """
        value = int(value)
        if value < self.min_value:
            value = self.min_value
        elif value > self.max_value:
            value = self.max_value

        if not self._is_reversed:
            offset = value - self.base_value
        else:
            offset = self.base_value - value

        discretized_offset = offset // self.resolution
        if not self._is_reversed:
            encoded_value = self.base_value + (discretized_offset * self.resolution)
        else:
            encoded_value = self.base_value - (discretized_offset * self.resolution)

        if self._is_signed:
            encoded_bits = Bits(se=discretized_offset)
        else:
            encoded_bits = Bits(ue=discretized_offset)

        return encoded_bits, encoded_value

    def decode(self, bits_to_decode: ConstBitStream) -> int:
        """
        Decodes a given bitstream into an integer value based on the configuration of
        the decoder.

        :param bits_to_decode: A bitstream containing the encoded value to be decoded.
                               Data is read in either signed or unsigned representation
                               depending on the decoder configuration.
        :type bits_to_decode: ConstBitStream
        :return: The decoded integer value computed after applying the transformations
                 and adjustments based on the decoder's configuration.
        :rtype: int
        """
        if self._is_signed:
            discretized_offset = bits_to_decode.read("se")
        else:
            discretized_offset = bits_to_decode.read("ue")

        if not self._is_reversed:
            value = self.base_value + (discretized_offset * self.resolution)
        else:
            value = self.base_value - (discretized_offset * self.resolution)

        return value

    @property
    def max_length_bits(self) -> int:
        return self._max_length_bits

    @property
    def min_length_bits(self) -> int:
        return 1

    def __repr__(self) -> str:
        """
        returns string representation of ExponentialGolombIntegerCodec
        """
        return f"ExponentialGolombIntegerCodec {id(self):x}: base_value={self.base_value}, min_value={self.min_value}, max_value={self.max_value}, resolution={self.resolution} {'(signed)' if self._is_signed else '(unsigned)'}"
