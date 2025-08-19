"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/performance.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15api/performance.proto\x12\x07synapse"\xd3\x01\n\x0fFunctionProfile\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x12\n\ncall_count\x18\x02 \x01(\x04\x12\x17\n\x0fmin_duration_ns\x18\x03 \x01(\x04\x12\x17\n\x0fmax_duration_ns\x18\x04 \x01(\x04\x12\x1b\n\x13average_duration_ns\x18\x05 \x01(\x04\x12\x1a\n\x12median_duration_ns\x18\x06 \x01(\x04\x12\x17\n\x0fp99_duration_ns\x18\x07 \x01(\x04\x12\x1a\n\x12latest_duration_ns\x18\x08 \x01(\x04b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.performance_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_FUNCTIONPROFILE']._serialized_start = 35
    _globals['_FUNCTIONPROFILE']._serialized_end = 246