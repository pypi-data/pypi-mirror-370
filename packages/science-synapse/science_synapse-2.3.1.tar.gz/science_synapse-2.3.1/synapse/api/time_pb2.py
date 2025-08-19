"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/time.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eapi/time.proto\x12\x07synapse"\xaf\x01\n\x0eTimeSyncPacket\x12\x11\n\tclient_id\x18\x01 \x01(\x07\x12\x10\n\x08sequence\x18\x02 \x01(\x07\x12\x1b\n\x13client_send_time_ns\x18\x03 \x01(\x06\x12\x1e\n\x16server_receive_time_ns\x18\x04 \x01(\x06\x12\x1b\n\x13server_send_time_ns\x18\x05 \x01(\x06\x12\x1e\n\x16client_receive_time_ns\x18\x06 \x01(\x06*c\n\nTimeSource\x12\x17\n\x13TIME_SOURCE_UNKNOWN\x10\x00\x12\x1c\n\x18TIME_SOURCE_STEADY_CLOCK\x10\x01\x12\x1e\n\x1aTIME_SOURCE_SAMPLE_COUNTER\x10\x02b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.time_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_TIMESOURCE']._serialized_start = 205
    _globals['_TIMESOURCE']._serialized_end = 304
    _globals['_TIMESYNCPACKET']._serialized_start = 28
    _globals['_TIMESYNCPACKET']._serialized_end = 203