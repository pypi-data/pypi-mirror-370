from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServerStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IDLE: _ClassVar[ServerStatus]
    BUSY: _ClassVar[ServerStatus]
    ERROR: _ClassVar[ServerStatus]
    STOPPING: _ClassVar[ServerStatus]
    STOPPED: _ClassVar[ServerStatus]
IDLE: ServerStatus
BUSY: ServerStatus
ERROR: ServerStatus
STOPPING: ServerStatus
STOPPED: ServerStatus

class ServerInfoResponse(_message.Message):
    __slots__ = ("server_name", "version")
    SERVER_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    server_name: str
    version: str
    def __init__(self, server_name: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class ServerStatusResponse(_message.Message):
    __slots__ = ("server_status", "status_message")
    SERVER_STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    server_status: ServerStatus
    status_message: str
    def __init__(self, server_status: _Optional[_Union[ServerStatus, str]] = ..., status_message: _Optional[str] = ...) -> None: ...
