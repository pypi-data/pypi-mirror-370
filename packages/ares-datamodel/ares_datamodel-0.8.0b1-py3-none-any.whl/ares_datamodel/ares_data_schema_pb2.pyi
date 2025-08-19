import ares_data_type_pb2 as _ares_data_type_pb2
import ares_struct_pb2 as _ares_struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AresDataSchema(_message.Message):
    __slots__ = ("fields",)
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: SchemaEntry
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[SchemaEntry, _Mapping]] = ...) -> None: ...
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.MessageMap[str, SchemaEntry]
    def __init__(self, fields: _Optional[_Mapping[str, SchemaEntry]] = ...) -> None: ...

class AresDataSchemaSimplified(_message.Message):
    __slots__ = ("fields",)
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _ares_data_type_pb2.AresDataType
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_ares_data_type_pb2.AresDataType, str]] = ...) -> None: ...
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.ScalarMap[str, _ares_data_type_pb2.AresDataType]
    def __init__(self, fields: _Optional[_Mapping[str, _ares_data_type_pb2.AresDataType]] = ...) -> None: ...

class SchemaEntry(_message.Message):
    __slots__ = ("type", "optional", "string_choices", "number_choices")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_FIELD_NUMBER: _ClassVar[int]
    STRING_CHOICES_FIELD_NUMBER: _ClassVar[int]
    NUMBER_CHOICES_FIELD_NUMBER: _ClassVar[int]
    type: _ares_data_type_pb2.AresDataType
    optional: bool
    string_choices: _ares_struct_pb2.StringArray
    number_choices: _ares_struct_pb2.NumberArray
    def __init__(self, type: _Optional[_Union[_ares_data_type_pb2.AresDataType, str]] = ..., optional: bool = ..., string_choices: _Optional[_Union[_ares_struct_pb2.StringArray, _Mapping]] = ..., number_choices: _Optional[_Union[_ares_struct_pb2.NumberArray, _Mapping]] = ...) -> None: ...
