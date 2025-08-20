"""
ltcodecs.ros_msg_codec
----------------------

This module contains the field codec which is used to encode and decode ROS messages.
"""

from __future__ import annotations
import re
from bitstring import ConstBitStream, BitArray
import operator

from typing import Union, Any, Dict
import armw

import ltcodecs as ltcodecs

from .field_codec import FieldCodec
from .multiple_field_codec import MultipleFieldCodec
from .exceptions import EncodingFailed


class RosMsgFieldCodec(FieldCodec):
    """
    Field codec for ROS messages
    """

    def __init__(self, ros_type: Union[str, None], fields: dict = None, **kwargs) -> None:
        """
        Instantiate a ROS message field codec.

        :param ros_type: The ROS message type, either as a string or a ROS Message object
        :type ros_type: Union[str, Message]
        :param fields: The fields of the ROS message, defaults to None.
        :type fields: dict, optional
        :param kwargs: Additional keyword arguments.  Unused by this field codec.
        :type kwargs: dict
        """
        super().__init__(**kwargs)
        self.fields = fields
        self.ros_type = ros_type

        if isinstance(ros_type, str):
            msg_class = armw.import_message_from_name(ros_type)
            if not msg_class:
                raise TypeError(f'Invalid ROS type "{ros_type}" for message codec {id}')
        else:
            msg_class = ros_type
        self.ros_msg_class = msg_class

        self.field_codecs = {}
        # Handle the case where we have to infer the field list from the ROS msg, since the user didn't specify one.
        if not self.fields:
            slots = armw.get_msg_fields_and_types(msg_class)

            new_fields = dict.fromkeys(slots.keys())
            for field_name in new_fields:
                msg_type = slots[field_name]
                if msg_type in ltcodecs.field_codec_classes:
                    field_params = {"codec": msg_type}
                else:
                    # There are two cases here: arrays or nested ROS messages
                    if msg_type.endswith("]"):
                        # either a variable or fixed length array
                        matched = re.match(
                            r"(?P<element_type>.*)\[(?P<array_len>\d*)\]", msg_type
                        )
                        if matched["array_len"]:
                            array_len = int(matched["array_len"])
                            field_params = {
                                "codec": "fixed_len_array",
                                "length": array_len,
                            }
                        else:
                            field_params = {
                                "codec": "variable_len_array",
                                "max_length": 10,
                            }  # TODO: maybe take this as a parameter?
                        # and the element type is either a standard type or a ROS message
                        if matched["element_type"] in ltcodecs.field_codec_classes:
                            field_params["element_type"] = matched["element_type"]
                        else:
                            field_params["element_type"] = "msg"
                            field_params["element_params"] = {
                                "ros_type": matched["element_type"]
                            }
                    else:
                        # It's a nested ROS message
                        field_params = {"codec": "msg", "ros_type": msg_type}

                new_fields[field_name] = field_params

            self.fields = new_fields

        # Now, build the list of codec classes for each field
        self.field_codecs = {}
        for field_name, field_params in self.fields.items():
            # print(field_name, field_params['codec'])
            # print(field_codecs.field_codec_classes[field_params['codec']])
            try:
                if field_params["codec"] not in ltcodecs.metadata_decoders.keys():
                    self.field_codecs[field_name] = ltcodecs.field_codec_classes[
                        field_params["codec"]
                    ](**field_params)
                else:
                    # The metadata codec is a string, which we use for a lookup later.
                    self.field_codecs[field_name] = field_params["codec"]
            except KeyError as err:
                raise KeyError(
                    f"Error parsing codec config for {field_name}.  Got params:\n{field_params}\nError: {err}"
                ) from err

    def encode(self, message: None, metadata=None) -> tuple[BitArray, dict[Any]]:
        """
        Encodes the given ROS message

        :param message: The ROS message to be encoded.
        :param metadata: Optional metadata (e.g. received packet information) to be used during encoding.  Some field
            codecs can use this information.
        :return: A tuple containing the encoded bits and a dictionary with the encoded values.
        :rtype: tuple[BitArray, dict[Any]]
        """
        # ROS messages use __slots__, so we can't use __dict__ or vars() to get the attributes as a dict
        message_dict = {}
        for field in message.__slots__:
            if field[0] == "_":  # ROS2 slots start with _ for some reason
                dict_field = field[1:]
            else:
                dict_field = field

            message_dict[dict_field] = getattr(message, field)

        encoded_bits = BitArray()
        encoded_dict = {}
        for field_name, field_params in self.fields.items():
            field_codec = self.field_codecs.get(field_name, None)
            # Note that metadata encoding is done at the ros_msg_codec level, not here
            if not field_codec or isinstance(field_codec, str):
                continue
            try:
                if isinstance(field_codec, MultipleFieldCodec):
                    field_bits, encoded_dict[field_name], encoded_fields_dict = field_codec.encode_multiple(
                        message_dict[field_name], message_dict)
                    encoded_dict = {**encoded_dict, **encoded_fields_dict}
                else:
                    field_bits, encoded_dict[field_name] = field_codec.encode(message_dict[field_name])

                encoded_bits.append(field_bits)
            except Exception as err:
                raise EncodingFailed(
                    f'Error encoding field "{field_name}" with codec {field_codec} (max len bits {field_codec.max_length_bits})'
                ) from err
        return encoded_bits, encoded_dict

    def decode(self, bits_to_decode: ConstBitStream, metadata=None) -> None:
        """
        Decode a ROS message from a BitStream

        :param bits_to_decode: The bitstream containing the encoded message bits.
        :param metadata: Optional metadata to be used for decoding certain fields.
        :return: The decoded message as a Message object.

        This method decodes an encoded message using the provided bitstream and optional metadata. It iterates
        through the fields in the message and uses the corresponding field codec to decode each field.

        If a nested field codec is a string, it is treated as a metadata codec. If metadata is not provided or the
        metadata codec is unrecognized, the field is skipped.

        If a field codec is an instance of the same class (a nested RosMessageCodec), it recursively calls the decode
        method on that field codec, passing the bitstream and metadata.

        If a field codec is a MultipleFieldCodec, it decodes multiple fields from the bitstream.

        Otherwise, it just uses the field codec to decode the nested field from the bitstream and add it to the message.

        Finally, it constructs and returns a Message object using the decoded fields.
        """
        # go through the bits in sequence until we are decoded.
        # The ConstBitStream has an internal read pointer.
        decoded_message = {}
        for field_name, field_params in self.fields.items():
            field_codec = self.field_codecs[field_name]
            if not field_codec:
                continue

            # Handle metadata codecs
            if isinstance(field_codec, str):
                if not metadata:
                    continue
                try:
                    if field_codec in ltcodecs.metadata_decoders:
                        metadata_attribute = ltcodecs.metadata_decoders[field_codec]
                        value = operator.attrgetter(metadata_attribute)(metadata)
                        decoded_message[field_name] = value
                        continue
                except KeyError:
                    # if we don't recognize the metadata codec, just keep going
                    continue

            # pass metadata only to nested ros msg fields
            if isinstance(field_codec, type(self)):
                decoded_message[field_name] = field_codec.decode(
                    bits_to_decode, metadata=metadata
                )
            else:
                if isinstance(field_codec, MultipleFieldCodec):
                    decoded_message[field_name], decoded_dict = field_codec.decode_multiple(bits_to_decode)
                    decoded_message = {**decoded_message, **decoded_dict}
                else:
                    decoded_message[field_name] = field_codec.decode(bits_to_decode)
        return self.ros_msg_class(**decoded_message)

    def decode_as_dict(self, bits_to_decode: ConstBitStream) -> Dict[Any, Any]:
        """
        Decode the given bits as a dictionary (rather than a ROS message).

        This function is primarily used to generate an object that we can use for calculating CRCs in the message codec.
        It seems like a bit of a hack, but the alternative would require adding a second return value to every field
        decoder.  Since this only affects ROS messages, this keeps the bloat down.

        :param bits_to_decode: The bit stream to be decoded.
        :return: The decoded message as a dictionary.
        """
        decoded_message = {}
        for field_name, field_params in self.fields.items():
            field_codec = self.field_codecs[field_name]
            if hasattr(field_codec, "decode_as_dict"):
                decoded_message[field_name] = field_codec.decode_as_dict(bits_to_decode)
            else:
                decoded_message[field_name] = field_codec.decode(bits_to_decode)
        return decoded_message

    @property
    def min_length_bits(self) -> int:
        return sum([c.min_length_bits for c in self.field_codecs.values()])

    @property
    def max_length_bits(self) -> int:
        return sum([c.max_length_bits for c in self.field_codecs.values()])
