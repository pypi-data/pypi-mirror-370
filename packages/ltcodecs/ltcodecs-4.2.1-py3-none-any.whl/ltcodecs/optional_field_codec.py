"""
ltcodecs.optional_field_codec
------------------------------

This module contains the OptionalCodec class, which uses a boolean field to control whether a set of target fields
is encoded in the message (making those fields optional).
"""

from __future__ import annotations
from bitstring import BitArray, ConstBitStream, Bits
from .multiple_field_codec import MultipleFieldCodec
import ltcodecs as ltcodecs
from typing import Any
from .exceptions import EncodingFailed


class OptionalFieldCodec(MultipleFieldCodec):
    """
    codec for optional fields, where a boolean field controls whether "target" fields should be encoded.

    If the controlling boolean field is true, the target fields will be encoded using parameters in the target_fields
    dictionary (much like ros messages are encoded).  If false, the target fields won't be encoded (thus using no
    space in the encoded message).

    Args:
        target_fields: Dict containing fields and associated parameters.
            In the form {field_name: {codec: <codec name>, <codec_param>, etc.}}
    """

    def __init__(
        self, target_fields: dict = None, **kwargs: object
    ) -> None:

        self.target_fields = target_fields
        self.field_codecs = {}
        if target_fields:
            for field_name, field_params in self.target_fields.items():
                # print(field_name, field_params['codec'])
                # print(field_codecs.field_codec_classes[field_params['codec']])
                try:
                    self.field_codecs[field_name] = ltcodecs.field_codec_classes[field_params["codec"]](**field_params)
                except KeyError as err:
                    raise KeyError(
                        f"Error parsing codec config for {field_name}.  Got params:\n{field_params}\nError: {err}"
                    ) from err


    def encode_multiple(self, value: bool, message_dict: dict) -> tuple[Bits, bool, dict]:
        """
        encode a set of fields: the boolean used to control the "nullable" target field(s), and the target if requested

        :param value: the boolean field value that indicates whether the target fields should be encoded
        :param message_dict: the full message from which the target field is read

        :return: A tuple containing the encoded bits, the boolean value that indicates if the optional fields are encoded
        and a dictionary of the encoded fields (after compression, if the target field codec does that).
        """
        value = bool(value)
        value_bits = BitArray(bool=value)

        # If the value is false, we treat this like a boolean codec
        if not value:
            return value_bits, value, {}

        # Otherwise, we want to encode a bit (to indicate that the target is present), and then the target fields
        encoded_dict = {}
        for field_name, field_params in self.target_fields.items():
            try:
                field_codec = self.field_codecs[field_name]
                # Note that metadata encoding is done at the ros_msg_codec level, not here
                if not field_codec or isinstance(field_codec, str):
                    continue
                if isinstance(field_codec, MultipleFieldCodec):
                    field_bits, encoded_dict[field_name], encoded_fields_dict = field_codec.encode_multiple(value, message_dict)
                    encoded_dict = {**encoded_dict, **encoded_fields_dict}
                else:
                    field_bits, encoded_dict[field_name] = field_codec.encode(message_dict[field_name])

                value_bits.append(field_bits)
            except Exception as err:
                raise EncodingFailed(
                    f'Error encoding field "{field_name}" with codec {field_codec} (max len bits {field_codec.max_length_bits})'
                ) from err
        return value_bits, value, encoded_dict

    def decode_multiple(self, bits_to_decode: ConstBitStream) -> tuple[bool, dict]:
        """
        decode a nullable (optional) field: the boolean used to control the "nullable" target, and the target if present

        Args:
            bits_to_decode: the bits to decode

        Returns:
            value: the value of the controlling boolean field
            values_dict: Dictionary with other decoded field name: value pairs
        """

        value = bits_to_decode.read("bool")

        if not value:
            return value, {}

        decoded_message = {}
        for field_name, field_params in self.target_fields.items():
            field_codec = self.field_codecs[field_name]
            if hasattr(field_codec, "decode_as_dict"):
                decoded_message[field_name] = field_codec.decode_as_dict(bits_to_decode)
            else:
                decoded_message[field_name] = field_codec.decode(bits_to_decode)

        return value, decoded_message

    @property
    def min_length_bits(self) -> int:
        return 1

    @property
    def max_length_bits(self) -> int:
        return 1 + sum([c.max_length_bits for c in self.field_codecs.values()])
