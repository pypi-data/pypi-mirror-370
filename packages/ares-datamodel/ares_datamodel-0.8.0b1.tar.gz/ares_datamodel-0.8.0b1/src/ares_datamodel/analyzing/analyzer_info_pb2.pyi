from analyzing import analyzer_capabilities_pb2 as _analyzer_capabilities_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnalyzerInfo(_message.Message):
    __slots__ = ("unique_id", "name", "type", "description", "version", "capabilities", "url")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    name: str
    type: str
    description: str
    version: str
    capabilities: _analyzer_capabilities_pb2.AnalyzerCapabilities
    url: str
    def __init__(self, unique_id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., description: _Optional[str] = ..., version: _Optional[str] = ..., capabilities: _Optional[_Union[_analyzer_capabilities_pb2.AnalyzerCapabilities, _Mapping]] = ..., url: _Optional[str] = ...) -> None: ...
