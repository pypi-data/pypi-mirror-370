"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'templates/command_template.proto')
_sym_db = _symbol_database.Default()
from ..templates import parameter_pb2 as templates_dot_parameter__pb2
from ..templates import command_metadata_pb2 as templates_dot_command__metadata__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n templates/command_template.proto\x12\x18ares.datamodel.templates\x1a\x19templates/parameter.proto\x1a templates/command_metadata.proto"\xc0\x02\n\x0fCommandTemplate\x12\x11\n\tunique_id\x18\x01 \x01(\t\x12;\n\x08metadata\x18\x02 \x01(\x0b2).ares.datamodel.templates.CommandMetadata\x127\n\nparameters\x18\x03 \x03(\x0b2#.ares.datamodel.templates.Parameter\x12\r\n\x05index\x18\x04 \x01(\x03\x12\\\n\x13user_output_key_map\x18\x05 \x03(\x0b2?.ares.datamodel.templates.CommandTemplate.UserOutputKeyMapEntry\x1a7\n\x15UserOutputKeyMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x028\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'templates.command_template_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_COMMANDTEMPLATE_USEROUTPUTKEYMAPENTRY']._loaded_options = None
    _globals['_COMMANDTEMPLATE_USEROUTPUTKEYMAPENTRY']._serialized_options = b'8\x01'
    _globals['_COMMANDTEMPLATE']._serialized_start = 124
    _globals['_COMMANDTEMPLATE']._serialized_end = 444
    _globals['_COMMANDTEMPLATE_USEROUTPUTKEYMAPENTRY']._serialized_start = 389
    _globals['_COMMANDTEMPLATE_USEROUTPUTKEYMAPENTRY']._serialized_end = 444