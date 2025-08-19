"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'analysis_overview.proto')
_sym_db = _symbol_database.Default()
from .analyzing import analyzer_info_pb2 as analyzing_dot_analyzer__info__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17analysis_overview.proto\x12\x0eares.datamodel\x1a\x1danalyzing/analyzer_info.proto"\x94\x01\n\x10AnalysisOverview\x12\x11\n\tunique_id\x18\x01 \x01(\t\x12\x1e\n\x16experiment_overview_id\x18\x02 \x01(\t\x12\x0e\n\x06result\x18\x03 \x01(\x01\x12=\n\ranalyzer_info\x18\x04 \x01(\x0b2&.ares.datamodel.analyzing.AnalyzerInfob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'analysis_overview_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ANALYSISOVERVIEW']._serialized_start = 75
    _globals['_ANALYSISOVERVIEW']._serialized_end = 223