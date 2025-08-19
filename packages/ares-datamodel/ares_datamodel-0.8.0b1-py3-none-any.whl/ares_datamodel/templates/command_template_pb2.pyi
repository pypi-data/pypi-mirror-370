from templates import parameter_pb2 as _parameter_pb2
from templates import command_metadata_pb2 as _command_metadata_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommandTemplate(_message.Message):
    __slots__ = ("unique_id", "metadata", "parameters", "index", "user_output_key_map")
    class UserOutputKeyMapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    USER_OUTPUT_KEY_MAP_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    metadata: _command_metadata_pb2.CommandMetadata
    parameters: _containers.RepeatedCompositeFieldContainer[_parameter_pb2.Parameter]
    index: int
    user_output_key_map: _containers.ScalarMap[str, str]
    def __init__(self, unique_id: _Optional[str] = ..., metadata: _Optional[_Union[_command_metadata_pb2.CommandMetadata, _Mapping]] = ..., parameters: _Optional[_Iterable[_Union[_parameter_pb2.Parameter, _Mapping]]] = ..., index: _Optional[int] = ..., user_output_key_map: _Optional[_Mapping[str, str]] = ...) -> None: ...
