"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_data_schema.proto')
_sym_db = _symbol_database.Default()
from . import ares_data_type_pb2 as ares__data__type__pb2
from . import ares_struct_pb2 as ares__struct__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16ares_data_schema.proto\x12\x0eares.datamodel\x1a\x14ares_data_type.proto\x1a\x11ares_struct.proto"\x98\x01\n\x0eAresDataSchema\x12:\n\x06fields\x18\x01 \x03(\x0b2*.ares.datamodel.AresDataSchema.FieldsEntry\x1aJ\n\x0bFieldsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12*\n\x05value\x18\x02 \x01(\x0b2\x1b.ares.datamodel.SchemaEntry:\x028\x01"\xad\x01\n\x18AresDataSchemaSimplified\x12D\n\x06fields\x18\x01 \x03(\x0b24.ares.datamodel.AresDataSchemaSimplified.FieldsEntry\x1aK\n\x0bFieldsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12+\n\x05value\x18\x02 \x01(\x0e2\x1c.ares.datamodel.AresDataType:\x028\x01"\xce\x01\n\x0bSchemaEntry\x12*\n\x04type\x18\x01 \x01(\x0e2\x1c.ares.datamodel.AresDataType\x12\x10\n\x08optional\x18\x02 \x01(\x08\x125\n\x0estring_choices\x18\x05 \x01(\x0b2\x1b.ares.datamodel.StringArrayH\x00\x125\n\x0enumber_choices\x18\x06 \x01(\x0b2\x1b.ares.datamodel.NumberArrayH\x00B\x13\n\x11available_choicesb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_data_schema_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ARESDATASCHEMA_FIELDSENTRY']._loaded_options = None
    _globals['_ARESDATASCHEMA_FIELDSENTRY']._serialized_options = b'8\x01'
    _globals['_ARESDATASCHEMASIMPLIFIED_FIELDSENTRY']._loaded_options = None
    _globals['_ARESDATASCHEMASIMPLIFIED_FIELDSENTRY']._serialized_options = b'8\x01'
    _globals['_ARESDATASCHEMA']._serialized_start = 84
    _globals['_ARESDATASCHEMA']._serialized_end = 236
    _globals['_ARESDATASCHEMA_FIELDSENTRY']._serialized_start = 162
    _globals['_ARESDATASCHEMA_FIELDSENTRY']._serialized_end = 236
    _globals['_ARESDATASCHEMASIMPLIFIED']._serialized_start = 239
    _globals['_ARESDATASCHEMASIMPLIFIED']._serialized_end = 412
    _globals['_ARESDATASCHEMASIMPLIFIED_FIELDSENTRY']._serialized_start = 337
    _globals['_ARESDATASCHEMASIMPLIFIED_FIELDSENTRY']._serialized_end = 412
    _globals['_SCHEMAENTRY']._serialized_start = 415
    _globals['_SCHEMAENTRY']._serialized_end = 621