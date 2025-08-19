"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from . import ares_event_pb2 as ares__event__pb2
from . import ares_notification_pb2 as ares__notification__pb2
GRPC_GENERATED_VERSION = '1.74.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in ares_event_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresEventStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetAllNotifications = channel.unary_unary('/ares.services.AresEvent/GetAllNotifications', request_serializer=ares__event__pb2.NotificationRequest.SerializeToString, response_deserializer=ares__event__pb2.NotificationResponse.FromString, _registered_method=True)
        self.GetNotificationStream = channel.unary_stream('/ares.services.AresEvent/GetNotificationStream', request_serializer=ares__event__pb2.NotificationRequest.SerializeToString, response_deserializer=ares__notification__pb2.AresNotification.FromString, _registered_method=True)

class AresEventServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetAllNotifications(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetNotificationStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_AresEventServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetAllNotifications': grpc.unary_unary_rpc_method_handler(servicer.GetAllNotifications, request_deserializer=ares__event__pb2.NotificationRequest.FromString, response_serializer=ares__event__pb2.NotificationResponse.SerializeToString), 'GetNotificationStream': grpc.unary_stream_rpc_method_handler(servicer.GetNotificationStream, request_deserializer=ares__event__pb2.NotificationRequest.FromString, response_serializer=ares__notification__pb2.AresNotification.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.services.AresEvent', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.services.AresEvent', rpc_method_handlers)

class AresEvent(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetAllNotifications(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresEvent/GetAllNotifications', ares__event__pb2.NotificationRequest.SerializeToString, ares__event__pb2.NotificationResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetNotificationStream(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/ares.services.AresEvent/GetNotificationStream', ares__event__pb2.NotificationRequest.SerializeToString, ares__notification__pb2.AresNotification.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)