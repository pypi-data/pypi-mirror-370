"""
ltcodecs.ccl_latlon_bcd_codec
-----------------------------

This module contains the the ccl latlon bcd codec
"""

from __future__ import annotations
from bitstring import ConstBitStream, Bits
from .field_codec import FieldCodec
from math import modf, copysign


class CclLatLonBcdCodec(FieldCodec):
    """This codec is horrifically inefficient, but included for compatibility with messages like MDAT_RANGER"""

    def __init__(self, lat_not_lon=True, **kwargs):
        self.lat_not_lon = lat_not_lon

    def encode(self, value: float) -> tuple[Bits, float]:
        sign = copysign(1, value)
        abs_value = abs(value)
        frac, degrees = modf(abs_value)
        degrees = int(degrees)
        minutes = frac * 60
        dec_min = int(minutes * 10000)

        if self.lat_not_lon:
            sign_char = "a" if sign > 0 else "c"
        else:
            sign_char = "b" if sign > 0 else "d"

        hex_string = f"{degrees:03d}{sign_char}{dec_min:06d}"
        encoded_value = sign * (degrees + (dec_min / 10000) / 60)
        encoded_bits = Bits(hex=hex_string)

        return encoded_bits, encoded_value

    def decode(self, bits_to_decode: ConstBitStream) -> float:
        string_bytes = bits_to_decode.read("bytes:5")
        hex_string = "".join(f"{x:02x}" for x in string_bytes)

        degrees = int(hex_string[0:3])
        direction = 1 if hex_string[3] in ("a", "b") else -1
        minutes = float(hex_string[4:10]) / 10000.0

        value = direction * (degrees + (minutes / 60))
        return value

    @property
    def max_length_bits(self) -> int:
        return 40

    @property
    def min_length_bits(self) -> int:
        return 40
