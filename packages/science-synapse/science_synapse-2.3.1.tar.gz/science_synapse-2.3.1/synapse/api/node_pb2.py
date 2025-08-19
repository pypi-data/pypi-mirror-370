"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/node.proto')
_sym_db = _symbol_database.Default()
from ..api.nodes import broadband_source_pb2 as api_dot_nodes_dot_broadband__source__pb2
from ..api.nodes import electrical_stimulation_pb2 as api_dot_nodes_dot_electrical__stimulation__pb2
from ..api.nodes import optical_stimulation_pb2 as api_dot_nodes_dot_optical__stimulation__pb2
from ..api.nodes import spike_detector_pb2 as api_dot_nodes_dot_spike__detector__pb2
from ..api.nodes import spectral_filter_pb2 as api_dot_nodes_dot_spectral__filter__pb2
from ..api.nodes import disk_writer_pb2 as api_dot_nodes_dot_disk__writer__pb2
from ..api.nodes import spike_source_pb2 as api_dot_nodes_dot_spike__source__pb2
from ..api.nodes import spike_binner_pb2 as api_dot_nodes_dot_spike__binner__pb2
from ..api.nodes import application_pb2 as api_dot_nodes_dot_application__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eapi/node.proto\x12\x07synapse\x1a api/nodes/broadband_source.proto\x1a&api/nodes/electrical_stimulation.proto\x1a#api/nodes/optical_stimulation.proto\x1a\x1eapi/nodes/spike_detector.proto\x1a\x1fapi/nodes/spectral_filter.proto\x1a\x1bapi/nodes/disk_writer.proto\x1a\x1capi/nodes/spike_source.proto\x1a\x1capi/nodes/spike_binner.proto\x1a\x1bapi/nodes/application.proto"\xd8\x04\n\nNodeConfig\x12\x1f\n\x04type\x18\x01 \x01(\x0e2\x11.synapse.NodeType\x12\n\n\x02id\x18\x02 \x01(\r\x12:\n\x10broadband_source\x18\x05 \x01(\x0b2\x1e.synapse.BroadbandSourceConfigH\x00\x12F\n\x16electrical_stimulation\x18\x06 \x01(\x0b2$.synapse.ElectricalStimulationConfigH\x00\x12@\n\x13optical_stimulation\x18\x08 \x01(\x0b2!.synapse.OpticalStimulationConfigH\x00\x126\n\x0espike_detector\x18\t \x01(\x0b2\x1c.synapse.SpikeDetectorConfigH\x00\x128\n\x0fspectral_filter\x18\n \x01(\x0b2\x1d.synapse.SpectralFilterConfigH\x00\x120\n\x0bdisk_writer\x18\x0b \x01(\x0b2\x19.synapse.DiskWriterConfigH\x00\x122\n\x0cspike_source\x18\x0c \x01(\x0b2\x1a.synapse.SpikeSourceConfigH\x00\x122\n\x0cspike_binner\x18\r \x01(\x0b2\x1a.synapse.SpikeBinnerConfigH\x00\x125\n\x0bapplication\x18\x0e \x01(\x0b2\x1e.synapse.ApplicationNodeConfigH\x00B\x08\n\x06configJ\x04\x08\x03\x10\x04J\x04\x08\x04\x10\x05"\xfe\x02\n\nNodeStatus\x12\x1f\n\x04type\x18\x01 \x01(\x0e2\x11.synapse.NodeType\x12\n\n\x02id\x18\x02 \x01(\r\x12:\n\x10broadband_source\x18\x04 \x01(\x0b2\x1e.synapse.BroadbandSourceStatusH\x00\x12F\n\x16electrical_stimulation\x18\x06 \x01(\x0b2$.synapse.ElectricalStimulationStatusH\x00\x125\n\x0bapplication\x18\x07 \x01(\x0b2\x1e.synapse.ApplicationNodeStatusH\x00\x12@\n\x13optical_stimulation\x18\x08 \x01(\x0b2!.synapse.OpticalStimulationStatusH\x00\x120\n\x0bdisk_writer\x18\n \x01(\x0b2\x19.synapse.DiskWriterStatusH\x00B\x08\n\x06statusJ\x04\x08\x03\x10\x04J\x04\x08\x05\x10\x06":\n\x0eNodeConnection\x12\x13\n\x0bsrc_node_id\x18\x01 \x01(\r\x12\x13\n\x0bdst_node_id\x18\x02 \x01(\r*\xe7\x01\n\x08NodeType\x12\x14\n\x10kNodeTypeUnknown\x10\x00\x12\x14\n\x10kBroadbandSource\x10\x03\x12\x1a\n\x16kElectricalStimulation\x10\x04\x12\x17\n\x13kOpticalStimulation\x10\x05\x12\x12\n\x0ekSpikeDetector\x10\x06\x12\x10\n\x0ckSpikeSource\x10\x07\x12\x13\n\x0fkSpectralFilter\x10\x08\x12\x0f\n\x0bkDiskWriter\x10\t\x12\x10\n\x0ckSpikeBinner\x10\n\x12\x10\n\x0ckApplication\x10\x0b"\x04\x08\x01\x10\x01"\x04\x08\x02\x10\x02b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.node_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_NODETYPE']._serialized_start = 1370
    _globals['_NODETYPE']._serialized_end = 1601
    _globals['_NODECONFIG']._serialized_start = 322
    _globals['_NODECONFIG']._serialized_end = 922
    _globals['_NODESTATUS']._serialized_start = 925
    _globals['_NODESTATUS']._serialized_end = 1307
    _globals['_NODECONNECTION']._serialized_start = 1309
    _globals['_NODECONNECTION']._serialized_end = 1367