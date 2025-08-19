"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_event.proto')
_sym_db = _symbol_database.Default()
from . import ares_notification_pb2 as ares__notification__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10ares_event.proto\x12\rares.services\x1a\x17ares_notification.proto"\x15\n\x13NotificationRequest"N\n\x14NotificationResponse\x126\n\rnotifications\x18\x01 \x03(\x0b2\x1f.ares.services.AresNotification2\xcb\x01\n\tAresEvent\x12^\n\x13GetAllNotifications\x12".ares.services.NotificationRequest\x1a#.ares.services.NotificationResponse\x12^\n\x15GetNotificationStream\x12".ares.services.NotificationRequest\x1a\x1f.ares.services.AresNotification0\x01b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_event_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_NOTIFICATIONREQUEST']._serialized_start = 60
    _globals['_NOTIFICATIONREQUEST']._serialized_end = 81
    _globals['_NOTIFICATIONRESPONSE']._serialized_start = 83
    _globals['_NOTIFICATIONRESPONSE']._serialized_end = 161
    _globals['_ARESEVENT']._serialized_start = 164
    _globals['_ARESEVENT']._serialized_end = 367