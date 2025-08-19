"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'templates/variable_allocation.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#templates/variable_allocation.proto\x12\x18ares.datamodel.templates\x1a\x1egoogle/protobuf/wrappers.proto"~\n\x12VariableAllocation\x12\x11\n\tunqiue_id\x18\x01 \x01(\t\x12=\n\rvariable_type\x18\x02 \x01(\x0e2&.ares.datamodel.templates.VariableType\x12\x16\n\x0eparameter_name\x18\x03 \x01(\t*\xae\x01\n\x0cVariableType\x12\x13\n\x0fVAR_UNSPECIFIED\x10\x00\x12\x18\n\x14CAMPAIGN_RESULT_PATH\x10\x01\x12\x1a\n\x16EXPERIMENT_RESULT_PATH\x10\x02\x12\x1c\n\x18PREVIOUS_EXPERIMENT_PATH\x10\x03\x12\x18\n\x14CAMPAIGN_MISC_FOLDER\x10\x04\x12\x1b\n\x17CAMPAIGN_STARTUP_FOLDER\x10\x05b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'templates.variable_allocation_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_VARIABLETYPE']._serialized_start = 226
    _globals['_VARIABLETYPE']._serialized_end = 400
    _globals['_VARIABLEALLOCATION']._serialized_start = 97
    _globals['_VARIABLEALLOCATION']._serialized_end = 223