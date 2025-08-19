"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'analyzing/analyzer_info.proto')
_sym_db = _symbol_database.Default()
from ..analyzing import analyzer_capabilities_pb2 as analyzing_dot_analyzer__capabilities__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1danalyzing/analyzer_info.proto\x12\x18ares.datamodel.analyzing\x1a%analyzing/analyzer_capabilities.proto"\xd8\x01\n\x0cAnalyzerInfo\x12\x11\n\tunique_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04type\x18\x03 \x01(\t\x12\x18\n\x0bdescription\x18\x04 \x01(\tH\x00\x88\x01\x01\x12\x0f\n\x07version\x18\x05 \x01(\t\x12D\n\x0ccapabilities\x18\x06 \x01(\x0b2..ares.datamodel.analyzing.AnalyzerCapabilities\x12\x10\n\x03url\x18\x07 \x01(\tH\x01\x88\x01\x01B\x0e\n\x0c_descriptionB\x06\n\x04_urlb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'analyzing.analyzer_info_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ANALYZERINFO']._serialized_start = 99
    _globals['_ANALYZERINFO']._serialized_end = 315