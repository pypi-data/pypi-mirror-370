"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/nodes/disk_writer.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bapi/nodes/disk_writer.proto\x12\x07synapse"$\n\x10DiskWriterConfig\x12\x10\n\x08filename\x18\x01 \x01(\t"\x94\x01\n\x10DiskWriterStatus\x12\x13\n\x0boutput_path\x18\x01 \x01(\t\x12\x15\n\rbytes_written\x18\x02 \x01(\x04\x12\x12\n\nis_writing\x18\x03 \x01(\x08\x12"\n\x1aavailable_disk_space_bytes\x18\x04 \x01(\x04\x12\x1c\n\x14current_bitrate_mbps\x18\x05 \x01(\x02b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.nodes.disk_writer_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_DISKWRITERCONFIG']._serialized_start = 40
    _globals['_DISKWRITERCONFIG']._serialized_end = 76
    _globals['_DISKWRITERSTATUS']._serialized_start = 79
    _globals['_DISKWRITERSTATUS']._serialized_end = 227