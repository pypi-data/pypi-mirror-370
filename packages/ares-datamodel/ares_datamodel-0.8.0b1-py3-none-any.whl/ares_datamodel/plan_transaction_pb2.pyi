import planner_adapter_info_pb2 as _planner_adapter_info_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from planning import ares_planner_pb2 as _ares_planner_pb2
from templates import parameter_metadata_pb2 as _parameter_metadata_pb2
import ares_struct_pb2 as _ares_struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlannerTransaction(_message.Message):
    __slots__ = ("unique_id", "request", "response", "planner_info", "success", "error")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    PLANNER_INFO_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    request: _ares_planner_pb2.PlanRequest
    response: _containers.RepeatedCompositeFieldContainer[PlanResult]
    planner_info: _planner_adapter_info_pb2.PlannerAdapterInfo
    success: bool
    error: str
    def __init__(self, unique_id: _Optional[str] = ..., request: _Optional[_Union[_ares_planner_pb2.PlanRequest, _Mapping]] = ..., response: _Optional[_Iterable[_Union[PlanResult, _Mapping]]] = ..., planner_info: _Optional[_Union[_planner_adapter_info_pb2.PlannerAdapterInfo, _Mapping]] = ..., success: bool = ..., error: _Optional[str] = ...) -> None: ...

class PlanResult(_message.Message):
    __slots__ = ("unique_id", "value", "parameter_metadata")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_METADATA_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    value: _ares_struct_pb2.AresValue
    parameter_metadata: _parameter_metadata_pb2.ParameterMetadata
    def __init__(self, unique_id: _Optional[str] = ..., value: _Optional[_Union[_ares_struct_pb2.AresValue, _Mapping]] = ..., parameter_metadata: _Optional[_Union[_parameter_metadata_pb2.ParameterMetadata, _Mapping]] = ...) -> None: ...
