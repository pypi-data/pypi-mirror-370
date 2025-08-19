"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/status.proto')
_sym_db = _symbol_database.Default()
from ..api import node_pb2 as api_dot_node__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10api/status.proto\x12\x07synapse\x1a\x0eapi/node.proto"2\n\rDeviceStorage\x12\x10\n\x08total_gb\x18\x01 \x01(\x02\x12\x0f\n\x07used_gb\x18\x02 \x01(\x02"A\n\x0bDevicePower\x12\x1d\n\x15battery_level_percent\x18\x01 \x01(\x02\x12\x13\n\x0bis_charging\x18\x02 \x01(\x08"7\n\x11SignalChainStatus\x12"\n\x05nodes\x18\x01 \x03(\x0b2\x13.synapse.NodeStatus"\xff\x01\n\x06Status\x12\x0f\n\x07message\x18\x01 \x01(\t\x12!\n\x04code\x18\x02 \x01(\x0e2\x13.synapse.StatusCode\x12#\n\x05state\x18\x03 \x01(\x0e2\x14.synapse.DeviceState\x12#\n\x05power\x18\x05 \x01(\x0b2\x14.synapse.DevicePower\x12\'\n\x07storage\x18\x06 \x01(\x0b2\x16.synapse.DeviceStorage\x120\n\x0csignal_chain\x18\x07 \x01(\x0b2\x1a.synapse.SignalChainStatus\x12\x16\n\x0etime_sync_port\x18\x08 \x01(\rJ\x04\x08\x04\x10\x05*\xaf\x01\n\nStatusCode\x12\x07\n\x03kOk\x10\x00\x12\x13\n\x0fkUndefinedError\x10\x01\x12\x19\n\x15kInvalidConfiguration\x10\x02\x12\x17\n\x13kFailedPrecondition\x10\x03\x12\x12\n\x0ekUnimplemented\x10\x04\x12\x12\n\x0ekInternalError\x10\x05\x12\x15\n\x11kPermissionDenied\x10\x06\x12\x10\n\x0ckQueryFailed\x10\x07*V\n\x0bDeviceState\x12\x0c\n\x08kUnknown\x10\x00\x12\x11\n\rkInitializing\x10\x01\x12\x0c\n\x08kStopped\x10\x02\x12\x0c\n\x08kRunning\x10\x03\x12\n\n\x06kError\x10\x04b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.status_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_STATUSCODE']._serialized_start = 480
    _globals['_STATUSCODE']._serialized_end = 655
    _globals['_DEVICESTATE']._serialized_start = 657
    _globals['_DEVICESTATE']._serialized_end = 743
    _globals['_DEVICESTORAGE']._serialized_start = 45
    _globals['_DEVICESTORAGE']._serialized_end = 95
    _globals['_DEVICEPOWER']._serialized_start = 97
    _globals['_DEVICEPOWER']._serialized_end = 162
    _globals['_SIGNALCHAINSTATUS']._serialized_start = 164
    _globals['_SIGNALCHAINSTATUS']._serialized_end = 219
    _globals['_STATUS']._serialized_start = 222
    _globals['_STATUS']._serialized_end = 477