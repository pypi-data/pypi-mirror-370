"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from .analyzing import analyzer_settings_pb2 as analyzing_dot_analyzer__settings__pb2
from . import ares_analyzer_management_service_pb2 as ares__analyzer__management__service__pb2
from . import ares_struct_pb2 as ares__struct__pb2
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
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in ares_analyzer_management_service_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresAnalyzerManagementServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetAllAnalyzers = channel.unary_unary('/ares.services.AresAnalyzerManagementService/GetAllAnalyzers', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__analyzer__management__service__pb2.GetAllAnalyzersResponse.FromString, _registered_method=True)
        self.AddRemoteAnalyzer = channel.unary_unary('/ares.services.AresAnalyzerManagementService/AddRemoteAnalyzer', request_serializer=ares__analyzer__management__service__pb2.AddRemoteAnalyzerRequest.SerializeToString, response_deserializer=ares__analyzer__management__service__pb2.AddRemoteAnalyzerResponse.FromString, _registered_method=True)
        self.UpdateRemoteAnalyzer = channel.unary_unary('/ares.services.AresAnalyzerManagementService/UpdateRemoteAnalyzer', request_serializer=ares__analyzer__management__service__pb2.UpdateRemoteAnalyzerRequest.SerializeToString, response_deserializer=ares__analyzer__management__service__pb2.UpdateRemoteAnalyzerResponse.FromString, _registered_method=True)
        self.RemoveRemoteAnalyzer = channel.unary_unary('/ares.services.AresAnalyzerManagementService/RemoveRemoteAnalyzer', request_serializer=ares__analyzer__management__service__pb2.RemoveRemoteAnalyzerRequest.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.GetState = channel.unary_unary('/ares.services.AresAnalyzerManagementService/GetState', request_serializer=ares__analyzer__management__service__pb2.AnalyzerStateRequest.SerializeToString, response_deserializer=ares__analyzer__management__service__pb2.AnalyzerStateResponse.FromString, _registered_method=True)
        self.GetInfo = channel.unary_unary('/ares.services.AresAnalyzerManagementService/GetInfo', request_serializer=ares__analyzer__management__service__pb2.AnalyzerInfoRequest.SerializeToString, response_deserializer=ares__analyzer__management__service__pb2.AnalyzerInfoResponse.FromString, _registered_method=True)
        self.SetAnalyzerSettings = channel.unary_unary('/ares.services.AresAnalyzerManagementService/SetAnalyzerSettings', request_serializer=analyzing_dot_analyzer__settings__pb2.AnalyzerSettings.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.GetAnalyzerSettings = channel.unary_unary('/ares.services.AresAnalyzerManagementService/GetAnalyzerSettings', request_serializer=ares__analyzer__management__service__pb2.AnalyzerSettingsRequest.SerializeToString, response_deserializer=ares__struct__pb2.AresStruct.FromString, _registered_method=True)

class AresAnalyzerManagementServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetAllAnalyzers(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddRemoteAnalyzer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateRemoteAnalyzer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveRemoteAnalyzer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetState(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetAnalyzerSettings(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAnalyzerSettings(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_AresAnalyzerManagementServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetAllAnalyzers': grpc.unary_unary_rpc_method_handler(servicer.GetAllAnalyzers, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__analyzer__management__service__pb2.GetAllAnalyzersResponse.SerializeToString), 'AddRemoteAnalyzer': grpc.unary_unary_rpc_method_handler(servicer.AddRemoteAnalyzer, request_deserializer=ares__analyzer__management__service__pb2.AddRemoteAnalyzerRequest.FromString, response_serializer=ares__analyzer__management__service__pb2.AddRemoteAnalyzerResponse.SerializeToString), 'UpdateRemoteAnalyzer': grpc.unary_unary_rpc_method_handler(servicer.UpdateRemoteAnalyzer, request_deserializer=ares__analyzer__management__service__pb2.UpdateRemoteAnalyzerRequest.FromString, response_serializer=ares__analyzer__management__service__pb2.UpdateRemoteAnalyzerResponse.SerializeToString), 'RemoveRemoteAnalyzer': grpc.unary_unary_rpc_method_handler(servicer.RemoveRemoteAnalyzer, request_deserializer=ares__analyzer__management__service__pb2.RemoveRemoteAnalyzerRequest.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'GetState': grpc.unary_unary_rpc_method_handler(servicer.GetState, request_deserializer=ares__analyzer__management__service__pb2.AnalyzerStateRequest.FromString, response_serializer=ares__analyzer__management__service__pb2.AnalyzerStateResponse.SerializeToString), 'GetInfo': grpc.unary_unary_rpc_method_handler(servicer.GetInfo, request_deserializer=ares__analyzer__management__service__pb2.AnalyzerInfoRequest.FromString, response_serializer=ares__analyzer__management__service__pb2.AnalyzerInfoResponse.SerializeToString), 'SetAnalyzerSettings': grpc.unary_unary_rpc_method_handler(servicer.SetAnalyzerSettings, request_deserializer=analyzing_dot_analyzer__settings__pb2.AnalyzerSettings.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'GetAnalyzerSettings': grpc.unary_unary_rpc_method_handler(servicer.GetAnalyzerSettings, request_deserializer=ares__analyzer__management__service__pb2.AnalyzerSettingsRequest.FromString, response_serializer=ares__struct__pb2.AresStruct.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.services.AresAnalyzerManagementService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.services.AresAnalyzerManagementService', rpc_method_handlers)

class AresAnalyzerManagementService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetAllAnalyzers(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAnalyzerManagementService/GetAllAnalyzers', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__analyzer__management__service__pb2.GetAllAnalyzersResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def AddRemoteAnalyzer(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAnalyzerManagementService/AddRemoteAnalyzer', ares__analyzer__management__service__pb2.AddRemoteAnalyzerRequest.SerializeToString, ares__analyzer__management__service__pb2.AddRemoteAnalyzerResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def UpdateRemoteAnalyzer(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAnalyzerManagementService/UpdateRemoteAnalyzer', ares__analyzer__management__service__pb2.UpdateRemoteAnalyzerRequest.SerializeToString, ares__analyzer__management__service__pb2.UpdateRemoteAnalyzerResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def RemoveRemoteAnalyzer(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAnalyzerManagementService/RemoveRemoteAnalyzer', ares__analyzer__management__service__pb2.RemoveRemoteAnalyzerRequest.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetState(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAnalyzerManagementService/GetState', ares__analyzer__management__service__pb2.AnalyzerStateRequest.SerializeToString, ares__analyzer__management__service__pb2.AnalyzerStateResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetInfo(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAnalyzerManagementService/GetInfo', ares__analyzer__management__service__pb2.AnalyzerInfoRequest.SerializeToString, ares__analyzer__management__service__pb2.AnalyzerInfoResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def SetAnalyzerSettings(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAnalyzerManagementService/SetAnalyzerSettings', analyzing_dot_analyzer__settings__pb2.AnalyzerSettings.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetAnalyzerSettings(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAnalyzerManagementService/GetAnalyzerSettings', ares__analyzer__management__service__pb2.AnalyzerSettingsRequest.SerializeToString, ares__struct__pb2.AresStruct.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)