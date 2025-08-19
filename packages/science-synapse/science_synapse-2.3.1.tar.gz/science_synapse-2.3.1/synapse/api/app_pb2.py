"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/app.proto')
_sym_db = _symbol_database.Default()
from ..api import status_pb2 as api_dot_status__pb2
from ..api import performance_pb2 as api_dot_performance__pb2
from ..api import device_pb2 as api_dot_device__pb2
from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rapi/app.proto\x12\x07synapse\x1a\x10api/status.proto\x1a\x15api/performance.proto\x1a\x10api/device.proto\x1a\x1cgoogle/protobuf/struct.proto"\x80\x01\n\x0bAppManifest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12.\n\rconfig_schema\x18\x02 \x01(\x0b2\x17.google.protobuf.Struct\x123\n\rdevice_config\x18\x03 \x01(\x0b2\x1c.synapse.DeviceConfiguration"R\n\x0fPackageMetadata\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\x12\x0c\n\x04size\x18\x03 \x01(\x04\x12\x12\n\nsha256_sum\x18\x04 \x01(\t"]\n\x0fAppPackageChunk\x12,\n\x08metadata\x18\x01 \x01(\x0b2\x18.synapse.PackageMetadataH\x00\x12\x14\n\nfile_chunk\x18\x02 \x01(\x0cH\x00B\x06\n\x04data"I\n\x11AppDeployResponse\x12#\n\x06status\x18\x01 \x01(\x0e2\x13.synapse.StatusCode\x12\x0f\n\x07message\x18\x02 \x01(\t"b\n\x15AppPerformanceSummary\x12\x14\n\x0ctimestamp_ns\x18\x01 \x01(\x04\x123\n\x11function_profiles\x18\x02 \x03(\x0b2\x18.synapse.FunctionProfileb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.app_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_APPMANIFEST']._serialized_start = 116
    _globals['_APPMANIFEST']._serialized_end = 244
    _globals['_PACKAGEMETADATA']._serialized_start = 246
    _globals['_PACKAGEMETADATA']._serialized_end = 328
    _globals['_APPPACKAGECHUNK']._serialized_start = 330
    _globals['_APPPACKAGECHUNK']._serialized_end = 423
    _globals['_APPDEPLOYRESPONSE']._serialized_start = 425
    _globals['_APPDEPLOYRESPONSE']._serialized_end = 498
    _globals['_APPPERFORMANCESUMMARY']._serialized_start = 500
    _globals['_APPPERFORMANCESUMMARY']._serialized_end = 598