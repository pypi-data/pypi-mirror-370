"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from .analyzing import analysis_pb2 as analyzing_dot_analysis__pb2
from . import ares_analysis_service_pb2 as ares__analysis__service__pb2
from . import validation_result_pb2 as validation__result__pb2
GRPC_GENERATED_VERSION = '1.74.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in ares_analysis_service_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresAnalysisServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ValidateInputs = channel.unary_unary('/ares.services.AresAnalysisService/ValidateInputs', request_serializer=ares__analysis__service__pb2.InputValidationRequest.SerializeToString, response_deserializer=validation__result__pb2.ValidationResult.FromString, _registered_method=True)
        self.Analyze = channel.unary_unary('/ares.services.AresAnalysisService/Analyze', request_serializer=ares__analysis__service__pb2.AnalysisRequest.SerializeToString, response_deserializer=analyzing_dot_analysis__pb2.Analysis.FromString, _registered_method=True)
        self.GetAnalyzerParameters = channel.unary_unary('/ares.services.AresAnalysisService/GetAnalyzerParameters', request_serializer=ares__analysis__service__pb2.AnalyzerParametersRequest.SerializeToString, response_deserializer=ares__analysis__service__pb2.AnalyzerParametersResponse.FromString, _registered_method=True)

class AresAnalysisServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ValidateInputs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Analyze(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAnalyzerParameters(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_AresAnalysisServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {'ValidateInputs': grpc.unary_unary_rpc_method_handler(servicer.ValidateInputs, request_deserializer=ares__analysis__service__pb2.InputValidationRequest.FromString, response_serializer=validation__result__pb2.ValidationResult.SerializeToString), 'Analyze': grpc.unary_unary_rpc_method_handler(servicer.Analyze, request_deserializer=ares__analysis__service__pb2.AnalysisRequest.FromString, response_serializer=analyzing_dot_analysis__pb2.Analysis.SerializeToString), 'GetAnalyzerParameters': grpc.unary_unary_rpc_method_handler(servicer.GetAnalyzerParameters, request_deserializer=ares__analysis__service__pb2.AnalyzerParametersRequest.FromString, response_serializer=ares__analysis__service__pb2.AnalyzerParametersResponse.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.services.AresAnalysisService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.services.AresAnalysisService', rpc_method_handlers)

class AresAnalysisService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ValidateInputs(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAnalysisService/ValidateInputs', ares__analysis__service__pb2.InputValidationRequest.SerializeToString, validation__result__pb2.ValidationResult.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def Analyze(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAnalysisService/Analyze', ares__analysis__service__pb2.AnalysisRequest.SerializeToString, analyzing_dot_analysis__pb2.Analysis.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetAnalyzerParameters(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAnalysisService/GetAnalyzerParameters', ares__analysis__service__pb2.AnalyzerParametersRequest.SerializeToString, ares__analysis__service__pb2.AnalyzerParametersResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)