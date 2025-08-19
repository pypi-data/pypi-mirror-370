"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/spike_detector.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1eapi/nodes/spike_detector.proto\x12\x07synapse"&\n\x0fTemplateMatcher\x12\x13\n\x0btemplate_uV\x18\x01 \x03(\r"#\n\x0bThresholder\x12\x14\n\x0cthreshold_uV\x18\x01 \x01(\r"\x9d\x01\n\x13SpikeDetectorConfig\x12+\n\x0bthresholder\x18\x01 \x01(\x0b2\x14.synapse.ThresholderH\x00\x124\n\x10template_matcher\x18\x02 \x01(\x0b2\x18.synapse.TemplateMatcherH\x00\x12\x19\n\x11samples_per_spike\x18\x03 \x01(\rB\x08\n\x06configb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.spike_detector_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_TEMPLATEMATCHER']._serialized_start = 43
    _globals['_TEMPLATEMATCHER']._serialized_end = 81
    _globals['_THRESHOLDER']._serialized_start = 83
    _globals['_THRESHOLDER']._serialized_end = 118
    _globals['_SPIKEDETECTORCONFIG']._serialized_start = 121
    _globals['_SPIKEDETECTORCONFIG']._serialized_end = 278