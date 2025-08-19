from google.protobuf import empty_pb2 as _empty_pb2
from templates import command_metadata_pb2 as _command_metadata_pb2
from templates import command_template_pb2 as _command_template_pb2
import device_command_result_pb2 as _device_command_result_pb2
from device import device_status_pb2 as _device_status_pb2
from device import device_config_pb2 as _device_config_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AresDeviceInfo(_message.Message):
    __slots__ = ("name", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class ListAresDevicesResponse(_message.Message):
    __slots__ = ("ares_devices",)
    ARES_DEVICES_FIELD_NUMBER: _ClassVar[int]
    ares_devices: _containers.RepeatedCompositeFieldContainer[AresDeviceInfo]
    def __init__(self, ares_devices: _Optional[_Iterable[_Union[AresDeviceInfo, _Mapping]]] = ...) -> None: ...

class ListServerSerialPortsResponse(_message.Message):
    __slots__ = ("serial_ports",)
    SERIAL_PORTS_FIELD_NUMBER: _ClassVar[int]
    serial_ports: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, serial_ports: _Optional[_Iterable[str]] = ...) -> None: ...

class CommandMetadatasRequest(_message.Message):
    __slots__ = ("device_name",)
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    device_name: str
    def __init__(self, device_name: _Optional[str] = ...) -> None: ...

class CommandMetadatasResponse(_message.Message):
    __slots__ = ("metadatas",)
    METADATAS_FIELD_NUMBER: _ClassVar[int]
    metadatas: _containers.RepeatedCompositeFieldContainer[_command_metadata_pb2.CommandMetadata]
    def __init__(self, metadatas: _Optional[_Iterable[_Union[_command_metadata_pb2.CommandMetadata, _Mapping]]] = ...) -> None: ...

class DeviceStatusRequest(_message.Message):
    __slots__ = ("device_name",)
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    device_name: str
    def __init__(self, device_name: _Optional[str] = ...) -> None: ...

class DeviceActivateRequest(_message.Message):
    __slots__ = ("device_name",)
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    device_name: str
    def __init__(self, device_name: _Optional[str] = ...) -> None: ...

class DeviceConfigRequest(_message.Message):
    __slots__ = ("device_type",)
    DEVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    device_type: str
    def __init__(self, device_type: _Optional[str] = ...) -> None: ...

class DeviceConfigResponse(_message.Message):
    __slots__ = ("configs",)
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    configs: _containers.RepeatedCompositeFieldContainer[_device_config_pb2.DeviceConfig]
    def __init__(self, configs: _Optional[_Iterable[_Union[_device_config_pb2.DeviceConfig, _Mapping]]] = ...) -> None: ...
