from templates import experiment_template_pb2 as _experiment_template_pb2
from templates import parameter_pb2 as _parameter_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
import ares_struct_pb2 as _ares_struct_pb2
import analysis_overview_pb2 as _analysis_overview_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExperimentOverview(_message.Message):
    __slots__ = ("unique_id", "template", "result", "parameters", "analysis_overview")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_OVERVIEW_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    template: _experiment_template_pb2.ExperimentTemplate
    result: _ares_struct_pb2.AresStruct
    parameters: _containers.RepeatedCompositeFieldContainer[_parameter_pb2.Parameter]
    analysis_overview: _analysis_overview_pb2.AnalysisOverview
    def __init__(self, unique_id: _Optional[str] = ..., template: _Optional[_Union[_experiment_template_pb2.ExperimentTemplate, _Mapping]] = ..., result: _Optional[_Union[_ares_struct_pb2.AresStruct, _Mapping]] = ..., parameters: _Optional[_Iterable[_Union[_parameter_pb2.Parameter, _Mapping]]] = ..., analysis_overview: _Optional[_Union[_analysis_overview_pb2.AnalysisOverview, _Mapping]] = ...) -> None: ...
