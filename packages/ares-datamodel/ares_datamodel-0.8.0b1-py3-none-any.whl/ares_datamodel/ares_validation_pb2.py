"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_validation.proto')
_sym_db = _symbol_database.Default()
from .templates import campaign_template_pb2 as templates_dot_campaign__template__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from .templates import experiment_template_pb2 as templates_dot_experiment__template__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15ares_validation.proto\x12\rares.services\x1a!templates/campaign_template.proto\x1a\x1bgoogle/protobuf/empty.proto\x1a#templates/experiment_template.proto"{\n\x19AnalyzerValidationRequest\x12\x13\n\x0banalyzer_id\x18\x01 \x01(\t\x12I\n\x13experiment_template\x18\x02 \x01(\x0b2,.ares.datamodel.templates.ExperimentTemplate"7\n\x12ValidationResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x10\n\x08messages\x18\x02 \x03(\t2\xb9\x02\n\x0eAresValidation\x12e\n\x14ValidateFullCampaign\x12*.ares.datamodel.templates.CampaignTemplate\x1a!.ares.services.ValidationResponse\x12h\n\x19ValidateAnalyzerSelection\x12(.ares.services.AnalyzerValidationRequest\x1a!.ares.services.ValidationResponse\x12V\n\x19ValidateRegisteredDevices\x12\x16.google.protobuf.Empty\x1a!.ares.services.ValidationResponseb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_validation_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ANALYZERVALIDATIONREQUEST']._serialized_start = 141
    _globals['_ANALYZERVALIDATIONREQUEST']._serialized_end = 264
    _globals['_VALIDATIONRESPONSE']._serialized_start = 266
    _globals['_VALIDATIONRESPONSE']._serialized_end = 321
    _globals['_ARESVALIDATION']._serialized_start = 324
    _globals['_ARESVALIDATION']._serialized_end = 637