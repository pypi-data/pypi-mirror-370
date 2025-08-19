from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeviceState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INACTIVE: _ClassVar[DeviceState]
    ACTIVE: _ClassVar[DeviceState]
    ERROR: _ClassVar[DeviceState]
INACTIVE: DeviceState
ACTIVE: DeviceState
ERROR: DeviceState

class DeviceStatus(_message.Message):
    __slots__ = ("device_state", "message")
    DEVICE_STATE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    device_state: DeviceState
    message: str
    def __init__(self, device_state: _Optional[_Union[DeviceState, str]] = ..., message: _Optional[str] = ...) -> None: ...
