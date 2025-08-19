from google.protobuf import wrappers_pb2 as _wrappers_pb2
import ares_data_schema_pb2 as _ares_data_schema_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OutputMetadata(_message.Message):
    __slots__ = ("unique_id", "data_schema", "description", "index")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    data_schema: _ares_data_schema_pb2.AresDataSchemaSimplified
    description: str
    index: int
    def __init__(self, unique_id: _Optional[str] = ..., data_schema: _Optional[_Union[_ares_data_schema_pb2.AresDataSchemaSimplified, _Mapping]] = ..., description: _Optional[str] = ..., index: _Optional[int] = ...) -> None: ...
