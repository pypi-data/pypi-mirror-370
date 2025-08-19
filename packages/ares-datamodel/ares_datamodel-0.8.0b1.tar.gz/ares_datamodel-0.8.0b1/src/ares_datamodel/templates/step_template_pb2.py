"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'templates/step_template.proto')
_sym_db = _symbol_database.Default()
from ..templates import command_template_pb2 as templates_dot_command__template__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dtemplates/step_template.proto\x12\x18ares.datamodel.templates\x1a templates/command_template.proto\x1a\x1egoogle/protobuf/wrappers.proto"\x99\x01\n\x0cStepTemplate\x12\x11\n\tunique_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x13\n\x0bis_parallel\x18\x03 \x01(\x08\x12D\n\x11command_templates\x18\x04 \x03(\x0b2).ares.datamodel.templates.CommandTemplate\x12\r\n\x05index\x18\x05 \x01(\x03b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'templates.step_template_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_STEPTEMPLATE']._serialized_start = 126
    _globals['_STEPTEMPLATE']._serialized_end = 279