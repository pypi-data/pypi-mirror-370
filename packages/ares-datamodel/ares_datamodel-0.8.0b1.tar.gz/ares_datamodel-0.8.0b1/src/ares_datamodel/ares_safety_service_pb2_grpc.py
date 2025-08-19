"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from . import ares_safety_service_pb2 as ares__safety__service__pb2
GRPC_GENERATED_VERSION = '1.74.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in ares_safety_service_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresSafetyServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RequestEmergencyStop = channel.unary_unary('/ares.services.AresSafetyService/RequestEmergencyStop', request_serializer=ares__safety__service__pb2.EmergencyStopRequest.SerializeToString, response_deserializer=ares__safety__service__pb2.EmergencyStopResponse.FromString, _registered_method=True)

class AresSafetyServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RequestEmergencyStop(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_AresSafetyServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'RequestEmergencyStop': grpc.unary_unary_rpc_method_handler(servicer.RequestEmergencyStop, request_deserializer=ares__safety__service__pb2.EmergencyStopRequest.FromString, response_serializer=ares__safety__service__pb2.EmergencyStopResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.services.AresSafetyService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.services.AresSafetyService', rpc_method_handlers)

class AresSafetyService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RequestEmergencyStop(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresSafetyService/RequestEmergencyStop', ares__safety__service__pb2.EmergencyStopRequest.SerializeToString, ares__safety__service__pb2.EmergencyStopResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)