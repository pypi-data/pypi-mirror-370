"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_safety_service.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19ares_safety_service.proto\x12\rares.services"\x16\n\x14EmergencyStopRequest"c\n\x15EmergencyStopResponse\x12\x16\n\x0estatus_message\x18\x01 \x01(\t\x122\n\x06status\x18\x02 \x01(\x0e2".ares.services.EmergencyStopStatus*>\n\x13EmergencyStopStatus\x12\x0f\n\x0bUNSPECIFIED\x10\x00\x12\x0b\n\x07SUCCESS\x10\x01\x12\t\n\x05ERROR\x10\x022v\n\x11AresSafetyService\x12a\n\x14RequestEmergencyStop\x12#.ares.services.EmergencyStopRequest\x1a$.ares.services.EmergencyStopResponseb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_safety_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_EMERGENCYSTOPSTATUS']._serialized_start = 169
    _globals['_EMERGENCYSTOPSTATUS']._serialized_end = 231
    _globals['_EMERGENCYSTOPREQUEST']._serialized_start = 44
    _globals['_EMERGENCYSTOPREQUEST']._serialized_end = 66
    _globals['_EMERGENCYSTOPRESPONSE']._serialized_start = 68
    _globals['_EMERGENCYSTOPRESPONSE']._serialized_end = 167
    _globals['_ARESSAFETYSERVICE']._serialized_start = 233
    _globals['_ARESSAFETYSERVICE']._serialized_end = 351