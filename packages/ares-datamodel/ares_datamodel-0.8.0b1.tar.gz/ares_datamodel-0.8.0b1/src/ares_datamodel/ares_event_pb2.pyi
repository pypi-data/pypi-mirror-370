import ares_notification_pb2 as _ares_notification_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NotificationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class NotificationResponse(_message.Message):
    __slots__ = ("notifications",)
    NOTIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    notifications: _containers.RepeatedCompositeFieldContainer[_ares_notification_pb2.AresNotification]
    def __init__(self, notifications: _Optional[_Iterable[_Union[_ares_notification_pb2.AresNotification, _Mapping]]] = ...) -> None: ...
