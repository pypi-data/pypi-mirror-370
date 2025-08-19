from templates import campaign_template_pb2 as _campaign_template_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from templates import experiment_template_pb2 as _experiment_template_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnalyzerValidationRequest(_message.Message):
    __slots__ = ("analyzer_id", "experiment_template")
    ANALYZER_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    analyzer_id: str
    experiment_template: _experiment_template_pb2.ExperimentTemplate
    def __init__(self, analyzer_id: _Optional[str] = ..., experiment_template: _Optional[_Union[_experiment_template_pb2.ExperimentTemplate, _Mapping]] = ...) -> None: ...

class ValidationResponse(_message.Message):
    __slots__ = ("success", "messages")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    success: bool
    messages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, success: bool = ..., messages: _Optional[_Iterable[str]] = ...) -> None: ...
