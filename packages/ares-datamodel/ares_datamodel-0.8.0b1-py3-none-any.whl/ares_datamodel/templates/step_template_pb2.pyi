from templates import command_template_pb2 as _command_template_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StepTemplate(_message.Message):
    __slots__ = ("unique_id", "name", "is_parallel", "command_templates", "index")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_PARALLEL_FIELD_NUMBER: _ClassVar[int]
    COMMAND_TEMPLATES_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    name: str
    is_parallel: bool
    command_templates: _containers.RepeatedCompositeFieldContainer[_command_template_pb2.CommandTemplate]
    index: int
    def __init__(self, unique_id: _Optional[str] = ..., name: _Optional[str] = ..., is_parallel: bool = ..., command_templates: _Optional[_Iterable[_Union[_command_template_pb2.CommandTemplate, _Mapping]]] = ..., index: _Optional[int] = ...) -> None: ...
