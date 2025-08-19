"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 29, 0, '', 'api/files.proto')
_sym_db = _symbol_database.Default()
from ..api import status_pb2 as api_dot_status__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fapi/files.proto\x12\x07synapse\x1a\x10api/status.proto"\x98\x01\n\x11ListFilesResponse\x12.\n\x05files\x18\x01 \x03(\x0b2\x1f.synapse.ListFilesResponse.File\x1aS\n\x04File\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04size\x18\x02 \x01(\r\x12\x0f\n\x07created\x18\x03 \x01(\r\x12\x10\n\x08modified\x18\x04 \x01(\r\x12\x0c\n\x04type\x18\x05 \x01(\t".\n\x10WriteFileRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04data\x18\x02 \x01(\x0c"8\n\x11WriteFileResponse\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x15\n\rbytes_written\x18\x02 \x01(\x04"\x1f\n\x0fReadFileRequest\x12\x0c\n\x04name\x18\x01 \x01(\t"_\n\x10ReadFileResponse\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04data\x18\x02 \x01(\x0c\x12\x14\n\x0cstart_offset\x18\x03 \x01(\r\x12\x19\n\x11file_total_length\x18\x04 \x01(\r"!\n\x11DeleteFileRequest\x12\x0c\n\x04name\x18\x01 \x01(\t"L\n\x12DeleteFileResponse\x12\x0c\n\x04name\x18\x01 \x01(\t\x12(\n\x0bstatus_code\x18\x02 \x01(\x0e2\x13.synapse.StatusCodeb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.files_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_LISTFILESRESPONSE']._serialized_start = 47
    _globals['_LISTFILESRESPONSE']._serialized_end = 199
    _globals['_LISTFILESRESPONSE_FILE']._serialized_start = 116
    _globals['_LISTFILESRESPONSE_FILE']._serialized_end = 199
    _globals['_WRITEFILEREQUEST']._serialized_start = 201
    _globals['_WRITEFILEREQUEST']._serialized_end = 247
    _globals['_WRITEFILERESPONSE']._serialized_start = 249
    _globals['_WRITEFILERESPONSE']._serialized_end = 305
    _globals['_READFILEREQUEST']._serialized_start = 307
    _globals['_READFILEREQUEST']._serialized_end = 338
    _globals['_READFILERESPONSE']._serialized_start = 340
    _globals['_READFILERESPONSE']._serialized_end = 435
    _globals['_DELETEFILEREQUEST']._serialized_start = 437
    _globals['_DELETEFILEREQUEST']._serialized_end = 470
    _globals['_DELETEFILERESPONSE']._serialized_start = 472
    _globals['_DELETEFILERESPONSE']._serialized_end = 548