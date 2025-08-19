from templates import step_template_pb2 as _step_template_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExperimentTemplate(_message.Message):
    __slots__ = ("unique_id", "step_templates", "name", "analyzer_id", "analyzer_maps", "resolved")
    class AnalyzerMapsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_TEMPLATES_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ANALYZER_ID_FIELD_NUMBER: _ClassVar[int]
    ANALYZER_MAPS_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    step_templates: _containers.RepeatedCompositeFieldContainer[_step_template_pb2.StepTemplate]
    name: str
    analyzer_id: str
    analyzer_maps: _containers.ScalarMap[str, str]
    resolved: bool
    def __init__(self, unique_id: _Optional[str] = ..., step_templates: _Optional[_Iterable[_Union[_step_template_pb2.StepTemplate, _Mapping]]] = ..., name: _Optional[str] = ..., analyzer_id: _Optional[str] = ..., analyzer_maps: _Optional[_Mapping[str, str]] = ..., resolved: bool = ...) -> None: ...
