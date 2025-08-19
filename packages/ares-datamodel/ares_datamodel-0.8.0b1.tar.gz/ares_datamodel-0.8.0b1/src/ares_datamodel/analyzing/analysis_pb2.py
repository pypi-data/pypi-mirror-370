"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'analyzing/analysis.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18analyzing/analysis.proto\x12\x18ares.datamodel.analyzing\x1a\x1egoogle/protobuf/wrappers.proto"W\n\x08Analysis\x12\x0e\n\x06result\x18\x01 \x01(\x02\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12\x19\n\x0cerror_string\x18\x03 \x01(\tH\x00\x88\x01\x01B\x0f\n\r_error_stringb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'analyzing.analysis_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ANALYSIS']._serialized_start = 86
    _globals['_ANALYSIS']._serialized_end = 173