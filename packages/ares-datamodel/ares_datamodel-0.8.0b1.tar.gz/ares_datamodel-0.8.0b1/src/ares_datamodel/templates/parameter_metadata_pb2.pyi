import limits_pb2 as _limits_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import any_pb2 as _any_pb2
import ares_data_schema_pb2 as _ares_data_schema_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ParameterMetadata(_message.Message):
    __slots__ = ("unique_id", "name", "unit", "constraints", "index", "not_plannable", "use_default", "schema", "planner_name", "planner_description", "extra_info")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    NOT_PLANNABLE_FIELD_NUMBER: _ClassVar[int]
    USE_DEFAULT_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    PLANNER_NAME_FIELD_NUMBER: _ClassVar[int]
    PLANNER_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EXTRA_INFO_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    name: str
    unit: str
    constraints: _containers.RepeatedCompositeFieldContainer[_limits_pb2.Limits]
    index: int
    not_plannable: bool
    use_default: bool
    schema: _ares_data_schema_pb2.SchemaEntry
    planner_name: str
    planner_description: str
    extra_info: _any_pb2.Any
    def __init__(self, unique_id: _Optional[str] = ..., name: _Optional[str] = ..., unit: _Optional[str] = ..., constraints: _Optional[_Iterable[_Union[_limits_pb2.Limits, _Mapping]]] = ..., index: _Optional[int] = ..., not_plannable: bool = ..., use_default: bool = ..., schema: _Optional[_Union[_ares_data_schema_pb2.SchemaEntry, _Mapping]] = ..., planner_name: _Optional[str] = ..., planner_description: _Optional[str] = ..., extra_info: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
