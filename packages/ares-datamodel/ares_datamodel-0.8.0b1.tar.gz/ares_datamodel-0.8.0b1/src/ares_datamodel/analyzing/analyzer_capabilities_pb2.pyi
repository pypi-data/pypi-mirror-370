import ares_data_schema_pb2 as _ares_data_schema_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnalyzerCapabilities(_message.Message):
    __slots__ = ("timeout_seconds", "settings_schema")
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    timeout_seconds: int
    settings_schema: _ares_data_schema_pb2.AresDataSchema
    def __init__(self, timeout_seconds: _Optional[int] = ..., settings_schema: _Optional[_Union[_ares_data_schema_pb2.AresDataSchema, _Mapping]] = ...) -> None: ...
