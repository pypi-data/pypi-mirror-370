from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeviceConfig(_message.Message):
    __slots__ = ("unique_id", "device_name", "device_type", "config_data")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONFIG_DATA_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    device_name: str
    device_type: str
    config_data: _any_pb2.Any
    def __init__(self, unique_id: _Optional[str] = ..., device_name: _Optional[str] = ..., device_type: _Optional[str] = ..., config_data: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
