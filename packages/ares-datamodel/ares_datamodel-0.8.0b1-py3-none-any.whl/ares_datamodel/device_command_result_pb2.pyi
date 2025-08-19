import ares_struct_pb2 as _ares_struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeviceCommandResult(_message.Message):
    __slots__ = ("unique_id", "result", "success", "error", "await_user_input")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    AWAIT_USER_INPUT_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    result: _ares_struct_pb2.AresStruct
    success: bool
    error: str
    await_user_input: bool
    def __init__(self, unique_id: _Optional[str] = ..., result: _Optional[_Union[_ares_struct_pb2.AresStruct, _Mapping]] = ..., success: bool = ..., error: _Optional[str] = ..., await_user_input: bool = ...) -> None: ...
