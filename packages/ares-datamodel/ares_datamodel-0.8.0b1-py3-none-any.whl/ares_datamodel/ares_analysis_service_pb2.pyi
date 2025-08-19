import validation_result_pb2 as _validation_result_pb2
from analyzing import analysis_pb2 as _analysis_pb2
import ares_struct_pb2 as _ares_struct_pb2
import ares_data_schema_pb2 as _ares_data_schema_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AnalysisRequest(_message.Message):
    __slots__ = ("analyzer_id", "inputs", "settings")
    ANALYZER_ID_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    analyzer_id: str
    inputs: _ares_struct_pb2.AresStruct
    settings: _ares_struct_pb2.AresStruct
    def __init__(self, analyzer_id: _Optional[str] = ..., inputs: _Optional[_Union[_ares_struct_pb2.AresStruct, _Mapping]] = ..., settings: _Optional[_Union[_ares_struct_pb2.AresStruct, _Mapping]] = ...) -> None: ...

class InputValidationRequest(_message.Message):
    __slots__ = ("analyzer_id", "input_schema")
    ANALYZER_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    analyzer_id: str
    input_schema: _ares_data_schema_pb2.AresDataSchemaSimplified
    def __init__(self, analyzer_id: _Optional[str] = ..., input_schema: _Optional[_Union[_ares_data_schema_pb2.AresDataSchemaSimplified, _Mapping]] = ...) -> None: ...

class AnalyzerParametersRequest(_message.Message):
    __slots__ = ("analyzer_id",)
    ANALYZER_ID_FIELD_NUMBER: _ClassVar[int]
    analyzer_id: str
    def __init__(self, analyzer_id: _Optional[str] = ...) -> None: ...

class AnalyzerParametersResponse(_message.Message):
    __slots__ = ("analysis_schema",)
    ANALYSIS_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    analysis_schema: _ares_data_schema_pb2.AresDataSchema
    def __init__(self, analysis_schema: _Optional[_Union[_ares_data_schema_pb2.AresDataSchema, _Mapping]] = ...) -> None: ...
