"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/spectral_filter.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fapi/nodes/spectral_filter.proto\x12\x07synapse"t\n\x14SpectralFilterConfig\x12-\n\x06method\x18\x01 \x01(\x0e2\x1d.synapse.SpectralFilterMethod\x12\x15\n\rlow_cutoff_hz\x18\x02 \x01(\x02\x12\x16\n\x0ehigh_cutoff_hz\x18\x03 \x01(\x02*m\n\x14SpectralFilterMethod\x12\x1a\n\x16kSpectralFilterUnknown\x10\x00\x12\x0c\n\x08kLowPass\x10\x01\x12\r\n\tkHighPass\x10\x02\x12\r\n\tkBandPass\x10\x03\x12\r\n\tkBandStop\x10\x04b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.spectral_filter_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_SPECTRALFILTERMETHOD']._serialized_start = 162
    _globals['_SPECTRALFILTERMETHOD']._serialized_end = 271
    _globals['_SPECTRALFILTERCONFIG']._serialized_start = 44
    _globals['_SPECTRALFILTERCONFIG']._serialized_end = 160