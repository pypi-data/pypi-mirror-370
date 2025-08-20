#!/usr/bin/env python3

"""
Test suite for ltcodecs
"""
import os
import time
import sys
import pytest
from bitstring import ConstBitStream

import armw

String = armw.import_message("std_msgs", "String")
ColorRGBA = armw.import_message("std_msgs", "ColorRGBA")

import ltcodecs


class TestCodecs:
    """
    Test class for ltcodecs
    """

    def test_bool_codec(self) -> None:
        """test functionality of the boolean codec"""

        input_bool = True
        codec = ltcodecs.BoolCodec()
        encoded_bool = codec.encode(input_bool)

        bit_stream = ConstBitStream(encoded_bool[0])

        decoded_bool = codec.decode(bit_stream)
        assert decoded_bool == input_bool, "decoded boolean does not match input boolean"

    def test_string_codec(self) -> None:
        """test functionality of the string codec"""

        input_str = "This is a test string"
        codec = ltcodecs.string_codecs.AsciiStringCodec()
        encoded_str = codec.encode(input_str)

        bit_stream = ConstBitStream(encoded_str[0])

        decoded_str = codec.decode(bit_stream)
        assert decoded_str == input_str, "decoded string does not match input string"

    def test_bytes_codec(self) -> None:
        """test functionality of the bytes codec"""

        input_str = "This is a test string"
        input_bytes = input_str.encode()  # encode entryString to bytes

        codec = ltcodecs.bytes_codec.BytesCodec(100)
        encoded_byes = codec.encode(input_bytes)

        bit_stream = ConstBitStream(encoded_byes[0])

        decoded_bytes = codec.decode(bit_stream).decode()
        assert decoded_bytes == input_str, "decoded string does not match input string"

    def test_lzma_codec(self) -> None:
        """test functionality of the LZMA codec"""

        input_str = "This is a test string"
        input_bytes = input_str.encode()  # encode entryString to bytes

        codec = ltcodecs.lzma_codec.LzmaCodec(100)
        encoded_byes = codec.encode(input_bytes)

        bit_stream = ConstBitStream(encoded_byes[0])

        decoded_bytes = codec.decode(bit_stream).decode()
        print(decoded_bytes)
        assert decoded_bytes == input_str, "decoded string does not match input string"

    def test_ccl_latlon_bcd_codec(self) -> None:
        """test functionality of the CclLatLonBcd codec"""

        input_coord = 41.5

        codec = ltcodecs.ccl_latlon_bcd_codec.CclLatLonBcdCodec(input_coord)
        encoded_coord = codec.encode(input_coord)

        bit_stream = ConstBitStream(encoded_coord[0])

        decoded_coord = codec.decode(bit_stream)

        pytest.approx(decoded_coord, input_coord)

    def test_ccl_latlon_codec(self) -> None:
        """test functionality of the CclLatLon codec"""

        input_coord = 41.5

        codec = ltcodecs.ccl_latlon_codec.CclLatLonCodec()
        encoded_coord = codec.encode(input_coord)

        bit_stream = ConstBitStream(encoded_coord[0])

        decoded_coord = codec.decode(bit_stream)

        pytest.approx(decoded_coord, input_coord)

    def test_int8_codec(self) -> None:
        """test functionality of the signed integer 8 codec"""

        input_int = -21

        codec = ltcodecs.FixedIntCodec(8, True)
        encoded_int = codec.encode(input_int)

        bit_stream = ConstBitStream(encoded_int[0])

        decoded_int = codec.decode(bit_stream)

        assert decoded_int == input_int

    def test_int16_codec(self) -> None:
        """test functionality of the signed integer 16 codec"""

        input_int = -21

        codec = ltcodecs.FixedIntCodec(16, True)
        encoded_int = codec.encode(input_int)

        bit_stream = ConstBitStream(encoded_int[0])

        decoded_int = codec.decode(bit_stream)

        assert decoded_int == input_int

    def test_int32_codec(self) -> None:
        """test functionality of the signed integer 32 codec"""

        input_int = 1

        codec = ltcodecs.FixedIntCodec(32, True)
        encoded_int = codec.encode(input_int)

        bit_stream = ConstBitStream(encoded_int[0])

        decoded_int = codec.decode(bit_stream)

        assert decoded_int == input_int

    def test_int64_codec(self) -> None:
        """test functionality of the signed integer 64 codec"""

        input_int = 1

        codec = ltcodecs.FixedIntCodec(64, True)
        encoded_int = codec.encode(input_int)

        bit_stream = ConstBitStream(encoded_int[0])

        decoded_int = codec.decode(bit_stream)

        assert decoded_int == input_int

    def test_uint8_codec(self) -> None:
        """test functionality of the unsigned integer 8 codec"""

        input_int = 21

        codec = ltcodecs.FixedIntCodec(8)
        encoded_int = codec.encode(input_int)

        bit_stream = ConstBitStream(encoded_int[0])

        decoded_int = codec.decode(bit_stream)

        assert decoded_int == input_int

    def test_uint16_codec(self) -> None:
        """test functionality of the unsigned integer 16 codec"""

        input_int = 21

        codec = ltcodecs.FixedIntCodec(16)
        encoded_int = codec.encode(input_int)

        bit_stream = ConstBitStream(encoded_int[0])

        decoded_int = codec.decode(bit_stream)

        assert decoded_int == input_int

    def test_uint32_codec(self) -> None:
        """test functionality of the unsigned integer 32 codec"""

        input_int = 21

        codec = ltcodecs.FixedIntCodec(32)
        encoded_int = codec.encode(input_int)

        bit_stream = ConstBitStream(encoded_int[0])

        decoded_int = codec.decode(bit_stream)

        assert decoded_int == input_int

    def test_uint64_codec(self) -> None:
        """test functionality of the unsigned integer 64 codec"""

        input_int = 21

        codec = ltcodecs.FixedIntCodec(64)
        encoded_int = codec.encode(input_int)

        bit_stream = ConstBitStream(encoded_int[0])

        decoded_int = codec.decode(bit_stream)

        assert decoded_int == input_int

    def test_float_codec(self) -> None:
        """test functionality of the Float codec"""

        input_float = 21.53

        codec = ltcodecs.float_codec.FloatCodec(0, 100, 2)
        encoded_float = codec.encode(input_float)

        bit_stream = ConstBitStream(encoded_float[0])

        decoded_float = codec.decode(bit_stream)

        pytest.approx(decoded_float, input_float)

    def test_ieee_float_codec(self) -> None:
        """test functionality of the IEEE Float codec"""

        input_float = 21.23

        codec = ltcodecs.ieee_float_codec.IeeeFloatCodec()
        encoded_float = codec.encode(input_float)

        bit_stream = ConstBitStream(encoded_float[0])

        decoded_float = codec.decode(bit_stream)

        pytest.approx(decoded_float, input_float)

    def test_linspace_float_codec(self) -> None:
        """test functionality of the Linspace Float codec"""

        input_float = 21.23

        codec = ltcodecs.linspace_float_codec.LinspaceFloatCodec(0, 100, num_bits=32)
        encoded_float = codec.encode(input_float)

        bit_stream = ConstBitStream(encoded_float[0])

        decoded_float = codec.decode(bit_stream)

        pytest.approx(decoded_float, input_float)

    def test_varint_codec(self) -> None:
        """test functionality of the Varint codec"""

        input_int = 21

        codec = ltcodecs.VarintCodec(0, 100)
        encoded_int = codec.encode(input_int)

        bit_stream = ConstBitStream(encoded_int[0])

        decoded_int = codec.decode(bit_stream)

        assert decoded_int == input_int, "decoded int does not match input int"

    def test_fixed_length_array_codec(self) -> None:
        """test functionality of the fixed length array codec"""

        input_array = [1, 2, 3, 4]

        codec = ltcodecs.FixedLenArrayCodec(
            "integer", 4, element_params={"min_value": 0, "max_value": 100}
        )
        encoded_int = codec.encode(input_array)

        bit_stream = ConstBitStream(encoded_int[0])

        decoded_int = codec.decode(bit_stream)

        assert decoded_int == input_array, "decoded array does not match input array"

    def test_variable_legnth_array_codec(self) -> None:
        """test functionality of the variable length array codec"""

        input_array = [1, 2, 3, 4]

        codec = ltcodecs.VariableLenArrayCodec(
            "integer", 4, element_params={"min_value": 0, "max_value": 100}
        )
        encoded_bits = codec.encode(input_array)
        bit_stream = ConstBitStream(encoded_bits[0])
        decoded_array = codec.decode(bit_stream)

        assert decoded_array == input_array, "decoded array does not match input array"

        # Now, test making it nullable
        codec = ltcodecs.VariableLenArrayCodec(
            "integer", 4, nullable=True, element_params={"min_value": 0, "max_value": 100}
        )
        encoded_bits = codec.encode(input_array)
        bit_stream = ConstBitStream(encoded_bits[0])
        decoded_array = codec.decode(bit_stream)

        assert decoded_array == input_array, "decoded array does not match input array (with nullable codec)"

        # ... and try actually making it null
        encoded_bits = codec.encode([])
        bit_stream = ConstBitStream(encoded_bits[0])
        decoded_array = codec.decode(bit_stream)

        assert len(bit_stream) == 1, "Encoded message (when nulled) has wrong number of bits"

    def test_ros_message_codec(self) -> None:
        """test functionality of the ros message  codec"""

        msg = String()
        msg.data = "test"

        codec = ltcodecs.RosMessageCodec("std_msgs/String")
        encoded_msg = codec.encode(msg)

        bit_stream = ConstBitStream(encoded_msg[0])

        decoded_msg = codec.decode(bit_stream)

        pytest.approx(decoded_msg, msg)

    def test_optional_codec(self) -> None:
        """test functionality of the OptionalFieldCodec codec"""

        # use a ColorRGBA message because it's part of std_msgs and has a field that we can cast as a boolean
        msg = ColorRGBA(r=1, g=1234.5678, b=3.14, a=4)
        message_dict = {}
        for field in ['r', 'g', 'b', 'a']:
            message_dict[field] = getattr(msg, field)

        codec = ltcodecs.OptionalFieldCodec(target_fields={'g': {'codec': 'float32'}, 'b': {'codec': 'float32'}})

        encoded_msg = codec.encode_multiple(msg.r, message_dict)
        bit_stream = ConstBitStream(encoded_msg[0])

        decoded_r, decoded_dict = codec.decode_multiple(bit_stream)
        decoded_dict = {'r': decoded_r, **decoded_dict}

        assert decoded_dict['g'] == pytest.approx(msg.g), "decoded target value doesn't match input"
        assert decoded_dict['b'] == pytest.approx(msg.b), "decoded target value doesn't match input"
        assert len(bit_stream) == 1+32+32, "Encoded message has wrong number of bits"

        # Now try with nulled
        msg.r = 0

        encoded_msg = codec.encode_multiple(msg.r, message_dict)
        bit_stream = ConstBitStream(encoded_msg[0])

        decoded_r, decoded_dict = codec.decode_multiple(bit_stream)
        decoded_dict = {'r': decoded_r, **decoded_dict}

        assert len(bit_stream) == 1, "Encoded message (when nulled) has wrong number of bits"

    def test_ros_message_field_codec(self) -> None:
        """test functionality of the ros message field codec"""

        msg = String()
        msg.data = "test"

        codec = ltcodecs.RosMsgFieldCodec("std_msgs/String")
        encoded_msg = codec.encode(msg)

        bit_stream = ConstBitStream(encoded_msg[0])

        decoded_msg = codec.decode(bit_stream)

        pytest.approx(decoded_msg, msg)

    def test_ros_time_codec(self) -> None:
        """test functionality of the ros time field codec"""

        input_time = armw.Time().from_sec(time.time())

        codec = ltcodecs.rostime_codec.RosTimeCodec(precision=20)
        encoded_time = codec.encode(input_time)

        bit_stream = ConstBitStream(encoded_time[0])

        decoded_time = armw.get_time_object(codec.decode(bit_stream))
        assert decoded_time == input_time, "Decoded time does not match input time"

    def test_string_enum_codec(self) -> None:
        """test functionality of the StringEnum field codec"""

        test_string = "test2"
        codec = ltcodecs.string_enum_codec.StringEnumCodec(
            entries=["Test1", "test2", "other strings here"]
        )
        encoded = codec.encode("test2")
        bit_stream = ConstBitStream(encoded[0])
        decoded = codec.decode(bit_stream)

        assert test_string == decoded, "Decoded string does not match input string"

    def test_ros_message_codec_from_yaml(self) -> None:
        """test functionality of the ros message  codec"""

        msg = String()
        msg.data = "test"

        codec_file_path = os.path.dirname(__file__) + "/string_msg_codec.yaml"

        codec = ltcodecs.RosMessageCodec.from_codec_file("std_msgs/String", codec_file_path)
        encoded_msg = codec.encode(msg)

        bit_stream = ConstBitStream(encoded_msg[0])

        decoded_msg = codec.decode(bit_stream)

        pytest.approx(decoded_msg, msg)

    def test_padding(self) -> None:
        value = "some nonsense"
        codec = ltcodecs.PaddingCodec(num_bits=19)
        encoded = codec.encode(value)

        bit_stream = ConstBitStream(encoded[0])
        decoded_value = codec.decode(bit_stream)
        assert decoded_value is None

        assert len(bit_stream) == 19


if __name__ == "__main__":
    sys.exit(pytest.main(['--capture=no', '--junitxml=results.xml', '--cov=ltcodecs', '--cov-report=xml', '--cov-report=html', '--cov-report=term', __file__]))
