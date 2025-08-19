"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'analyzing/analyzer_capabilities.proto')
_sym_db = _symbol_database.Default()
from .. import ares_data_schema_pb2 as ares__data__schema__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n%analyzing/analyzer_capabilities.proto\x12\x18ares.datamodel.analyzing\x1a\x16ares_data_schema.proto"h\n\x14AnalyzerCapabilities\x12\x17\n\x0ftimeout_seconds\x18\x01 \x01(\x03\x127\n\x0fsettings_schema\x18\x02 \x01(\x0b2\x1e.ares.datamodel.AresDataSchemab\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'analyzing.analyzer_capabilities_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ANALYZERCAPABILITIES']._serialized_start = 91
    _globals['_ANALYZERCAPABILITIES']._serialized_end = 195