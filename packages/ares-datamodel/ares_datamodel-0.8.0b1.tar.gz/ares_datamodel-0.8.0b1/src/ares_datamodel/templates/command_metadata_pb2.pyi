from templates import parameter_metadata_pb2 as _parameter_metadata_pb2
from templates import output_metadata_pb2 as _output_metadata_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommandMetadata(_message.Message):
    __slots__ = ("unique_id", "name", "description", "device_name", "output_metadata", "parameter_metadatas", "device_type")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_METADATA_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_METADATAS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_TYPE_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    name: str
    description: str
    device_name: str
    output_metadata: _output_metadata_pb2.OutputMetadata
    parameter_metadatas: _containers.RepeatedCompositeFieldContainer[_parameter_metadata_pb2.ParameterMetadata]
    device_type: str
    def __init__(self, unique_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., device_name: _Optional[str] = ..., output_metadata: _Optional[_Union[_output_metadata_pb2.OutputMetadata, _Mapping]] = ..., parameter_metadatas: _Optional[_Iterable[_Union[_parameter_metadata_pb2.ParameterMetadata, _Mapping]]] = ..., device_type: _Optional[str] = ...) -> None: ...
