"""
ltcodecs.ros_message_codec
--------------------------

This module contains the the ROS message codec
"""

from __future__ import annotations
from typing import Any, Union
import ltcodecs as ltcodecs
import msgpack
from crccheck.crc import Crc8SaeJ1850, Crc32Iscsi
from bitstring import Bits, ConstBitStream
from copy import copy
import yaml

from rospy_yaml_include.yaml_include import RospyYamlInclude

import armw


class RosMessageCodec(object):
    """
    RosMessageCodec
    """

    def __init__(self, ros_type: Union[None, str], fields_dict: dict = None, checksum=None):
        self.ros_type = ros_type
        self.packet_codec = None
        self.checksum = checksum

        if fields_dict:
            self.metadata_encoder_fields = {}
            for field_name, field_params in fields_dict.items():
                # We only support a few metadata fields for encoding
                codec_name = field_params.get("codec", "auto")
                if codec_name in (ltcodecs.metadata_encoders.keys()):
                    self.metadata_encoder_fields[field_name] = codec_name
        else:
            self.metadata_encoder_fields = None

        self.root_field_codec = ltcodecs.RosMsgFieldCodec(
            ros_type=ros_type, fields=fields_dict
        )

    def encode(self, ros_msg: armw.AnyMsg) -> tuple[Bits, dict[Any]]:
        """
        Encode a ROS message into a bitstream and metadata dictionary

        :param ros_msg: ROS message to encode
        """
        encoded_bits, encoded_dict = self.root_field_codec.encode(ros_msg)

        if self.checksum:
            msgpack_bytes = msgpack.packb(encoded_dict)
            if self.checksum == "crc8":
                calculated_crc = Crc8SaeJ1850.calc(msgpack_bytes)
                encoded_bits.append(Bits(uint=calculated_crc, length=8))
            elif self.checksum == "crc32":
                calculated_crc = Crc32Iscsi.calc(msgpack_bytes)
                encoded_bits.append(Bits(uint=calculated_crc, length=32))

        metadata_dict = self._encode_metadata(ros_msg)

        return encoded_bits, metadata_dict

    def decode(
            self, bits_to_decode: ConstBitStream, received_packet=None
    ) -> armw.AnyMsg:
        """
        Decode a ROS message from a bitstream

        :param bits_to_decode: Bitstream to decode
        """

        if armw.NODE():
            armw.NODE().log_info(f"Decoding ROS message {self.ros_type}")
        else:
            print(f"Decoding ROS message {self.ros_type}")
        # Now, check CRC, if required.
        if self.checksum:
            # We need to decode this as a dict separately, so we need a new copy of the received bitstream.
            bits_copy = copy(bits_to_decode)
            bits_copy.pos = bits_to_decode.pos
            decoded_dict = self.root_field_codec.decode_as_dict(bits_copy)

        ros_msg = self.root_field_codec.decode(bits_to_decode, metadata=received_packet)

        if self.checksum:
            msgpack_bytes = msgpack.packb(decoded_dict)
            if self.checksum == "crc8":
                calculated_crc = Crc8SaeJ1850.calc(msgpack_bytes)
                # Next 8 bits of message are CRC
                received_crc = bits_to_decode.read("uint:8")
            elif self.checksum == "crc32":
                calculated_crc = Crc32Iscsi.calc(msgpack_bytes)
                received_crc = bits_to_decode.read("uint:32")

            if calculated_crc != received_crc:
                raise ValueError("Message CRC Mismatch")

        if armw.NODE():
            armw.NODE().log_info(f"ROS Message: {ros_msg}")
        else:
            print(f"ROS Message: {ros_msg}")
        return ros_msg

    def _encode_metadata(self, ros_msg) -> dict[Any]:
        """Look through the fields dict for one of the magic keywords specified in field_codecs.py"""

        if self.metadata_encoder_fields:
            metadata_dict = {}
            for field_name, codec in self.metadata_encoder_fields.items():
                metadata_dict[field_name] = getattr(ros_msg, codec)
            return metadata_dict
        else:
            return None

    @property
    def max_length_bits(self) -> int:
        if self.checksum == "crc8":
            checksum_len = 8
        elif self.checksum == "crc32":
            checksum_len = 32
        else:
            checksum_len = 0
        return self.root_field_codec.max_length_bits + checksum_len

    @property
    def min_length_bits(self) -> int:
        if self.checksum == "crc8":
            checksum_len = 8
        elif self.checksum == "crc32":
            checksum_len = 32
        else:
            checksum_len = 0
        return self.root_field_codec.min_length_bits + checksum_len

    @classmethod
    def from_codec_file(cls, ros_type: Union[type, str], msg_codec_file_path: str, codec_include_directory: str = None) -> "ROSMessageCodec":
        constructor = RospyYamlInclude(base_directory=codec_include_directory)
        with open(msg_codec_file_path, 'r') as f:
            codec_fields = yaml.load(f, Loader=constructor.add_constructor())
        return cls(ros_type=ros_type, fields_dict=codec_fields)
