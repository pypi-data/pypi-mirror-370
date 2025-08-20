.. ltcodecs documentation master file, created by
   sphinx-quickstart on Tue Jun  6 11:03:07 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ltcodecs's documentation!
====================================

There are aliases for each codec that can be used in codec yaml files.
Note that there are multiple aliases for some codec classes.

========================  ====================================================
Alias                     Codec Class
========================  ====================================================
``integer``               :py:class:`~ltcodecs.varint_codec.VarintCodec`
``fixedint``              :py:class:`~ltcodecs.fixedint_codec.FixedIntCodec`
``varint``                :py:class:`~ltcodecs.varint_codec.VarintCodec`
``float``                 :py:class:`~ltcodecs.float_codec.FloatCodec`
``linspace_float``        :py:class:`~ltcodecs.linspace_float_codec.LinspaceFloatCodec`
``linspace``              :py:class:`~ltcodecs.linspace_float_codec.LinspaceFloatCodec`
``uint8``                 :py:class:`~ltcodecs.fixedint_codec.UInt8Codec`
``uint16``                :py:class:`~ltcodecs.fixedint_codec.UInt16Codec`
``uint32``                :py:class:`~ltcodecs.fixedint_codec.UInt32Codec`
``uint64``                :py:class:`~ltcodecs.fixedint_codec.UInt64Codec`
``int8``                  :py:class:`~ltcodecs.fixedint_codec.Int8Codec`
``int16``                 :py:class:`~ltcodecs.fixedint_codec.Int16Codec`
``int32``                 :py:class:`~ltcodecs.fixedint_codec.Int32Codec`
``int64``                 :py:class:`~ltcodecs.fixedint_codec.Int64Codec`
``egint``                 :py:class:`~ltcodecs.exponentialgolomb_integer_codec.ExponentialGolombIntegerCodec`
``float32``               :py:class:`~ltcodecs.ieee_float_codec.IeeeFloat32Codec`
``float64``               :py:class:`~ltcodecs.ieee_float_codec.IeeeFloat64Codec`
``bool``                  :py:class:`~ltcodecs.bool_codec.BoolCodec`
``string``                :py:class:`~ltcodecs.string_codecs.AsciiStringCodec`
``ascii``                 :py:class:`~ltcodecs.string_codecs.AsciiStringCodec`
``bytes``                 :py:class:`~ltcodecs.bytes_codec.BytesCodec`
``msg``                   :py:class:`~ltcodecs.ros_msg_field_codec.RosMsgFieldCodec`
``ros_msg``               :py:class:`~ltcodecs.ros_msg_field_codec.RosMsgFieldCodec`
``variable_len_array``    :py:class:`~ltcodecs.variable_len_array_codec.VariableLenArrayCodec`
``fixed_len_array``       :py:class:`~ltcodecs.fixed_len_array_codec.FixedLenArrayCodec`
``ccl_latlon``            :py:class:`~ltcodecs.ccl_latlon_codec.CclLatLonCodec`,
``ccl_latlon_bcd``        :py:class:`~ltcodecs.ccl_latlon_bcd_codec.CclLatLonBcdCodec`
``pad``                   :py:class:`~ltcodecs.padding_codec.PaddingCodec`
``padding``               :py:class:`~ltcodecs.padding_codec.PaddingCodec`
``time``                  :py:class:`~ltcodecs.rostime_codec.RosTimeCodec`
``rostime``               :py:class:`~ltcodecs.rostime_codec.RosTimeCodec`
``string_enum``           :py:class:`~ltcodecs.string_enum_codec.StringEnumCodec`
``lzma``                  :py:class:`~ltcodecs.lzma_codec.LzmaCodec`
``optional``              :py:class:`~ltcodecs.optional_field_codec.OptionalFieldCodec`
========================  ====================================================


.. toctree::
   :maxdepth: 4
   :caption: Contents:

   ltcodecs
   tests



