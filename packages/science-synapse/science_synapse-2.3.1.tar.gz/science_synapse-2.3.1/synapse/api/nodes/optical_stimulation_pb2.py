"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/optical_stimulation.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#api/nodes/optical_stimulation.proto\x12\x07synapse"\x91\x01\n\x18OpticalStimulationConfig\x12\x15\n\rperipheral_id\x18\x01 \x01(\r\x12\x12\n\npixel_mask\x18\x02 \x03(\r\x12\x11\n\tbit_width\x18\x03 \x01(\r\x12\x12\n\nframe_rate\x18\x04 \x01(\r\x12\x0c\n\x04gain\x18\x05 \x01(\x02\x12\x15\n\rsend_receipts\x18\x06 \x01(\x08"\x9a\x01\n\x10OpticalStimFrame\x12\x10\n\x08frame_id\x18\x01 \x01(\x04\x12\x17\n\x0fsequence_number\x18\x02 \x01(\x04\x12\x14\n\x0ctimestamp_ns\x18\x03 \x01(\x04\x12\x0c\n\x04rows\x18\x04 \x01(\r\x12\x0f\n\x07columns\x18\x05 \x01(\r\x12\x11\n\tintensity\x18\x06 \x03(\x02\x12\x13\n\x0bduration_us\x18\x07 \x01(\x04"2\n\x18OpticalStimulationStatus\x12\x16\n\x0eframes_written\x18\x01 \x01(\x04b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.optical_stimulation_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_OPTICALSTIMULATIONCONFIG']._serialized_start = 49
    _globals['_OPTICALSTIMULATIONCONFIG']._serialized_end = 194
    _globals['_OPTICALSTIMFRAME']._serialized_start = 197
    _globals['_OPTICALSTIMFRAME']._serialized_end = 351
    _globals['_OPTICALSTIMULATIONSTATUS']._serialized_start = 353
    _globals['_OPTICALSTIMULATIONSTATUS']._serialized_end = 403