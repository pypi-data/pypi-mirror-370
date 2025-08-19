import ares_struct_pb2 as _ares_struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnalyzerSettings(_message.Message):
    __slots__ = ("analyzer_id", "settings")
    ANALYZER_ID_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    analyzer_id: str
    settings: _ares_struct_pb2.AresStruct
    def __init__(self, analyzer_id: _Optional[str] = ..., settings: _Optional[_Union[_ares_struct_pb2.AresStruct, _Mapping]] = ...) -> None: ...
