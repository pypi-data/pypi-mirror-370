from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlannerState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INACTIVE: _ClassVar[PlannerState]
    ACTIVE: _ClassVar[PlannerState]
    ERROR: _ClassVar[PlannerState]
INACTIVE: PlannerState
ACTIVE: PlannerState
ERROR: PlannerState

class PlannerStatus(_message.Message):
    __slots__ = ("planner_state", "message")
    PLANNER_STATE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    planner_state: PlannerState
    message: str
    def __init__(self, planner_state: _Optional[_Union[PlannerState, str]] = ..., message: _Optional[str] = ...) -> None: ...
