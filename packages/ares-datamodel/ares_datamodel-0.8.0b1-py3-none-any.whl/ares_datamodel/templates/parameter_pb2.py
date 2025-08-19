"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'templates/parameter.proto')
_sym_db = _symbol_database.Default()
from ..templates import parameter_metadata_pb2 as templates_dot_parameter__metadata__pb2
from ..templates import variable_allocation_pb2 as templates_dot_variable__allocation__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from .. import ares_struct_pb2 as ares__struct__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19templates/parameter.proto\x12\x18ares.datamodel.templates\x1a"templates/parameter_metadata.proto\x1a#templates/variable_allocation.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x11ares_struct.proto"\xe4\x02\n\tParameter\x12\x11\n\tunique_id\x18\x01 \x01(\t\x12=\n\x08metadata\x18\x02 \x01(\x0b2+.ares.datamodel.templates.ParameterMetadata\x12(\n\x05value\x18\x03 \x01(\x0b2\x19.ares.datamodel.AresValue\x12\x0f\n\x07planned\x18\x04 \x01(\x08\x12\x19\n\x11environment_based\x18\x05 \x01(\x08\x12F\n\x11planning_metadata\x18\x06 \x01(\x0b2+.ares.datamodel.templates.ParameterMetadata\x12=\n\rvariable_type\x18\x07 \x01(\x0e2&.ares.datamodel.templates.VariableType\x12\x19\n\x11variable_argument\x18\x08 \x01(\t\x12\r\n\x05index\x18\t \x01(\x03b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'templates.parameter_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_PARAMETER']._serialized_start = 180
    _globals['_PARAMETER']._serialized_end = 536