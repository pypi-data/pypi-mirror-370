from analyzing import analyzer_info_pb2 as _analyzer_info_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnalysisOverview(_message.Message):
    __slots__ = ("unique_id", "experiment_overview_id", "result", "analyzer_info")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_OVERVIEW_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ANALYZER_INFO_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    experiment_overview_id: str
    result: float
    analyzer_info: _analyzer_info_pb2.AnalyzerInfo
    def __init__(self, unique_id: _Optional[str] = ..., experiment_overview_id: _Optional[str] = ..., result: _Optional[float] = ..., analyzer_info: _Optional[_Union[_analyzer_info_pb2.AnalyzerInfo, _Mapping]] = ...) -> None: ...
