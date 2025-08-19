"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'templates/command_metadata.proto')
_sym_db = _symbol_database.Default()
from ..templates import parameter_metadata_pb2 as templates_dot_parameter__metadata__pb2
from ..templates import output_metadata_pb2 as templates_dot_output__metadata__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n templates/command_metadata.proto\x12\x18ares.datamodel.templates\x1a"templates/parameter_metadata.proto\x1a\x1ftemplates/output_metadata.proto"\xfe\x01\n\x0fCommandMetadata\x12\x11\n\tunique_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0bdescription\x18\x03 \x01(\t\x12\x13\n\x0bdevice_name\x18\x04 \x01(\t\x12A\n\x0foutput_metadata\x18\x05 \x01(\x0b2(.ares.datamodel.templates.OutputMetadata\x12H\n\x13parameter_metadatas\x18\x06 \x03(\x0b2+.ares.datamodel.templates.ParameterMetadata\x12\x13\n\x0bdevice_type\x18\x07 \x01(\tb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'templates.command_metadata_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_COMMANDMETADATA']._serialized_start = 132
    _globals['_COMMANDMETADATA']._serialized_end = 386