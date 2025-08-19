import datetime

from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Severity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[Severity]
    INFO: _ClassVar[Severity]
    WARNING: _ClassVar[Severity]
    ERROR: _ClassVar[Severity]
    DANGER: _ClassVar[Severity]
    SUCCESS: _ClassVar[Severity]
UNSPECIFIED: Severity
INFO: Severity
WARNING: Severity
ERROR: Severity
DANGER: Severity
SUCCESS: Severity

class SubscriptionRequest(_message.Message):
    __slots__ = ("clientId",)
    CLIENTID_FIELD_NUMBER: _ClassVar[int]
    clientId: str
    def __init__(self, clientId: _Optional[str] = ...) -> None: ...

class NotificationsList(_message.Message):
    __slots__ = ("notifications",)
    NOTIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    notifications: _containers.RepeatedCompositeFieldContainer[AresNotification]
    def __init__(self, notifications: _Optional[_Iterable[_Union[AresNotification, _Mapping]]] = ...) -> None: ...

class AresNotification(_message.Message):
    __slots__ = ("title", "message", "notification_severity", "timestamp", "loiter")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_SEVERITY_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LOITER_FIELD_NUMBER: _ClassVar[int]
    title: str
    message: str
    notification_severity: Severity
    timestamp: _timestamp_pb2.Timestamp
    loiter: bool
    def __init__(self, title: _Optional[str] = ..., message: _Optional[str] = ..., notification_severity: _Optional[_Union[Severity, str]] = ..., timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., loiter: bool = ...) -> None: ...
