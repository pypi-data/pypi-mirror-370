"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'device/device_status.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1adevice/device_status.proto\x12\x15ares.datamodel.device"Y\n\x0cDeviceStatus\x128\n\x0cdevice_state\x18\x01 \x01(\x0e2".ares.datamodel.device.DeviceState\x12\x0f\n\x07message\x18\x02 \x01(\t*2\n\x0bDeviceState\x12\x0c\n\x08INACTIVE\x10\x00\x12\n\n\x06ACTIVE\x10\x01\x12\t\n\x05ERROR\x10\x02b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'device.device_status_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_DEVICESTATE']._serialized_start = 144
    _globals['_DEVICESTATE']._serialized_end = 194
    _globals['_DEVICESTATUS']._serialized_start = 53
    _globals['_DEVICESTATUS']._serialized_end = 142