from .varint_codec import VarintCodec
from .fixedint_codec import FixedIntCodec
from .fixedint_codec import Int8Codec, Int16Codec, Int32Codec, Int64Codec
from .fixedint_codec import UInt8Codec, UInt16Codec, UInt32Codec, UInt64Codec
from .exponentialgolomb_integer_codec import ExponentialGolombIntegerCodec
from .float_codec import FloatCodec
from .linspace_float_codec import LinspaceFloatCodec
from .ieee_float_codec import IeeeFloat32Codec, IeeeFloat64Codec
from .bool_codec import BoolCodec
from .string_codecs import AsciiStringCodec
from .string_enum_codec import StringEnumCodec
from .bytes_codec import BytesCodec
from .variable_len_array_codec import VariableLenArrayCodec
from .fixed_len_array_codec import FixedLenArrayCodec
from .ros_msg_field_codec import RosMsgFieldCodec
from .ccl_latlon_codec import CclLatLonCodec
from .ccl_latlon_bcd_codec import CclLatLonBcdCodec
from .padding_codec import PaddingCodec
from .rostime_codec import RosTimeCodec
from .ros_message_codec import RosMessageCodec
from .lzma_codec import LzmaCodec
from .optional_field_codec import OptionalFieldCodec
from .exceptions import EncodingFailed

field_codec_classes = {
    "integer": VarintCodec,
    "fixedint": FixedIntCodec,
    "varint": VarintCodec,
    "float": FloatCodec,
    "linspace_float": LinspaceFloatCodec,
    "linspace": LinspaceFloatCodec,
    "uint8": UInt8Codec,
    "uint16": UInt16Codec,
    "uint32": UInt32Codec,
    "uint64": UInt64Codec,
    "int8": Int8Codec,
    "int16": Int16Codec,
    "int32": Int32Codec,
    "int64": Int64Codec,
    "egint": ExponentialGolombIntegerCodec,
    "float32": IeeeFloat32Codec,
    "float64": IeeeFloat64Codec,
    "bool": BoolCodec,
    "boolean": BoolCodec,
    "string": AsciiStringCodec,
    "ascii": AsciiStringCodec,
    "bytes": BytesCodec,
    "msg": RosMsgFieldCodec,
    "ros_msg": RosMsgFieldCodec,
    "variable_len_array": VariableLenArrayCodec,
    "fixed_len_array": FixedLenArrayCodec,
    "ccl_latlon": CclLatLonCodec,
    "ccl_latlon_bcd": CclLatLonBcdCodec,
    "pad": PaddingCodec,
    "padding": PaddingCodec,
    "time": RosTimeCodec,
    "rostime": RosTimeCodec,
    "string_enum": StringEnumCodec,
    "lzma": LzmaCodec,
    "optional": OptionalFieldCodec,
}

metadata_decoders = {
    "src": "packet.src",
    "dest": "packet.dest",
    "dest_decoder": "packet.dest",
    "toa": "cst.toa",
    "snr_in": "cst.snr_in",
}


metadata_encoders = {"dest": "packet.dest"}
