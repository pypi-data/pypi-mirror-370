"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/device.proto')
_sym_db = _symbol_database.Default()
from ..api import node_pb2 as api_dot_node__pb2
from ..api import status_pb2 as api_dot_status__pb2
from ..api import time_pb2 as api_dot_time__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10api/device.proto\x12\x07synapse\x1a\x0eapi/node.proto\x1a\x10api/status.proto\x1a\x0eapi/time.proto"\xed\x01\n\nPeripheral\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06vendor\x18\x02 \x01(\t\x12\x15\n\rperipheral_id\x18\x03 \x01(\r\x12&\n\x04type\x18\x04 \x01(\x0e2\x18.synapse.Peripheral.Type\x12\x0f\n\x07address\x18\x05 \x01(\t"q\n\x04Type\x12\x0c\n\x08kUnknown\x10\x00\x12\x14\n\x10kBroadbandSource\x10\x01\x12\x1a\n\x16kElectricalStimulation\x10\x02\x12\x17\n\x13kOpticalStimulation\x10\x03\x12\x10\n\x0ckSpikeSource\x10\x04"\xdd\x01\n\nDeviceInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06serial\x18\x02 \x01(\t\x12\x17\n\x0fsynapse_version\x18\x03 \x01(\r\x12\x18\n\x10firmware_version\x18\x04 \x01(\r\x12\x1f\n\x06status\x18\x05 \x01(\x0b2\x0f.synapse.Status\x12(\n\x0bperipherals\x18\x06 \x03(\x0b2\x13.synapse.Peripheral\x123\n\rconfiguration\x18\x07 \x01(\x0b2\x1c.synapse.DeviceConfiguration"g\n\x13DeviceConfiguration\x12"\n\x05nodes\x18\x01 \x03(\x0b2\x13.synapse.NodeConfig\x12,\n\x0bconnections\x18\x02 \x03(\x0b2\x17.synapse.NodeConnection"H\n\x0eDeviceSettings\x12\x0c\n\x04name\x18\x01 \x01(\t\x12(\n\x0btime_source\x18\x02 \x01(\x0e2\x13.synapse.TimeSource"\x12\n\x10GetSettingsQuery"@\n\x13GetSettingsResponse\x12)\n\x08settings\x18\x01 \x01(\x0b2\x17.synapse.DeviceSettings"H\n\x1bUpdateDeviceSettingsRequest\x12)\n\x08settings\x18\x01 \x01(\x0b2\x17.synapse.DeviceSettings"r\n\x1cUpdateDeviceSettingsResponse\x12\x1f\n\x06status\x18\x01 \x01(\x0b2\x0f.synapse.Status\x121\n\x10updated_settings\x18\x02 \x01(\x0b2\x17.synapse.DeviceSettingsb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.device_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_PERIPHERAL']._serialized_start = 80
    _globals['_PERIPHERAL']._serialized_end = 317
    _globals['_PERIPHERAL_TYPE']._serialized_start = 204
    _globals['_PERIPHERAL_TYPE']._serialized_end = 317
    _globals['_DEVICEINFO']._serialized_start = 320
    _globals['_DEVICEINFO']._serialized_end = 541
    _globals['_DEVICECONFIGURATION']._serialized_start = 543
    _globals['_DEVICECONFIGURATION']._serialized_end = 646
    _globals['_DEVICESETTINGS']._serialized_start = 648
    _globals['_DEVICESETTINGS']._serialized_end = 720
    _globals['_GETSETTINGSQUERY']._serialized_start = 722
    _globals['_GETSETTINGSQUERY']._serialized_end = 740
    _globals['_GETSETTINGSRESPONSE']._serialized_start = 742
    _globals['_GETSETTINGSRESPONSE']._serialized_end = 806
    _globals['_UPDATEDEVICESETTINGSREQUEST']._serialized_start = 808
    _globals['_UPDATEDEVICESETTINGSREQUEST']._serialized_end = 880
    _globals['_UPDATEDEVICESETTINGSRESPONSE']._serialized_start = 882
    _globals['_UPDATEDEVICESETTINGSRESPONSE']._serialized_end = 996