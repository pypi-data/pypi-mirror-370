"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/signal_status.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dapi/nodes/signal_status.proto\x12\x07synapse"!\n\x0fElectrodeStatus\x12\x0e\n\x06lsb_uV\x18\x01 \x01(\x02"\r\n\x0bPixelStatus"s\n\x0cSignalStatus\x12-\n\telectrode\x18\x01 \x01(\x0b2\x18.synapse.ElectrodeStatusH\x00\x12%\n\x05pixel\x18\x02 \x01(\x0b2\x14.synapse.PixelStatusH\x00B\r\n\x0bsignal_typeb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.signal_status_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ELECTRODESTATUS']._serialized_start = 42
    _globals['_ELECTRODESTATUS']._serialized_end = 75
    _globals['_PIXELSTATUS']._serialized_start = 77
    _globals['_PIXELSTATUS']._serialized_end = 90
    _globals['_SIGNALSTATUS']._serialized_start = 92
    _globals['_SIGNALSTATUS']._serialized_end = 207