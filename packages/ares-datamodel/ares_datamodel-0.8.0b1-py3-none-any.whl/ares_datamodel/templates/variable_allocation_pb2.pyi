from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VariableType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VAR_UNSPECIFIED: _ClassVar[VariableType]
    CAMPAIGN_RESULT_PATH: _ClassVar[VariableType]
    EXPERIMENT_RESULT_PATH: _ClassVar[VariableType]
    PREVIOUS_EXPERIMENT_PATH: _ClassVar[VariableType]
    CAMPAIGN_MISC_FOLDER: _ClassVar[VariableType]
    CAMPAIGN_STARTUP_FOLDER: _ClassVar[VariableType]
VAR_UNSPECIFIED: VariableType
CAMPAIGN_RESULT_PATH: VariableType
EXPERIMENT_RESULT_PATH: VariableType
PREVIOUS_EXPERIMENT_PATH: VariableType
CAMPAIGN_MISC_FOLDER: VariableType
CAMPAIGN_STARTUP_FOLDER: VariableType

class VariableAllocation(_message.Message):
    __slots__ = ("unqiue_id", "variable_type", "parameter_name")
    UNQIUE_ID_FIELD_NUMBER: _ClassVar[int]
    VARIABLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_NAME_FIELD_NUMBER: _ClassVar[int]
    unqiue_id: str
    variable_type: VariableType
    parameter_name: str
    def __init__(self, unqiue_id: _Optional[str] = ..., variable_type: _Optional[_Union[VariableType, str]] = ..., parameter_name: _Optional[str] = ...) -> None: ...
