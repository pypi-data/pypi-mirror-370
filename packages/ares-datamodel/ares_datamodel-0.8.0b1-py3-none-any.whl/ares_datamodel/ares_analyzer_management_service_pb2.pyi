from analyzing import analyzer_info_pb2 as _analyzer_info_pb2
from analyzing import analyzer_state_pb2 as _analyzer_state_pb2
from analyzing import analyzer_settings_pb2 as _analyzer_settings_pb2
import ares_struct_pb2 as _ares_struct_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAllAnalyzersResponse(_message.Message):
    __slots__ = ("analyzers",)
    ANALYZERS_FIELD_NUMBER: _ClassVar[int]
    analyzers: _containers.RepeatedCompositeFieldContainer[_analyzer_info_pb2.AnalyzerInfo]
    def __init__(self, analyzers: _Optional[_Iterable[_Union[_analyzer_info_pb2.AnalyzerInfo, _Mapping]]] = ...) -> None: ...

class AddRemoteAnalyzerRequest(_message.Message):
    __slots__ = ("name", "url")
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    name: str
    url: str
    def __init__(self, name: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class AddRemoteAnalyzerResponse(_message.Message):
    __slots__ = ("analyzer_id", "success", "error_message")
    ANALYZER_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    analyzer_id: str
    success: bool
    error_message: str
    def __init__(self, analyzer_id: _Optional[str] = ..., success: bool = ..., error_message: _Optional[str] = ...) -> None: ...

class UpdateRemoteAnalyzerRequest(_message.Message):
    __slots__ = ("analyzer_id", "name", "url")
    ANALYZER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    analyzer_id: str
    name: str
    url: str
    def __init__(self, analyzer_id: _Optional[str] = ..., name: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class UpdateRemoteAnalyzerResponse(_message.Message):
    __slots__ = ("success", "error_message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error_message: str
    def __init__(self, success: bool = ..., error_message: _Optional[str] = ...) -> None: ...

class RemoveRemoteAnalyzerRequest(_message.Message):
    __slots__ = ("analyzer_id", "success", "error_message")
    ANALYZER_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    analyzer_id: str
    success: bool
    error_message: str
    def __init__(self, analyzer_id: _Optional[str] = ..., success: bool = ..., error_message: _Optional[str] = ...) -> None: ...

class AnalyzerStateRequest(_message.Message):
    __slots__ = ("analyzer_id",)
    ANALYZER_ID_FIELD_NUMBER: _ClassVar[int]
    analyzer_id: str
    def __init__(self, analyzer_id: _Optional[str] = ...) -> None: ...

class AnalyzerStateResponse(_message.Message):
    __slots__ = ("state", "state_message")
    STATE_FIELD_NUMBER: _ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    state: _analyzer_state_pb2.AnalyzerState
    state_message: str
    def __init__(self, state: _Optional[_Union[_analyzer_state_pb2.AnalyzerState, str]] = ..., state_message: _Optional[str] = ...) -> None: ...

class AnalyzerInfoRequest(_message.Message):
    __slots__ = ("analyzer_id",)
    ANALYZER_ID_FIELD_NUMBER: _ClassVar[int]
    analyzer_id: str
    def __init__(self, analyzer_id: _Optional[str] = ...) -> None: ...

class AnalyzerInfoResponse(_message.Message):
    __slots__ = ("info",)
    INFO_FIELD_NUMBER: _ClassVar[int]
    info: _analyzer_info_pb2.AnalyzerInfo
    def __init__(self, info: _Optional[_Union[_analyzer_info_pb2.AnalyzerInfo, _Mapping]] = ...) -> None: ...

class AnalyzerSettingsRequest(_message.Message):
    __slots__ = ("analyzer_id",)
    ANALYZER_ID_FIELD_NUMBER: _ClassVar[int]
    analyzer_id: str
    def __init__(self, analyzer_id: _Optional[str] = ...) -> None: ...
