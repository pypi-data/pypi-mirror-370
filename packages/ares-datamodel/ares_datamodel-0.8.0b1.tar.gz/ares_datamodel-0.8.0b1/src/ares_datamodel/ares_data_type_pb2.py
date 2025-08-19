"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_data_type.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14ares_data_type.proto\x12\x0eares.datamodel*\x97\x01\n\x0cAresDataType\x12\x14\n\x10UNSPECIFIED_TYPE\x10\x00\x12\x08\n\x04NULL\x10\x01\x12\x0b\n\x07BOOLEAN\x10\x02\x12\n\n\x06STRING\x10\x03\x12\n\n\x06NUMBER\x10\x04\x12\x10\n\x0cSTRING_ARRAY\x10\x05\x12\x10\n\x0cNUMBER_ARRAY\x10\x06\x12\x0e\n\nBYTE_ARRAY\x10\x07\x12\x0e\n\nBOOL_ARRAY\x10\x08b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_data_type_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ARESDATATYPE']._serialized_start = 41
    _globals['_ARESDATATYPE']._serialized_end = 192