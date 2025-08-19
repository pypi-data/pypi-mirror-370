"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'device/device_config.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1adevice/device_config.proto\x12\x15ares.datamodel.device\x1a\x19google/protobuf/any.proto\x1a\x1egoogle/protobuf/wrappers.proto"v\n\x0cDeviceConfig\x12\x11\n\tunique_id\x18\x01 \x01(\t\x12\x13\n\x0bdevice_name\x18\x02 \x01(\t\x12\x13\n\x0bdevice_type\x18\x03 \x01(\t\x12)\n\x0bconfig_data\x18\x04 \x01(\x0b2\x14.google.protobuf.Anyb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'device.device_config_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_DEVICECONFIG']._serialized_start = 112
    _globals['_DEVICECONFIG']._serialized_end = 230