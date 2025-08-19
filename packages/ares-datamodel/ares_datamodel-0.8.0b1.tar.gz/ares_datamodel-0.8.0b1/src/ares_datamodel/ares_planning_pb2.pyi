import planner_adapter_info_pb2 as _planner_adapter_info_pb2
from planning import manual_planner_pb2 as _manual_planner_pb2
from planning import ares_planner_pb2 as _ares_planner_pb2
from planning import planner_status_pb2 as _planner_status_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAllPlannersResponse(_message.Message):
    __slots__ = ("planners",)
    PLANNERS_FIELD_NUMBER: _ClassVar[int]
    planners: _containers.RepeatedCompositeFieldContainer[_planner_adapter_info_pb2.PlannerAdapterInfo]
    def __init__(self, planners: _Optional[_Iterable[_Union[_planner_adapter_info_pb2.PlannerAdapterInfo, _Mapping]]] = ...) -> None: ...

class CapabilitiesRequest(_message.Message):
    __slots__ = ("adapter_name",)
    ADAPTER_NAME_FIELD_NUMBER: _ClassVar[int]
    adapter_name: str
    def __init__(self, adapter_name: _Optional[str] = ...) -> None: ...

class PlannerStatusRequest(_message.Message):
    __slots__ = ("adapter_name",)
    ADAPTER_NAME_FIELD_NUMBER: _ClassVar[int]
    adapter_name: str
    def __init__(self, adapter_name: _Optional[str] = ...) -> None: ...

class PlannerActivationRequest(_message.Message):
    __slots__ = ("adapter_name",)
    ADAPTER_NAME_FIELD_NUMBER: _ClassVar[int]
    adapter_name: str
    def __init__(self, adapter_name: _Optional[str] = ...) -> None: ...

class PlannerSettingsRequest(_message.Message):
    __slots__ = ("service_name", "planner_name")
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    PLANNER_NAME_FIELD_NUMBER: _ClassVar[int]
    service_name: str
    planner_name: str
    def __init__(self, service_name: _Optional[str] = ..., planner_name: _Optional[str] = ...) -> None: ...

class PlannerSettingsResponse(_message.Message):
    __slots__ = ("settings",)
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    settings: _containers.RepeatedCompositeFieldContainer[_ares_planner_pb2.PlannerSetting]
    def __init__(self, settings: _Optional[_Iterable[_Union[_ares_planner_pb2.PlannerSetting, _Mapping]]] = ...) -> None: ...

class CapabilitiesResponse(_message.Message):
    __slots__ = ("planner_capability",)
    PLANNER_CAPABILITY_FIELD_NUMBER: _ClassVar[int]
    planner_capability: _containers.RepeatedCompositeFieldContainer[PlannerOption]
    def __init__(self, planner_capability: _Optional[_Iterable[_Union[PlannerOption, _Mapping]]] = ...) -> None: ...

class GenericPlanner(_message.Message):
    __slots__ = ("name", "address")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    name: str
    address: str
    def __init__(self, name: _Optional[str] = ..., address: _Optional[str] = ...) -> None: ...

class PlannerOption(_message.Message):
    __slots__ = ("name", "description", "version")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    version: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...
