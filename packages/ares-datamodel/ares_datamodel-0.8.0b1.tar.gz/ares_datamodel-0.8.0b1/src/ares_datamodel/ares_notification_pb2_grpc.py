"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from . import ares_notification_pb2 as ares__notification__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
GRPC_GENERATED_VERSION = '1.74.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in ares_notification_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresNotificationRpcStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Subscribe = channel.unary_stream('/ares.services.AresNotificationRpc/Subscribe', request_serializer=ares__notification__pb2.SubscriptionRequest.SerializeToString, response_deserializer=ares__notification__pb2.AresNotification.FromString, _registered_method=True)
        self.GetUpdatedNotificationList = channel.unary_unary('/ares.services.AresNotificationRpc/GetUpdatedNotificationList', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__notification__pb2.NotificationsList.FromString, _registered_method=True)

class AresNotificationRpcServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Subscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetUpdatedNotificationList(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_AresNotificationRpcServicer_to_server(servicer, server):
    rpc_method_handlers = {'Subscribe': grpc.unary_stream_rpc_method_handler(servicer.Subscribe, request_deserializer=ares__notification__pb2.SubscriptionRequest.FromString, response_serializer=ares__notification__pb2.AresNotification.SerializeToString), 'GetUpdatedNotificationList': grpc.unary_unary_rpc_method_handler(servicer.GetUpdatedNotificationList, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__notification__pb2.NotificationsList.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.services.AresNotificationRpc', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.services.AresNotificationRpc', rpc_method_handlers)

class AresNotificationRpc(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Subscribe(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/ares.services.AresNotificationRpc/Subscribe', ares__notification__pb2.SubscriptionRequest.SerializeToString, ares__notification__pb2.AresNotification.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetUpdatedNotificationList(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresNotificationRpc/GetUpdatedNotificationList', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__notification__pb2.NotificationsList.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)