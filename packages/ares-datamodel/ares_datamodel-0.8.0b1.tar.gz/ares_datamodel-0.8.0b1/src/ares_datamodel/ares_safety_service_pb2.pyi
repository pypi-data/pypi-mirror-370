from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EmergencyStopStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[EmergencyStopStatus]
    SUCCESS: _ClassVar[EmergencyStopStatus]
    ERROR: _ClassVar[EmergencyStopStatus]
UNSPECIFIED: EmergencyStopStatus
SUCCESS: EmergencyStopStatus
ERROR: EmergencyStopStatus

class EmergencyStopRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EmergencyStopResponse(_message.Message):
    __slots__ = ("status_message", "status")
    STATUS_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status_message: str
    status: EmergencyStopStatus
    def __init__(self, status_message: _Optional[str] = ..., status: _Optional[_Union[EmergencyStopStatus, str]] = ...) -> None: ...
