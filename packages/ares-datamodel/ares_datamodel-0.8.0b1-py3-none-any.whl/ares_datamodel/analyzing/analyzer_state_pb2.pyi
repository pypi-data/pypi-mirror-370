from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class AnalyzerState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED_STATE: _ClassVar[AnalyzerState]
    ACTIVE: _ClassVar[AnalyzerState]
    INACTIVE: _ClassVar[AnalyzerState]
    ERROR: _ClassVar[AnalyzerState]
UNSPECIFIED_STATE: AnalyzerState
ACTIVE: AnalyzerState
INACTIVE: AnalyzerState
ERROR: AnalyzerState
