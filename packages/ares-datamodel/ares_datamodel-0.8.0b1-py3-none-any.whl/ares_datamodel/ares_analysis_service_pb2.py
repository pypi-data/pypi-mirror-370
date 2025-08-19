"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_analysis_service.proto')
_sym_db = _symbol_database.Default()
from . import validation_result_pb2 as validation__result__pb2
from .analyzing import analysis_pb2 as analyzing_dot_analysis__pb2
from . import ares_struct_pb2 as ares__struct__pb2
from . import ares_data_schema_pb2 as ares__data__schema__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bares_analysis_service.proto\x12\rares.services\x1a\x17validation_result.proto\x1a\x18analyzing/analysis.proto\x1a\x11ares_struct.proto\x1a\x16ares_data_schema.proto"\x80\x01\n\x0fAnalysisRequest\x12\x13\n\x0banalyzer_id\x18\x01 \x01(\t\x12*\n\x06inputs\x18\x02 \x01(\x0b2\x1a.ares.datamodel.AresStruct\x12,\n\x08settings\x18\x03 \x01(\x0b2\x1a.ares.datamodel.AresStruct"m\n\x16InputValidationRequest\x12\x13\n\x0banalyzer_id\x18\x01 \x01(\t\x12>\n\x0cinput_schema\x18\x02 \x01(\x0b2(.ares.datamodel.AresDataSchemaSimplified"0\n\x19AnalyzerParametersRequest\x12\x13\n\x0banalyzer_id\x18\x01 \x01(\t"U\n\x1aAnalyzerParametersResponse\x127\n\x0fanalysis_schema\x18\x01 \x01(\x0b2\x1e.ares.datamodel.AresDataSchema2\xad\x02\n\x13AresAnalysisService\x12Y\n\x0eValidateInputs\x12%.ares.services.InputValidationRequest\x1a .ares.datamodel.ValidationResult\x12M\n\x07Analyze\x12\x1e.ares.services.AnalysisRequest\x1a".ares.datamodel.analyzing.Analysis\x12l\n\x15GetAnalyzerParameters\x12(.ares.services.AnalyzerParametersRequest\x1a).ares.services.AnalyzerParametersResponseb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_analysis_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ANALYSISREQUEST']._serialized_start = 141
    _globals['_ANALYSISREQUEST']._serialized_end = 269
    _globals['_INPUTVALIDATIONREQUEST']._serialized_start = 271
    _globals['_INPUTVALIDATIONREQUEST']._serialized_end = 380
    _globals['_ANALYZERPARAMETERSREQUEST']._serialized_start = 382
    _globals['_ANALYZERPARAMETERSREQUEST']._serialized_end = 430
    _globals['_ANALYZERPARAMETERSRESPONSE']._serialized_start = 432
    _globals['_ANALYZERPARAMETERSRESPONSE']._serialized_end = 517
    _globals['_ARESANALYSISSERVICE']._serialized_start = 520
    _globals['_ARESANALYSISSERVICE']._serialized_end = 821