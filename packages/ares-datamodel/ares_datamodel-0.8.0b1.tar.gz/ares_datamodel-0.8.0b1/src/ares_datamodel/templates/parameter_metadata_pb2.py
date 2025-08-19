"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'templates/parameter_metadata.proto')
_sym_db = _symbol_database.Default()
from .. import limits_pb2 as limits__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from .. import ares_data_schema_pb2 as ares__data__schema__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n"templates/parameter_metadata.proto\x12\x18ares.datamodel.templates\x1a\x0climits.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x19google/protobuf/any.proto\x1a\x16ares_data_schema.proto"\xb4\x02\n\x11ParameterMetadata\x12\x11\n\tunique_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04unit\x18\x03 \x01(\t\x12+\n\x0bconstraints\x18\x04 \x03(\x0b2\x16.ares.datamodel.Limits\x12\r\n\x05index\x18\x05 \x01(\x03\x12\x15\n\rnot_plannable\x18\x06 \x01(\x08\x12\x13\n\x0buse_default\x18\x07 \x01(\x08\x12+\n\x06schema\x18\x08 \x01(\x0b2\x1b.ares.datamodel.SchemaEntry\x12\x14\n\x0cplanner_name\x18\t \x01(\t\x12\x1b\n\x13planner_description\x18\n \x01(\t\x12(\n\nextra_info\x18\x0b \x01(\x0b2\x14.google.protobuf.Anyb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'templates.parameter_metadata_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_PARAMETERMETADATA']._serialized_start = 162
    _globals['_PARAMETERMETADATA']._serialized_end = 470