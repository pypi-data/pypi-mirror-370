from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AnalyzerConfig(_message.Message):
    __slots__ = ("unique_id", "name", "url")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    name: str
    url: str
    def __init__(self, unique_id: _Optional[str] = ..., name: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...
