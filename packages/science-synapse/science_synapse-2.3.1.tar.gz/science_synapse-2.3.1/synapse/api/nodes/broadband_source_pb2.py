"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/broadband_source.proto')
_sym_db = _symbol_database.Default()
from ...api.nodes import signal_config_pb2 as api_dot_nodes_dot_signal__config__pb2
from ...api.nodes import signal_status_pb2 as api_dot_nodes_dot_signal__status__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n api/nodes/broadband_source.proto\x12\x07synapse\x1a\x1dapi/nodes/signal_config.proto\x1a\x1dapi/nodes/signal_status.proto"\x8e\x01\n\x15BroadbandSourceConfig\x12\x15\n\rperipheral_id\x18\x01 \x01(\r\x12\x11\n\tbit_width\x18\x02 \x01(\r\x12\x16\n\x0esample_rate_hz\x18\x03 \x01(\r\x12\x0c\n\x04gain\x18\x04 \x01(\x02\x12%\n\x06signal\x18\x05 \x01(\x0b2\x15.synapse.SignalConfig">\n\x15BroadbandSourceStatus\x12%\n\x06status\x18\x01 \x01(\x0b2\x15.synapse.SignalStatusb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.broadband_source_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_BROADBANDSOURCECONFIG']._serialized_start = 108
    _globals['_BROADBANDSOURCECONFIG']._serialized_end = 250
    _globals['_BROADBANDSOURCESTATUS']._serialized_start = 252
    _globals['_BROADBANDSOURCESTATUS']._serialized_end = 314