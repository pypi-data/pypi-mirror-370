"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from . import ares_planning_pb2 as ares__planning__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from .planning import manual_planner_pb2 as planning_dot_manual__planner__pb2
from .planning import planner_status_pb2 as planning_dot_planner__status__pb2
GRPC_GENERATED_VERSION = '1.74.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in ares_planning_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresPlanningStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetAllPlanners = channel.unary_unary('/ares.messaging.planning.AresPlanning/GetAllPlanners', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__planning__pb2.GetAllPlannersResponse.FromString, _registered_method=True)
        self.GetPlannerCapabilities = channel.unary_unary('/ares.messaging.planning.AresPlanning/GetPlannerCapabilities', request_serializer=ares__planning__pb2.CapabilitiesRequest.SerializeToString, response_deserializer=ares__planning__pb2.CapabilitiesResponse.FromString, _registered_method=True)
        self.GetPlannerSettings = channel.unary_unary('/ares.messaging.planning.AresPlanning/GetPlannerSettings', request_serializer=ares__planning__pb2.PlannerSettingsRequest.SerializeToString, response_deserializer=ares__planning__pb2.PlannerSettingsResponse.FromString, _registered_method=True)
        self.GetPlannerStatus = channel.unary_unary('/ares.messaging.planning.AresPlanning/GetPlannerStatus', request_serializer=ares__planning__pb2.PlannerStatusRequest.SerializeToString, response_deserializer=planning_dot_planner__status__pb2.PlannerStatus.FromString, _registered_method=True)
        self.ActivatePlanner = channel.unary_unary('/ares.messaging.planning.AresPlanning/ActivatePlanner', request_serializer=ares__planning__pb2.PlannerActivationRequest.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.SeedManualPlanner = channel.unary_unary('/ares.messaging.planning.AresPlanning/SeedManualPlanner', request_serializer=planning_dot_manual__planner__pb2.ManualPlannerSeed.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.GetManualPlannerSeed = channel.unary_unary('/ares.messaging.planning.AresPlanning/GetManualPlannerSeed', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=planning_dot_manual__planner__pb2.ManualPlannerSetCollection.FromString, _registered_method=True)
        self.ResetManualPlanner = channel.unary_unary('/ares.messaging.planning.AresPlanning/ResetManualPlanner', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.AddPlanner = channel.unary_unary('/ares.messaging.planning.AresPlanning/AddPlanner', request_serializer=ares__planning__pb2.GenericPlanner.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.RemovePlanner = channel.unary_unary('/ares.messaging.planning.AresPlanning/RemovePlanner', request_serializer=ares__planning__pb2.GenericPlanner.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.UpdatePlanner = channel.unary_unary('/ares.messaging.planning.AresPlanning/UpdatePlanner', request_serializer=ares__planning__pb2.GenericPlanner.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)

class AresPlanningServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetAllPlanners(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPlannerCapabilities(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPlannerSettings(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPlannerStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ActivatePlanner(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SeedManualPlanner(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetManualPlannerSeed(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ResetManualPlanner(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddPlanner(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemovePlanner(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdatePlanner(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_AresPlanningServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetAllPlanners': grpc.unary_unary_rpc_method_handler(servicer.GetAllPlanners, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__planning__pb2.GetAllPlannersResponse.SerializeToString), 'GetPlannerCapabilities': grpc.unary_unary_rpc_method_handler(servicer.GetPlannerCapabilities, request_deserializer=ares__planning__pb2.CapabilitiesRequest.FromString, response_serializer=ares__planning__pb2.CapabilitiesResponse.SerializeToString), 'GetPlannerSettings': grpc.unary_unary_rpc_method_handler(servicer.GetPlannerSettings, request_deserializer=ares__planning__pb2.PlannerSettingsRequest.FromString, response_serializer=ares__planning__pb2.PlannerSettingsResponse.SerializeToString), 'GetPlannerStatus': grpc.unary_unary_rpc_method_handler(servicer.GetPlannerStatus, request_deserializer=ares__planning__pb2.PlannerStatusRequest.FromString, response_serializer=planning_dot_planner__status__pb2.PlannerStatus.SerializeToString), 'ActivatePlanner': grpc.unary_unary_rpc_method_handler(servicer.ActivatePlanner, request_deserializer=ares__planning__pb2.PlannerActivationRequest.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'SeedManualPlanner': grpc.unary_unary_rpc_method_handler(servicer.SeedManualPlanner, request_deserializer=planning_dot_manual__planner__pb2.ManualPlannerSeed.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'GetManualPlannerSeed': grpc.unary_unary_rpc_method_handler(servicer.GetManualPlannerSeed, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=planning_dot_manual__planner__pb2.ManualPlannerSetCollection.SerializeToString), 'ResetManualPlanner': grpc.unary_unary_rpc_method_handler(servicer.ResetManualPlanner, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'AddPlanner': grpc.unary_unary_rpc_method_handler(servicer.AddPlanner, request_deserializer=ares__planning__pb2.GenericPlanner.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'RemovePlanner': grpc.unary_unary_rpc_method_handler(servicer.RemovePlanner, request_deserializer=ares__planning__pb2.GenericPlanner.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'UpdatePlanner': grpc.unary_unary_rpc_method_handler(servicer.UpdatePlanner, request_deserializer=ares__planning__pb2.GenericPlanner.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.messaging.planning.AresPlanning', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.messaging.planning.AresPlanning', rpc_method_handlers)

class AresPlanning(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetAllPlanners(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.messaging.planning.AresPlanning/GetAllPlanners', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__planning__pb2.GetAllPlannersResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetPlannerCapabilities(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.messaging.planning.AresPlanning/GetPlannerCapabilities', ares__planning__pb2.CapabilitiesRequest.SerializeToString, ares__planning__pb2.CapabilitiesResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetPlannerSettings(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.messaging.planning.AresPlanning/GetPlannerSettings', ares__planning__pb2.PlannerSettingsRequest.SerializeToString, ares__planning__pb2.PlannerSettingsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetPlannerStatus(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.messaging.planning.AresPlanning/GetPlannerStatus', ares__planning__pb2.PlannerStatusRequest.SerializeToString, planning_dot_planner__status__pb2.PlannerStatus.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ActivatePlanner(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.messaging.planning.AresPlanning/ActivatePlanner', ares__planning__pb2.PlannerActivationRequest.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def SeedManualPlanner(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.messaging.planning.AresPlanning/SeedManualPlanner', planning_dot_manual__planner__pb2.ManualPlannerSeed.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetManualPlannerSeed(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.messaging.planning.AresPlanning/GetManualPlannerSeed', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, planning_dot_manual__planner__pb2.ManualPlannerSetCollection.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ResetManualPlanner(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.messaging.planning.AresPlanning/ResetManualPlanner', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def AddPlanner(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.messaging.planning.AresPlanning/AddPlanner', ares__planning__pb2.GenericPlanner.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def RemovePlanner(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.messaging.planning.AresPlanning/RemovePlanner', ares__planning__pb2.GenericPlanner.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def UpdatePlanner(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.messaging.planning.AresPlanning/UpdatePlanner', ares__planning__pb2.GenericPlanner.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)