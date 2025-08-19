"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/signal_config.proto')
_sym_db = _symbol_database.Default()
from ...api import channel_pb2 as api_dot_channel__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dapi/nodes/signal_config.proto\x12\x07synapse\x1a\x11api/channel.proto"d\n\x0fElectrodeConfig\x12"\n\x08channels\x18\x01 \x03(\x0b2\x10.synapse.Channel\x12\x15\n\rlow_cutoff_hz\x18\x02 \x01(\x02\x12\x16\n\x0ehigh_cutoff_hz\x18\x03 \x01(\x02"!\n\x0bPixelConfig\x12\x12\n\npixel_mask\x18\x01 \x03(\r"s\n\x0cSignalConfig\x12-\n\telectrode\x18\x01 \x01(\x0b2\x18.synapse.ElectrodeConfigH\x00\x12%\n\x05pixel\x18\x02 \x01(\x0b2\x14.synapse.PixelConfigH\x00B\r\n\x0bsignal_typeb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.signal_config_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ELECTRODECONFIG']._serialized_start = 61
    _globals['_ELECTRODECONFIG']._serialized_end = 161
    _globals['_PIXELCONFIG']._serialized_start = 163
    _globals['_PIXELCONFIG']._serialized_end = 196
    _globals['_SIGNALCONFIG']._serialized_start = 198
    _globals['_SIGNALCONFIG']._serialized_end = 313