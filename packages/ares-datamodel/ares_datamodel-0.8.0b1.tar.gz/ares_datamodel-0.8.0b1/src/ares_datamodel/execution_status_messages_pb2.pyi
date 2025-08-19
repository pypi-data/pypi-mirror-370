from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExecutionState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNDEFINED: _ClassVar[ExecutionState]
    SUCCEEDED: _ClassVar[ExecutionState]
    WAITING: _ClassVar[ExecutionState]
    AWAITING_USER: _ClassVar[ExecutionState]
    RUNNING: _ClassVar[ExecutionState]
    PAUSED: _ClassVar[ExecutionState]
    FAILED: _ClassVar[ExecutionState]
UNDEFINED: ExecutionState
SUCCEEDED: ExecutionState
WAITING: ExecutionState
AWAITING_USER: ExecutionState
RUNNING: ExecutionState
PAUSED: ExecutionState
FAILED: ExecutionState

class CampaignExecutionStatus(_message.Message):
    __slots__ = ("campaign_id", "state", "experiment_execution_statuses")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_EXECUTION_STATUSES_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    state: ExecutionState
    experiment_execution_statuses: _containers.RepeatedCompositeFieldContainer[ExperimentExecutionStatus]
    def __init__(self, campaign_id: _Optional[str] = ..., state: _Optional[_Union[ExecutionState, str]] = ..., experiment_execution_statuses: _Optional[_Iterable[_Union[ExperimentExecutionStatus, _Mapping]]] = ...) -> None: ...

class CampaignExecutionState(_message.Message):
    __slots__ = ("campaign_id", "state")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    state: ExecutionState
    def __init__(self, campaign_id: _Optional[str] = ..., state: _Optional[_Union[ExecutionState, str]] = ...) -> None: ...

class ExperimentExecutionStatus(_message.Message):
    __slots__ = ("experiment_id", "step_execution_statuses")
    EXPERIMENT_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_EXECUTION_STATUSES_FIELD_NUMBER: _ClassVar[int]
    experiment_id: str
    step_execution_statuses: _containers.RepeatedCompositeFieldContainer[StepExecutionStatus]
    def __init__(self, experiment_id: _Optional[str] = ..., step_execution_statuses: _Optional[_Iterable[_Union[StepExecutionStatus, _Mapping]]] = ...) -> None: ...

class CampaignStartupStatus(_message.Message):
    __slots__ = ("campaign_id", "startup_execution_statuses")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    STARTUP_EXECUTION_STATUSES_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    startup_execution_statuses: _containers.RepeatedCompositeFieldContainer[StepExecutionStatus]
    def __init__(self, campaign_id: _Optional[str] = ..., startup_execution_statuses: _Optional[_Iterable[_Union[StepExecutionStatus, _Mapping]]] = ...) -> None: ...

class CampaignCloseoutStatus(_message.Message):
    __slots__ = ("campaign_id", "closeout_execution_statuses")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    CLOSEOUT_EXECUTION_STATUSES_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    closeout_execution_statuses: _containers.RepeatedCompositeFieldContainer[StepExecutionStatus]
    def __init__(self, campaign_id: _Optional[str] = ..., closeout_execution_statuses: _Optional[_Iterable[_Union[StepExecutionStatus, _Mapping]]] = ...) -> None: ...

class StepExecutionStatus(_message.Message):
    __slots__ = ("step_id", "step_name", "command_execution_statuses")
    STEP_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_NAME_FIELD_NUMBER: _ClassVar[int]
    COMMAND_EXECUTION_STATUSES_FIELD_NUMBER: _ClassVar[int]
    step_id: str
    step_name: str
    command_execution_statuses: _containers.RepeatedCompositeFieldContainer[CommandExecutionStatus]
    def __init__(self, step_id: _Optional[str] = ..., step_name: _Optional[str] = ..., command_execution_statuses: _Optional[_Iterable[_Union[CommandExecutionStatus, _Mapping]]] = ...) -> None: ...

class CommandExecutionStatus(_message.Message):
    __slots__ = ("command_id", "command_name", "device_name", "state")
    COMMAND_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    command_id: str
    command_name: str
    device_name: str
    state: ExecutionState
    def __init__(self, command_id: _Optional[str] = ..., command_name: _Optional[str] = ..., device_name: _Optional[str] = ..., state: _Optional[_Union[ExecutionState, str]] = ...) -> None: ...
