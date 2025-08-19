from templates import experiment_template_pb2 as _experiment_template_pb2
from templates import parameter_metadata_pb2 as _parameter_metadata_pb2
from templates import planner_allocation_pb2 as _planner_allocation_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CampaignTemplate(_message.Message):
    __slots__ = ("unique_id", "startup_template", "experiment_template", "closeout_template", "name", "plannable_parameters", "planner_allocations")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    STARTUP_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    CLOSEOUT_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PLANNABLE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    PLANNER_ALLOCATIONS_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    startup_template: _experiment_template_pb2.ExperimentTemplate
    experiment_template: _experiment_template_pb2.ExperimentTemplate
    closeout_template: _experiment_template_pb2.ExperimentTemplate
    name: str
    plannable_parameters: _containers.RepeatedCompositeFieldContainer[_parameter_metadata_pb2.ParameterMetadata]
    planner_allocations: _containers.RepeatedCompositeFieldContainer[_planner_allocation_pb2.PlannerAllocation]
    def __init__(self, unique_id: _Optional[str] = ..., startup_template: _Optional[_Union[_experiment_template_pb2.ExperimentTemplate, _Mapping]] = ..., experiment_template: _Optional[_Union[_experiment_template_pb2.ExperimentTemplate, _Mapping]] = ..., closeout_template: _Optional[_Union[_experiment_template_pb2.ExperimentTemplate, _Mapping]] = ..., name: _Optional[str] = ..., plannable_parameters: _Optional[_Iterable[_Union[_parameter_metadata_pb2.ParameterMetadata, _Mapping]]] = ..., planner_allocations: _Optional[_Iterable[_Union[_planner_allocation_pb2.PlannerAllocation, _Mapping]]] = ...) -> None: ...
