from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InternalVariableType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VAR_UNSPECIFIED: _ClassVar[InternalVariableType]
    CURRENT_EXPERIMENT_NUMBER: _ClassVar[InternalVariableType]
    CURRENT_CAMPAIGN_ID: _ClassVar[InternalVariableType]
    CURRENT_CAMPAIGN_NAME: _ClassVar[InternalVariableType]
VAR_UNSPECIFIED: InternalVariableType
CURRENT_EXPERIMENT_NUMBER: InternalVariableType
CURRENT_CAMPAIGN_ID: InternalVariableType
CURRENT_CAMPAIGN_NAME: InternalVariableType

class InternalVariableAllocation(_message.Message):
    __slots__ = ("unique_id", "internal_variable_type", "value")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_VARIABLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    internal_variable_type: InternalVariableType
    value: str
    def __init__(self, unique_id: _Optional[str] = ..., internal_variable_type: _Optional[_Union[InternalVariableType, str]] = ..., value: _Optional[str] = ...) -> None: ...
