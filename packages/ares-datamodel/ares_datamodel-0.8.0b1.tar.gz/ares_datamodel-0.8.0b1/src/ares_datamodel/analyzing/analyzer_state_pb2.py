"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'analyzing/analyzer_state.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1eanalyzing/analyzer_state.proto\x12\x18ares.datamodel.analyzing*K\n\rAnalyzerState\x12\x15\n\x11UNSPECIFIED_STATE\x10\x00\x12\n\n\x06ACTIVE\x10\x01\x12\x0c\n\x08INACTIVE\x10\x02\x12\t\n\x05ERROR\x10\x03b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'analyzing.analyzer_state_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ANALYZERSTATE']._serialized_start = 60
    _globals['_ANALYZERSTATE']._serialized_end = 135