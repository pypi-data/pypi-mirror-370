"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'experiment_overview.proto')
_sym_db = _symbol_database.Default()
from .templates import experiment_template_pb2 as templates_dot_experiment__template__pb2
from .templates import parameter_pb2 as templates_dot_parameter__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from . import ares_struct_pb2 as ares__struct__pb2
from . import analysis_overview_pb2 as analysis__overview__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19experiment_overview.proto\x12\x0eares.datamodel\x1a#templates/experiment_template.proto\x1a\x19templates/parameter.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x11ares_struct.proto\x1a\x17analysis_overview.proto"\x89\x02\n\x12ExperimentOverview\x12\x11\n\tunique_id\x18\x01 \x01(\t\x12>\n\x08template\x18\x02 \x01(\x0b2,.ares.datamodel.templates.ExperimentTemplate\x12*\n\x06result\x18\x03 \x01(\x0b2\x1a.ares.datamodel.AresStruct\x127\n\nparameters\x18\x04 \x03(\x0b2#.ares.datamodel.templates.Parameter\x12;\n\x11analysis_overview\x18\x05 \x01(\x0b2 .ares.datamodel.AnalysisOverviewb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'experiment_overview_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_EXPERIMENTOVERVIEW']._serialized_start = 186
    _globals['_EXPERIMENTOVERVIEW']._serialized_end = 451