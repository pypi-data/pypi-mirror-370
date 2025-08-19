"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_notification.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17ares_notification.proto\x12\rares.services\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1fgoogle/protobuf/timestamp.proto"\'\n\x13SubscriptionRequest\x12\x10\n\x08clientId\x18\x01 \x01(\t"K\n\x11NotificationsList\x126\n\rnotifications\x18\x01 \x03(\x0b2\x1f.ares.services.AresNotification"\xa9\x01\n\x10AresNotification\x12\r\n\x05title\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x126\n\x15notification_severity\x18\x03 \x01(\x0e2\x17.ares.services.Severity\x12-\n\ttimestamp\x18\x04 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x0e\n\x06loiter\x18\x05 \x01(\x08*V\n\x08Severity\x12\x0f\n\x0bUNSPECIFIED\x10\x00\x12\x08\n\x04INFO\x10\x01\x12\x0b\n\x07WARNING\x10\x02\x12\t\n\x05ERROR\x10\x03\x12\n\n\x06DANGER\x10\x04\x12\x0b\n\x07SUCCESS\x10\x052\xc1\x01\n\x13AresNotificationRpc\x12R\n\tSubscribe\x12".ares.services.SubscriptionRequest\x1a\x1f.ares.services.AresNotification0\x01\x12V\n\x1aGetUpdatedNotificationList\x12\x16.google.protobuf.Empty\x1a .ares.services.NotificationsListb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_notification_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_SEVERITY']._serialized_start = 394
    _globals['_SEVERITY']._serialized_end = 480
    _globals['_SUBSCRIPTIONREQUEST']._serialized_start = 104
    _globals['_SUBSCRIPTIONREQUEST']._serialized_end = 143
    _globals['_NOTIFICATIONSLIST']._serialized_start = 145
    _globals['_NOTIFICATIONSLIST']._serialized_end = 220
    _globals['_ARESNOTIFICATION']._serialized_start = 223
    _globals['_ARESNOTIFICATION']._serialized_end = 392
    _globals['_ARESNOTIFICATIONRPC']._serialized_start = 483
    _globals['_ARESNOTIFICATIONRPC']._serialized_end = 676