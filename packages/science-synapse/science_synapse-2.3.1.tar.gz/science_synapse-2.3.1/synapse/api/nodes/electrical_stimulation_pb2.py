"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/electrical_stimulation.proto')
_sym_db = _symbol_database.Default()
from ...api import channel_pb2 as api_dot_channel__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n&api/nodes/electrical_stimulation.proto\x12\x07synapse\x1a\x11api/channel.proto"\x8d\x01\n\x1bElectricalStimulationConfig\x12\x15\n\rperipheral_id\x18\x01 \x01(\r\x12"\n\x08channels\x18\x02 \x03(\x0b2\x10.synapse.Channel\x12\x11\n\tbit_width\x18\x03 \x01(\r\x12\x13\n\x0bsample_rate\x18\x04 \x01(\r\x12\x0b\n\x03lsb\x18\x05 \x01(\r"-\n\x1bElectricalStimulationStatus\x12\x0e\n\x06lsb_uV\x18\x01 \x01(\x02b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.electrical_stimulation_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ELECTRICALSTIMULATIONCONFIG']._serialized_start = 71
    _globals['_ELECTRICALSTIMULATIONCONFIG']._serialized_end = 212
    _globals['_ELECTRICALSTIMULATIONSTATUS']._serialized_start = 214
    _globals['_ELECTRICALSTIMULATIONSTATUS']._serialized_end = 259