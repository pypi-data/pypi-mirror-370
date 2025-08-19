"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/channel.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11api/channel.proto\x12\x07synapse"e\n\x07Channel\x12\n\n\x02id\x18\x01 \x01(\r\x12\x14\n\x0celectrode_id\x18\x02 \x01(\r\x12\x14\n\x0creference_id\x18\x03 \x01(\r\x12"\n\x04type\x18\x04 \x01(\x0e2\x14.synapse.ChannelType"V\n\x0cChannelRange\x12"\n\x04type\x18\x01 \x01(\x0e2\x14.synapse.ChannelType\x12\r\n\x05count\x18\x02 \x01(\r\x12\x13\n\x0bchannel_ids\x18\x03 \x03(\r*&\n\x0bChannelType\x12\r\n\tELECTRODE\x10\x00\x12\x08\n\x04GPIO\x10\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.channel_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_CHANNELTYPE']._serialized_start = 221
    _globals['_CHANNELTYPE']._serialized_end = 259
    _globals['_CHANNEL']._serialized_start = 30
    _globals['_CHANNEL']._serialized_end = 131
    _globals['_CHANNELRANGE']._serialized_start = 133
    _globals['_CHANNELRANGE']._serialized_end = 219