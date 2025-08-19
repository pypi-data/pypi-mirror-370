"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'templates/experiment_template.proto')
_sym_db = _symbol_database.Default()
from ..templates import step_template_pb2 as templates_dot_step__template__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#templates/experiment_template.proto\x12\x18ares.datamodel.templates\x1a\x1dtemplates/step_template.proto"\xbd\x02\n\x12ExperimentTemplate\x12\x11\n\tunique_id\x18\x01 \x01(\t\x12>\n\x0estep_templates\x18\x02 \x03(\x0b2&.ares.datamodel.templates.StepTemplate\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x18\n\x0banalyzer_id\x18\x04 \x01(\tH\x00\x88\x01\x01\x12U\n\ranalyzer_maps\x18\x05 \x03(\x0b2>.ares.datamodel.templates.ExperimentTemplate.AnalyzerMapsEntry\x12\x10\n\x08resolved\x18\x06 \x01(\x08\x1a3\n\x11AnalyzerMapsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x028\x01B\x0e\n\x0c_analyzer_idb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'templates.experiment_template_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_EXPERIMENTTEMPLATE_ANALYZERMAPSENTRY']._loaded_options = None
    _globals['_EXPERIMENTTEMPLATE_ANALYZERMAPSENTRY']._serialized_options = b'8\x01'
    _globals['_EXPERIMENTTEMPLATE']._serialized_start = 97
    _globals['_EXPERIMENTTEMPLATE']._serialized_end = 414
    _globals['_EXPERIMENTTEMPLATE_ANALYZERMAPSENTRY']._serialized_start = 347
    _globals['_EXPERIMENTTEMPLATE_ANALYZERMAPSENTRY']._serialized_end = 398