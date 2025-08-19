import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
import experiment_overview_pb2 as _experiment_overview_pb2
import device_command_result_pb2 as _device_command_result_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExecutionInfo(_message.Message):
    __slots__ = ("unique_id", "time_started", "time_finished", "timezone", "localtime_offset")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_STARTED_FIELD_NUMBER: _ClassVar[int]
    TIME_FINISHED_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    LOCALTIME_OFFSET_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    time_started: _timestamp_pb2.Timestamp
    time_finished: _timestamp_pb2.Timestamp
    timezone: str
    localtime_offset: str
    def __init__(self, unique_id: _Optional[str] = ..., time_started: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., time_finished: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., timezone: _Optional[str] = ..., localtime_offset: _Optional[str] = ...) -> None: ...

class CampaignExecutionSummary(_message.Message):
    __slots__ = ("unique_id", "campaign_id", "experiment_summaries", "execution_info", "campaign_name", "campaign_tags", "campaign_notes", "startup_execution_summary", "closeout_execution_summary")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_SUMMARIES_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_INFO_FIELD_NUMBER: _ClassVar[int]
    CAMPAIGN_NAME_FIELD_NUMBER: _ClassVar[int]
    CAMPAIGN_TAGS_FIELD_NUMBER: _ClassVar[int]
    CAMPAIGN_NOTES_FIELD_NUMBER: _ClassVar[int]
    STARTUP_EXECUTION_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    CLOSEOUT_EXECUTION_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    campaign_id: str
    experiment_summaries: _containers.RepeatedCompositeFieldContainer[ExperimentExecutionSummary]
    execution_info: ExecutionInfo
    campaign_name: str
    campaign_tags: str
    campaign_notes: str
    startup_execution_summary: ExperimentExecutionSummary
    closeout_execution_summary: ExperimentExecutionSummary
    def __init__(self, unique_id: _Optional[str] = ..., campaign_id: _Optional[str] = ..., experiment_summaries: _Optional[_Iterable[_Union[ExperimentExecutionSummary, _Mapping]]] = ..., execution_info: _Optional[_Union[ExecutionInfo, _Mapping]] = ..., campaign_name: _Optional[str] = ..., campaign_tags: _Optional[str] = ..., campaign_notes: _Optional[str] = ..., startup_execution_summary: _Optional[_Union[ExperimentExecutionSummary, _Mapping]] = ..., closeout_execution_summary: _Optional[_Union[ExperimentExecutionSummary, _Mapping]] = ...) -> None: ...

class ExperimentExecutionSummary(_message.Message):
    __slots__ = ("unique_id", "experiment_id", "step_summaries", "execution_info", "experiment_overview", "result_output_path")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_SUMMARIES_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_INFO_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_OVERVIEW_FIELD_NUMBER: _ClassVar[int]
    RESULT_OUTPUT_PATH_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    experiment_id: str
    step_summaries: _containers.RepeatedCompositeFieldContainer[StepExecutionSummary]
    execution_info: ExecutionInfo
    experiment_overview: _experiment_overview_pb2.ExperimentOverview
    result_output_path: str
    def __init__(self, unique_id: _Optional[str] = ..., experiment_id: _Optional[str] = ..., step_summaries: _Optional[_Iterable[_Union[StepExecutionSummary, _Mapping]]] = ..., execution_info: _Optional[_Union[ExecutionInfo, _Mapping]] = ..., experiment_overview: _Optional[_Union[_experiment_overview_pb2.ExperimentOverview, _Mapping]] = ..., result_output_path: _Optional[str] = ...) -> None: ...

class StepExecutionSummary(_message.Message):
    __slots__ = ("unique_id", "step_id", "command_summaries", "execution_info")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_SUMMARIES_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_INFO_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    step_id: str
    command_summaries: _containers.RepeatedCompositeFieldContainer[CommandExecutionSummary]
    execution_info: ExecutionInfo
    def __init__(self, unique_id: _Optional[str] = ..., step_id: _Optional[str] = ..., command_summaries: _Optional[_Iterable[_Union[CommandExecutionSummary, _Mapping]]] = ..., execution_info: _Optional[_Union[ExecutionInfo, _Mapping]] = ...) -> None: ...

class CommandExecutionSummary(_message.Message):
    __slots__ = ("unique_id", "command_id", "execution_info", "result", "command_name", "command_description")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_INFO_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    COMMAND_NAME_FIELD_NUMBER: _ClassVar[int]
    COMMAND_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    command_id: str
    execution_info: ExecutionInfo
    result: _device_command_result_pb2.DeviceCommandResult
    command_name: str
    command_description: str
    def __init__(self, unique_id: _Optional[str] = ..., command_id: _Optional[str] = ..., execution_info: _Optional[_Union[ExecutionInfo, _Mapping]] = ..., result: _Optional[_Union[_device_command_result_pb2.DeviceCommandResult, _Mapping]] = ..., command_name: _Optional[str] = ..., command_description: _Optional[str] = ...) -> None: ...
