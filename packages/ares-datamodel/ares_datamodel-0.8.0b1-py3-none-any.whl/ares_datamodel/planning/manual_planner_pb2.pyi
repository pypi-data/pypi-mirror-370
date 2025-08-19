import ares_struct_pb2 as _ares_struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ManualPlannerSeed(_message.Message):
    __slots__ = ("planner_values", "file_lines")
    PLANNER_VALUES_FIELD_NUMBER: _ClassVar[int]
    FILE_LINES_FIELD_NUMBER: _ClassVar[int]
    planner_values: ManualPlannerSetCollection
    file_lines: ManualPlannerFileLines
    def __init__(self, planner_values: _Optional[_Union[ManualPlannerSetCollection, _Mapping]] = ..., file_lines: _Optional[_Union[ManualPlannerFileLines, _Mapping]] = ...) -> None: ...

class ManualPlannerSet(_message.Message):
    __slots__ = ("parameter_values",)
    PARAMETER_VALUES_FIELD_NUMBER: _ClassVar[int]
    parameter_values: _containers.RepeatedCompositeFieldContainer[ParameterNameValuePair]
    def __init__(self, parameter_values: _Optional[_Iterable[_Union[ParameterNameValuePair, _Mapping]]] = ...) -> None: ...

class ParameterNameValuePair(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: _ares_struct_pb2.AresValue
    def __init__(self, name: _Optional[str] = ..., value: _Optional[_Union[_ares_struct_pb2.AresValue, _Mapping]] = ...) -> None: ...

class ManualPlannerFileLines(_message.Message):
    __slots__ = ("planner_values",)
    PLANNER_VALUES_FIELD_NUMBER: _ClassVar[int]
    planner_values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, planner_values: _Optional[_Iterable[str]] = ...) -> None: ...

class ManualPlannerSetCollection(_message.Message):
    __slots__ = ("planned_values",)
    PLANNED_VALUES_FIELD_NUMBER: _ClassVar[int]
    planned_values: _containers.RepeatedCompositeFieldContainer[ManualPlannerSet]
    def __init__(self, planned_values: _Optional[_Iterable[_Union[ManualPlannerSet, _Mapping]]] = ...) -> None: ...
