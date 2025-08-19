"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/spike_source.proto')
_sym_db = _symbol_database.Default()
from ...api.nodes import signal_config_pb2 as api_dot_nodes_dot_signal__config__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1capi/nodes/spike_source.proto\x12\x07synapse\x1a\x1dapi/nodes/signal_config.proto"\xad\x01\n\x11SpikeSourceConfig\x12\x15\n\rperipheral_id\x18\x01 \x01(\r\x12\x16\n\x0esample_rate_hz\x18\x02 \x01(\r\x12\x17\n\x0fspike_window_ms\x18\x03 \x01(\x02\x12\x0c\n\x04gain\x18\x04 \x01(\x02\x12\x14\n\x0cthreshold_uV\x18\x05 \x01(\x02\x12,\n\nelectrodes\x18\x06 \x01(\x0b2\x18.synapse.ElectrodeConfigb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.spike_source_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_SPIKESOURCECONFIG']._serialized_start = 73
    _globals['_SPIKESOURCECONFIG']._serialized_end = 246