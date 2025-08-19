"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from ..planning import ares_planner_pb2 as planning_dot_ares__planner__pb2
GRPC_GENERATED_VERSION = '1.74.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in planning/ares_planner_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresPlannerGrpcStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RequestCapabilities = channel.unary_unary('/ares.datamodel.planning.AresPlannerGrpc/RequestCapabilities', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=planning_dot_ares__planner__pb2.Capabilities.FromString, _registered_method=True)
        self.Plan = channel.unary_unary('/ares.datamodel.planning.AresPlannerGrpc/Plan', request_serializer=planning_dot_ares__planner__pb2.PlanRequest.SerializeToString, response_deserializer=planning_dot_ares__planner__pb2.PlanResponse.FromString, _registered_method=True)

class AresPlannerGrpcServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RequestCapabilities(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Plan(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_AresPlannerGrpcServicer_to_server(servicer, server):
    rpc_method_handlers = {'RequestCapabilities': grpc.unary_unary_rpc_method_handler(servicer.RequestCapabilities, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=planning_dot_ares__planner__pb2.Capabilities.SerializeToString), 'Plan': grpc.unary_unary_rpc_method_handler(servicer.Plan, request_deserializer=planning_dot_ares__planner__pb2.PlanRequest.FromString, response_serializer=planning_dot_ares__planner__pb2.PlanResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.datamodel.planning.AresPlannerGrpc', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.datamodel.planning.AresPlannerGrpc', rpc_method_handlers)

class AresPlannerGrpc(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RequestCapabilities(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.planning.AresPlannerGrpc/RequestCapabilities', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, planning_dot_ares__planner__pb2.Capabilities.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def Plan(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.datamodel.planning.AresPlannerGrpc/Plan', planning_dot_ares__planner__pb2.PlanRequest.SerializeToString, planning_dot_ares__planner__pb2.PlanResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)