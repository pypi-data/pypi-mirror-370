from templates import parameter_metadata_pb2 as _parameter_metadata_pb2
from templates import variable_allocation_pb2 as _variable_allocation_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
import ares_struct_pb2 as _ares_struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Parameter(_message.Message):
    __slots__ = ("unique_id", "metadata", "value", "planned", "environment_based", "planning_metadata", "variable_type", "variable_argument", "index")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    PLANNED_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_BASED_FIELD_NUMBER: _ClassVar[int]
    PLANNING_METADATA_FIELD_NUMBER: _ClassVar[int]
    VARIABLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    VARIABLE_ARGUMENT_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    metadata: _parameter_metadata_pb2.ParameterMetadata
    value: _ares_struct_pb2.AresValue
    planned: bool
    environment_based: bool
    planning_metadata: _parameter_metadata_pb2.ParameterMetadata
    variable_type: _variable_allocation_pb2.VariableType
    variable_argument: str
    index: int
    def __init__(self, unique_id: _Optional[str] = ..., metadata: _Optional[_Union[_parameter_metadata_pb2.ParameterMetadata, _Mapping]] = ..., value: _Optional[_Union[_ares_struct_pb2.AresValue, _Mapping]] = ..., planned: bool = ..., environment_based: bool = ..., planning_metadata: _Optional[_Union[_parameter_metadata_pb2.ParameterMetadata, _Mapping]] = ..., variable_type: _Optional[_Union[_variable_allocation_pb2.VariableType, str]] = ..., variable_argument: _Optional[str] = ..., index: _Optional[int] = ...) -> None: ...
