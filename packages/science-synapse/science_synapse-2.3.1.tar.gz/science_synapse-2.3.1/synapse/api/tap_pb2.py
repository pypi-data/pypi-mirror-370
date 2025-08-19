"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/tap.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rapi/tap.proto\x12\x07synapse"i\n\rTapConnection\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08endpoint\x18\x02 \x01(\t\x12\x14\n\x0cmessage_type\x18\x03 \x01(\t\x12"\n\x08tap_type\x18\x04 \x01(\x0e2\x10.synapse.TapType"\x0f\n\rListTapsQuery"8\n\x10ListTapsResponse\x12$\n\x04taps\x18\x01 \x03(\x0b2\x16.synapse.TapConnection*Q\n\x07TapType\x12\x18\n\x14TAP_TYPE_UNSPECIFIED\x10\x00\x12\x15\n\x11TAP_TYPE_PRODUCER\x10\x01\x12\x15\n\x11TAP_TYPE_CONSUMER\x10\x02b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.tap_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_TAPTYPE']._serialized_start = 208
    _globals['_TAPTYPE']._serialized_end = 289
    _globals['_TAPCONNECTION']._serialized_start = 26
    _globals['_TAPCONNECTION']._serialized_end = 131
    _globals['_LISTTAPSQUERY']._serialized_start = 133
    _globals['_LISTTAPSQUERY']._serialized_end = 148
    _globals['_LISTTAPSRESPONSE']._serialized_start = 150
    _globals['_LISTTAPSRESPONSE']._serialized_end = 206