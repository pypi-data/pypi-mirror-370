"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from . import ares_validation_pb2 as ares__validation__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from .templates import campaign_template_pb2 as templates_dot_campaign__template__pb2
GRPC_GENERATED_VERSION = '1.74.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in ares_validation_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresValidationStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ValidateFullCampaign = channel.unary_unary('/ares.services.AresValidation/ValidateFullCampaign', request_serializer=templates_dot_campaign__template__pb2.CampaignTemplate.SerializeToString, response_deserializer=ares__validation__pb2.ValidationResponse.FromString, _registered_method=True)
        self.ValidateAnalyzerSelection = channel.unary_unary('/ares.services.AresValidation/ValidateAnalyzerSelection', request_serializer=ares__validation__pb2.AnalyzerValidationRequest.SerializeToString, response_deserializer=ares__validation__pb2.ValidationResponse.FromString, _registered_method=True)
        self.ValidateRegisteredDevices = channel.unary_unary('/ares.services.AresValidation/ValidateRegisteredDevices', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__validation__pb2.ValidationResponse.FromString, _registered_method=True)

class AresValidationServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ValidateFullCampaign(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ValidateAnalyzerSelection(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ValidateRegisteredDevices(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_AresValidationServicer_to_server(servicer, server):
    rpc_method_handlers = {'ValidateFullCampaign': grpc.unary_unary_rpc_method_handler(servicer.ValidateFullCampaign, request_deserializer=templates_dot_campaign__template__pb2.CampaignTemplate.FromString, response_serializer=ares__validation__pb2.ValidationResponse.SerializeToString), 'ValidateAnalyzerSelection': grpc.unary_unary_rpc_method_handler(servicer.ValidateAnalyzerSelection, request_deserializer=ares__validation__pb2.AnalyzerValidationRequest.FromString, response_serializer=ares__validation__pb2.ValidationResponse.SerializeToString), 'ValidateRegisteredDevices': grpc.unary_unary_rpc_method_handler(servicer.ValidateRegisteredDevices, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__validation__pb2.ValidationResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.services.AresValidation', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.services.AresValidation', rpc_method_handlers)

class AresValidation(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ValidateFullCampaign(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresValidation/ValidateFullCampaign', templates_dot_campaign__template__pb2.CampaignTemplate.SerializeToString, ares__validation__pb2.ValidationResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ValidateAnalyzerSelection(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresValidation/ValidateAnalyzerSelection', ares__validation__pb2.AnalyzerValidationRequest.SerializeToString, ares__validation__pb2.ValidationResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ValidateRegisteredDevices(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresValidation/ValidateRegisteredDevices', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__validation__pb2.ValidationResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)