"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_server_info.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16ares_server_info.proto\x12\rares.services\x1a\x1bgoogle/protobuf/empty.proto":\n\x12ServerInfoResponse\x12\x13\n\x0bserver_name\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t"b\n\x14ServerStatusResponse\x122\n\rserver_status\x18\x01 \x01(\x0e2\x1b.ares.services.ServerStatus\x12\x16\n\x0estatus_message\x18\x02 \x01(\t*H\n\x0cServerStatus\x12\x08\n\x04IDLE\x10\x00\x12\x08\n\x04BUSY\x10\x01\x12\t\n\x05ERROR\x10\x02\x12\x0c\n\x08STOPPING\x10\x03\x12\x0b\n\x07STOPPED\x10\x042\xb4\x01\n\x0eAresServerInfo\x12J\n\rGetServerInfo\x12\x16.google.protobuf.Empty\x1a!.ares.services.ServerInfoResponse\x12V\n\x15GetServerStatusStream\x12\x16.google.protobuf.Empty\x1a#.ares.services.ServerStatusResponse0\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_server_info_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_SERVERSTATUS']._serialized_start = 230
    _globals['_SERVERSTATUS']._serialized_end = 302
    _globals['_SERVERINFORESPONSE']._serialized_start = 70
    _globals['_SERVERINFORESPONSE']._serialized_end = 128
    _globals['_SERVERSTATUSRESPONSE']._serialized_start = 130
    _globals['_SERVERSTATUSRESPONSE']._serialized_end = 228
    _globals['_ARESSERVERINFO']._serialized_start = 305
    _globals['_ARESSERVERINFO']._serialized_end = 485