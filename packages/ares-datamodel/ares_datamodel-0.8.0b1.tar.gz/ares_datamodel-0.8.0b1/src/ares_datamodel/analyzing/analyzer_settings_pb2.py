"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'analyzing/analyzer_settings.proto')
_sym_db = _symbol_database.Default()
from .. import ares_struct_pb2 as ares__struct__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n!analyzing/analyzer_settings.proto\x12\x18ares.datamodel.analyzing\x1a\x11ares_struct.proto"U\n\x10AnalyzerSettings\x12\x13\n\x0banalyzer_id\x18\x01 \x01(\t\x12,\n\x08settings\x18\x02 \x01(\x0b2\x1a.ares.datamodel.AresStructb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'analyzing.analyzer_settings_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ANALYZERSETTINGS']._serialized_start = 82
    _globals['_ANALYZERSETTINGS']._serialized_end = 167