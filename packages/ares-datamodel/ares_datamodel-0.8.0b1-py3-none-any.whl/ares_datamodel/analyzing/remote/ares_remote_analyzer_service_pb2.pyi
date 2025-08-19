from analyzing import analysis_pb2 as _analysis_pb2
import ares_struct_pb2 as _ares_struct_pb2
from analyzing import analyzer_state_pb2 as _analyzer_state_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from analyzing import analyzer_capabilities_pb2 as _analyzer_capabilities_pb2
import ares_data_schema_pb2 as _ares_data_schema_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConnectionStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_CONNECTION_STATUS: _ClassVar[ConnectionStatus]
    CONNECTED: _ClassVar[ConnectionStatus]
    DISCONNECTED: _ClassVar[ConnectionStatus]
UNKNOWN_CONNECTION_STATUS: ConnectionStatus
CONNECTED: ConnectionStatus
DISCONNECTED: ConnectionStatus

class ParameterValidationRequest(_message.Message):
    __slots__ = ("input_schema",)
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    input_schema: _ares_data_schema_pb2.AresDataSchemaSimplified
    def __init__(self, input_schema: _Optional[_Union[_ares_data_schema_pb2.AresDataSchemaSimplified, _Mapping]] = ...) -> None: ...

class ParameterValidationResult(_message.Message):
    __slots__ = ("success", "messages")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    success: bool
    messages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, success: bool = ..., messages: _Optional[_Iterable[str]] = ...) -> None: ...

class AnalysisRequest(_message.Message):
    __slots__ = ("inputs", "settings")
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    inputs: _ares_struct_pb2.AresStruct
    settings: _ares_struct_pb2.AresStruct
    def __init__(self, inputs: _Optional[_Union[_ares_struct_pb2.AresStruct, _Mapping]] = ..., settings: _Optional[_Union[_ares_struct_pb2.AresStruct, _Mapping]] = ...) -> None: ...

class AnalysisParametersResponse(_message.Message):
    __slots__ = ("parameter_schema",)
    PARAMETER_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    parameter_schema: _ares_data_schema_pb2.AresDataSchema
    def __init__(self, parameter_schema: _Optional[_Union[_ares_data_schema_pb2.AresDataSchema, _Mapping]] = ...) -> None: ...

class ConnectionStatusResponse(_message.Message):
    __slots__ = ("status", "info")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    status: ConnectionStatus
    info: str
    def __init__(self, status: _Optional[_Union[ConnectionStatus, str]] = ..., info: _Optional[str] = ...) -> None: ...

class AnalyzerStateResponse(_message.Message):
    __slots__ = ("state", "state_message")
    STATE_FIELD_NUMBER: _ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    state: _analyzer_state_pb2.AnalyzerState
    state_message: str
    def __init__(self, state: _Optional[_Union[_analyzer_state_pb2.AnalyzerState, str]] = ..., state_message: _Optional[str] = ...) -> None: ...

class InfoResponse(_message.Message):
    __slots__ = ("name", "version", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    version: str
    description: str
    def __init__(self, name: _Optional[str] = ..., version: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...
