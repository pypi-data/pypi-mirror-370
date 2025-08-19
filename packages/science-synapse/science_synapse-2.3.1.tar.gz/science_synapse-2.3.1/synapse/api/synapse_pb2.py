"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/synapse.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from ..api import query_pb2 as api_dot_query__pb2
from ..api import status_pb2 as api_dot_status__pb2
from ..api import files_pb2 as api_dot_files__pb2
from ..api import logging_pb2 as api_dot_logging__pb2
from ..api import app_pb2 as api_dot_app__pb2
from ..api import device_pb2 as api_dot_device__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11api/synapse.proto\x12\x07synapse\x1a\x1bgoogle/protobuf/empty.proto\x1a\x0fapi/query.proto\x1a\x10api/status.proto\x1a\x0fapi/files.proto\x1a\x11api/logging.proto\x1a\rapi/app.proto\x1a\x10api/device.proto2\xb9\x07\n\rSynapseDevice\x125\n\x04Info\x12\x16.google.protobuf.Empty\x1a\x13.synapse.DeviceInfo"\x00\x12<\n\tConfigure\x12\x1c.synapse.DeviceConfiguration\x1a\x0f.synapse.Status"\x00\x122\n\x05Start\x12\x16.google.protobuf.Empty\x1a\x0f.synapse.Status"\x00\x121\n\x04Stop\x12\x16.google.protobuf.Empty\x1a\x0f.synapse.Status"\x00\x128\n\x05Query\x12\x15.synapse.QueryRequest\x1a\x16.synapse.QueryResponse"\x00\x12L\n\x0bStreamQuery\x12\x1b.synapse.StreamQueryRequest\x1a\x1c.synapse.StreamQueryResponse"\x000\x01\x12G\n\tDeployApp\x12\x18.synapse.AppPackageChunk\x1a\x1a.synapse.AppDeployResponse"\x00(\x010\x01\x12A\n\tListFiles\x12\x16.google.protobuf.Empty\x1a\x1a.synapse.ListFilesResponse"\x00\x12D\n\tWriteFile\x12\x19.synapse.WriteFileRequest\x1a\x1a.synapse.WriteFileResponse"\x00\x12C\n\x08ReadFile\x12\x18.synapse.ReadFileRequest\x1a\x19.synapse.ReadFileResponse"\x000\x01\x12G\n\nDeleteFile\x12\x1a.synapse.DeleteFileRequest\x1a\x1b.synapse.DeleteFileResponse"\x00\x12@\n\x07GetLogs\x12\x18.synapse.LogQueryRequest\x1a\x19.synapse.LogQueryResponse"\x00\x12;\n\x08TailLogs\x12\x18.synapse.TailLogsRequest\x1a\x11.synapse.LogEntry"\x000\x01\x12e\n\x14UpdateDeviceSettings\x12$.synapse.UpdateDeviceSettingsRequest\x1a%.synapse.UpdateDeviceSettingsResponse"\x00b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.synapse_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_SYNAPSEDEVICE']._serialized_start = 164
    _globals['_SYNAPSEDEVICE']._serialized_end = 1117