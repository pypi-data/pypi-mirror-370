"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_devices.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from .templates import command_metadata_pb2 as templates_dot_command__metadata__pb2
from .templates import command_template_pb2 as templates_dot_command__template__pb2
from . import device_command_result_pb2 as device__command__result__pb2
from .device import device_status_pb2 as device_dot_device__status__pb2
from .device import device_config_pb2 as device_dot_device__config__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12ares_devices.proto\x12\x14ares.services.device\x1a\x1bgoogle/protobuf/empty.proto\x1a templates/command_metadata.proto\x1a templates/command_template.proto\x1a\x1bdevice_command_result.proto\x1a\x1adevice/device_status.proto\x1a\x1adevice/device_config.proto",\n\x0eAresDeviceInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\t"U\n\x17ListAresDevicesResponse\x12:\n\x0cares_devices\x18\x01 \x03(\x0b2$.ares.services.device.AresDeviceInfo"5\n\x1dListServerSerialPortsResponse\x12\x14\n\x0cserial_ports\x18\x01 \x03(\t".\n\x17CommandMetadatasRequest\x12\x13\n\x0bdevice_name\x18\x01 \x01(\t"X\n\x18CommandMetadatasResponse\x12<\n\tmetadatas\x18\x01 \x03(\x0b2).ares.datamodel.templates.CommandMetadata"*\n\x13DeviceStatusRequest\x12\x13\n\x0bdevice_name\x18\x01 \x01(\t",\n\x15DeviceActivateRequest\x12\x13\n\x0bdevice_name\x18\x01 \x01(\t"*\n\x13DeviceConfigRequest\x12\x13\n\x0bdevice_type\x18\x01 \x01(\t"L\n\x14DeviceConfigResponse\x124\n\x07configs\x18\x01 \x03(\x0b2#.ares.datamodel.device.DeviceConfig2\xc6\x05\n\x0bAresDevices\x12X\n\x0fListAresDevices\x12\x16.google.protobuf.Empty\x1a-.ares.services.device.ListAresDevicesResponse\x12c\n\x14GetServerSerialPorts\x12\x16.google.protobuf.Empty\x1a3.ares.services.device.ListServerSerialPortsResponse\x12a\n\x0fGetDeviceStatus\x12).ares.services.device.DeviceStatusRequest\x1a#.ares.datamodel.device.DeviceStatus\x12t\n\x13GetCommandMetadatas\x12-.ares.services.device.CommandMetadatasRequest\x1a..ares.services.device.CommandMetadatasResponse\x12`\n\x0eExecuteCommand\x12).ares.datamodel.templates.CommandTemplate\x1a#.ares.datamodel.DeviceCommandResult\x12l\n\x13GetAllDeviceConfigs\x12).ares.services.device.DeviceConfigRequest\x1a*.ares.services.device.DeviceConfigResponse\x12O\n\x08Activate\x12+.ares.services.device.DeviceActivateRequest\x1a\x16.google.protobuf.Emptyb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_devices_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_ARESDEVICEINFO']._serialized_start = 226
    _globals['_ARESDEVICEINFO']._serialized_end = 270
    _globals['_LISTARESDEVICESRESPONSE']._serialized_start = 272
    _globals['_LISTARESDEVICESRESPONSE']._serialized_end = 357
    _globals['_LISTSERVERSERIALPORTSRESPONSE']._serialized_start = 359
    _globals['_LISTSERVERSERIALPORTSRESPONSE']._serialized_end = 412
    _globals['_COMMANDMETADATASREQUEST']._serialized_start = 414
    _globals['_COMMANDMETADATASREQUEST']._serialized_end = 460
    _globals['_COMMANDMETADATASRESPONSE']._serialized_start = 462
    _globals['_COMMANDMETADATASRESPONSE']._serialized_end = 550
    _globals['_DEVICESTATUSREQUEST']._serialized_start = 552
    _globals['_DEVICESTATUSREQUEST']._serialized_end = 594
    _globals['_DEVICEACTIVATEREQUEST']._serialized_start = 596
    _globals['_DEVICEACTIVATEREQUEST']._serialized_end = 640
    _globals['_DEVICECONFIGREQUEST']._serialized_start = 642
    _globals['_DEVICECONFIGREQUEST']._serialized_end = 684
    _globals['_DEVICECONFIGRESPONSE']._serialized_start = 686
    _globals['_DEVICECONFIGRESPONSE']._serialized_end = 762
    _globals['_ARESDEVICES']._serialized_start = 765
    _globals['_ARESDEVICES']._serialized_end = 1475