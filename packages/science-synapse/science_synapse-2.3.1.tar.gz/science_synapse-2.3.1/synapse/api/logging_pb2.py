"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/logging.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11api/logging.proto\x12\x07synapse"c\n\x08LogEntry\x12\x14\n\x0ctimestamp_ns\x18\x01 \x01(\x04\x12 \n\x05level\x18\x02 \x01(\x0e2\x11.synapse.LogLevel\x12\x0e\n\x06source\x18\x03 \x01(\t\x12\x0f\n\x07message\x18\x04 \x01(\t"u\n\x0fLogQueryRequest\x12\x15\n\rstart_time_ns\x18\x01 \x01(\x04\x12\x13\n\x0bend_time_ns\x18\x02 \x01(\x04\x12\x10\n\x08since_ms\x18\x03 \x01(\x04\x12$\n\tmin_level\x18\x04 \x01(\x0e2\x11.synapse.LogLevel"6\n\x10LogQueryResponse\x12"\n\x07entries\x18\x01 \x03(\x0b2\x11.synapse.LogEntry"7\n\x0fTailLogsRequest\x12$\n\tmin_level\x18\x01 \x01(\x0e2\x11.synapse.LogLevel*\x8e\x01\n\x08LogLevel\x12\x15\n\x11LOG_LEVEL_UNKNOWN\x10\x00\x12\x13\n\x0fLOG_LEVEL_DEBUG\x10\x01\x12\x12\n\x0eLOG_LEVEL_INFO\x10\x02\x12\x15\n\x11LOG_LEVEL_WARNING\x10\x03\x12\x13\n\x0fLOG_LEVEL_ERROR\x10\x04\x12\x16\n\x12LOG_LEVEL_CRITICAL\x10\x05b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.logging_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_LOGLEVEL']._serialized_start = 364
    _globals['_LOGLEVEL']._serialized_end = 506
    _globals['_LOGENTRY']._serialized_start = 30
    _globals['_LOGENTRY']._serialized_end = 129
    _globals['_LOGQUERYREQUEST']._serialized_start = 131
    _globals['_LOGQUERYREQUEST']._serialized_end = 248
    _globals['_LOGQUERYRESPONSE']._serialized_start = 250
    _globals['_LOGQUERYRESPONSE']._serialized_end = 304
    _globals['_TAILLOGSREQUEST']._serialized_start = 306
    _globals['_TAILLOGSREQUEST']._serialized_end = 361