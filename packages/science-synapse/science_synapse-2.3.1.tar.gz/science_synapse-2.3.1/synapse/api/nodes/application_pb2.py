"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/application.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bapi/nodes/application.proto\x12\x07synapse\x1a\x1cgoogle/protobuf/struct.proto"\xb4\x01\n\x15ApplicationNodeConfig\x12\x0c\n\x04name\x18\x01 \x01(\t\x12B\n\nparameters\x18\x02 \x03(\x0b2..synapse.ApplicationNodeConfig.ParametersEntry\x1aI\n\x0fParametersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12%\n\x05value\x18\x02 \x01(\x0b2\x16.google.protobuf.Value:\x028\x01"J\n\x15ApplicationNodeStatus\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07running\x18\x02 \x01(\x08\x12\x12\n\nerror_logs\x18\x03 \x01(\tb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.application_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_APPLICATIONNODECONFIG_PARAMETERSENTRY']._loaded_options = None
    _globals['_APPLICATIONNODECONFIG_PARAMETERSENTRY']._serialized_options = b'8\x01'
    _globals['_APPLICATIONNODECONFIG']._serialized_start = 71
    _globals['_APPLICATIONNODECONFIG']._serialized_end = 251
    _globals['_APPLICATIONNODECONFIG_PARAMETERSENTRY']._serialized_start = 178
    _globals['_APPLICATIONNODECONFIG_PARAMETERSENTRY']._serialized_end = 251
    _globals['_APPLICATIONNODESTATUS']._serialized_start = 253
    _globals['_APPLICATIONNODESTATUS']._serialized_end = 327