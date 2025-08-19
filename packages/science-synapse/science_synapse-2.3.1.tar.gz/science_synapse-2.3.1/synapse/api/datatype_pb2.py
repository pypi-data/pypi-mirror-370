"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/datatype.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from ..api import channel_pb2 as api_dot_channel__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12api/datatype.proto\x12\x07synapse\x1a\x1cgoogle/protobuf/struct.proto\x1a\x11api/channel.proto"\x86\x03\n\x06Tensor\x12\x14\n\x0ctimestamp_ns\x18\x01 \x01(\x04\x12\r\n\x05shape\x18\x02 \x03(\x05\x12$\n\x05dtype\x18\x03 \x01(\x0e2\x15.synapse.Tensor.DType\x12.\n\nendianness\x18\x04 \x01(\x0e2\x1a.synapse.Tensor.Endianness\x12\x0c\n\x04data\x18\x05 \x01(\x0c"\xb3\x01\n\x05DType\x12\x0e\n\nDT_INVALID\x10\x00\x12\x0c\n\x08DT_FLOAT\x10\x01\x12\r\n\tDT_DOUBLE\x10\x02\x12\x0c\n\x08DT_UINT8\x10\x03\x12\r\n\tDT_UINT16\x10\x04\x12\r\n\tDT_UINT32\x10\x05\x12\r\n\tDT_UINT64\x10\x06\x12\x0b\n\x07DT_INT8\x10\x07\x12\x0c\n\x08DT_INT16\x10\x08\x12\x0c\n\x08DT_INT32\x10\t\x12\x0c\n\x08DT_INT64\x10\n\x12\x0b\n\x07DT_BOOL\x10\x0b"=\n\nEndianness\x12\x18\n\x14TENSOR_LITTLE_ENDIAN\x10\x00\x12\x15\n\x11TENSOR_BIG_ENDIAN\x10\x01"\xb5\x01\n\x0eBroadbandFrame\x12\x14\n\x0ctimestamp_ns\x18\x01 \x01(\x04\x12\x17\n\x0fsequence_number\x18\x02 \x01(\x04\x12\x12\n\nframe_data\x18\x03 \x03(\x11\x12\x16\n\x0esample_rate_hz\x18\x04 \x01(\r\x12-\n\x0echannel_ranges\x18\x05 \x03(\x0b2\x15.synapse.ChannelRange\x12\x19\n\x11unix_timestamp_ns\x18\x06 \x01(\x04"~\n\nTimeseries\x12\n\n\x02id\x18\x01 \x01(\r\x121\n\ndatapoints\x18\x02 \x03(\x0b2\x1d.synapse.Timeseries.Datapoint\x1a1\n\tDatapoint\x12\x14\n\x0ctimestamp_ns\x18\x01 \x01(\x04\x12\x0e\n\x06sample\x18\x02 \x01(\x11"\xb5\x01\n\x0fAnnotatedTensor\x12\x1f\n\x06tensor\x18\x01 \x01(\x0b2\x0f.synapse.Tensor\x128\n\x08metadata\x18\x02 \x03(\x0b2&.synapse.AnnotatedTensor.MetadataEntry\x1aG\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12%\n\x05value\x18\x02 \x01(\x0b2\x16.google.protobuf.Value:\x028\x01*x\n\x08DataType\x12\x14\n\x10kDataTypeUnknown\x10\x00\x12\x08\n\x04kAny\x10\x01\x12\x0e\n\nkBroadband\x10\x02\x12\x0f\n\x0bkSpiketrain\x10\x03\x12\x0f\n\x0bkTimestamps\x10\x04\x12\n\n\x06kImage\x10\x05\x12\x0e\n\nkWaveforms\x10\x06b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.datatype_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ANNOTATEDTENSOR_METADATAENTRY']._loaded_options = None
    _globals['_ANNOTATEDTENSOR_METADATAENTRY']._serialized_options = b'8\x01'
    _globals['_DATATYPE']._serialized_start = 969
    _globals['_DATATYPE']._serialized_end = 1089
    _globals['_TENSOR']._serialized_start = 81
    _globals['_TENSOR']._serialized_end = 471
    _globals['_TENSOR_DTYPE']._serialized_start = 229
    _globals['_TENSOR_DTYPE']._serialized_end = 408
    _globals['_TENSOR_ENDIANNESS']._serialized_start = 410
    _globals['_TENSOR_ENDIANNESS']._serialized_end = 471
    _globals['_BROADBANDFRAME']._serialized_start = 474
    _globals['_BROADBANDFRAME']._serialized_end = 655
    _globals['_TIMESERIES']._serialized_start = 657
    _globals['_TIMESERIES']._serialized_end = 783
    _globals['_TIMESERIES_DATAPOINT']._serialized_start = 734
    _globals['_TIMESERIES_DATAPOINT']._serialized_end = 783
    _globals['_ANNOTATEDTENSOR']._serialized_start = 786
    _globals['_ANNOTATEDTENSOR']._serialized_end = 967
    _globals['_ANNOTATEDTENSOR_METADATAENTRY']._serialized_start = 896
    _globals['_ANNOTATEDTENSOR_METADATAENTRY']._serialized_end = 967