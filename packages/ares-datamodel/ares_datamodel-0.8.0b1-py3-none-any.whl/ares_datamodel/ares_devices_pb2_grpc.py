"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from . import ares_devices_pb2 as ares__devices__pb2
from .device import device_status_pb2 as device_dot_device__status__pb2
from . import device_command_result_pb2 as device__command__result__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from .templates import command_template_pb2 as templates_dot_command__template__pb2
GRPC_GENERATED_VERSION = '1.74.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False
try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True
if _version_not_supported:
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in ares_devices_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresDevicesStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ListAresDevices = channel.unary_unary('/ares.services.device.AresDevices/ListAresDevices', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__devices__pb2.ListAresDevicesResponse.FromString, _registered_method=True)
        self.GetServerSerialPorts = channel.unary_unary('/ares.services.device.AresDevices/GetServerSerialPorts', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__devices__pb2.ListServerSerialPortsResponse.FromString, _registered_method=True)
        self.GetDeviceStatus = channel.unary_unary('/ares.services.device.AresDevices/GetDeviceStatus', request_serializer=ares__devices__pb2.DeviceStatusRequest.SerializeToString, response_deserializer=device_dot_device__status__pb2.DeviceStatus.FromString, _registered_method=True)
        self.GetCommandMetadatas = channel.unary_unary('/ares.services.device.AresDevices/GetCommandMetadatas', request_serializer=ares__devices__pb2.CommandMetadatasRequest.SerializeToString, response_deserializer=ares__devices__pb2.CommandMetadatasResponse.FromString, _registered_method=True)
        self.ExecuteCommand = channel.unary_unary('/ares.services.device.AresDevices/ExecuteCommand', request_serializer=templates_dot_command__template__pb2.CommandTemplate.SerializeToString, response_deserializer=device__command__result__pb2.DeviceCommandResult.FromString, _registered_method=True)
        self.GetAllDeviceConfigs = channel.unary_unary('/ares.services.device.AresDevices/GetAllDeviceConfigs', request_serializer=ares__devices__pb2.DeviceConfigRequest.SerializeToString, response_deserializer=ares__devices__pb2.DeviceConfigResponse.FromString, _registered_method=True)
        self.Activate = channel.unary_unary('/ares.services.device.AresDevices/Activate', request_serializer=ares__devices__pb2.DeviceActivateRequest.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)

class AresDevicesServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ListAresDevices(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetServerSerialPorts(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetDeviceStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetCommandMetadatas(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ExecuteCommand(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAllDeviceConfigs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Activate(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_AresDevicesServicer_to_server(servicer, server):
    rpc_method_handlers = {'ListAresDevices': grpc.unary_unary_rpc_method_handler(servicer.ListAresDevices, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__devices__pb2.ListAresDevicesResponse.SerializeToString), 'GetServerSerialPorts': grpc.unary_unary_rpc_method_handler(servicer.GetServerSerialPorts, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__devices__pb2.ListServerSerialPortsResponse.SerializeToString), 'GetDeviceStatus': grpc.unary_unary_rpc_method_handler(servicer.GetDeviceStatus, request_deserializer=ares__devices__pb2.DeviceStatusRequest.FromString, response_serializer=device_dot_device__status__pb2.DeviceStatus.SerializeToString), 'GetCommandMetadatas': grpc.unary_unary_rpc_method_handler(servicer.GetCommandMetadatas, request_deserializer=ares__devices__pb2.CommandMetadatasRequest.FromString, response_serializer=ares__devices__pb2.CommandMetadatasResponse.SerializeToString), 'ExecuteCommand': grpc.unary_unary_rpc_method_handler(servicer.ExecuteCommand, request_deserializer=templates_dot_command__template__pb2.CommandTemplate.FromString, response_serializer=device__command__result__pb2.DeviceCommandResult.SerializeToString), 'GetAllDeviceConfigs': grpc.unary_unary_rpc_method_handler(servicer.GetAllDeviceConfigs, request_deserializer=ares__devices__pb2.DeviceConfigRequest.FromString, response_serializer=ares__devices__pb2.DeviceConfigResponse.SerializeToString), 'Activate': grpc.unary_unary_rpc_method_handler(servicer.Activate, request_deserializer=ares__devices__pb2.DeviceActivateRequest.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.services.device.AresDevices', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.services.device.AresDevices', rpc_method_handlers)

class AresDevices(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ListAresDevices(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.device.AresDevices/ListAresDevices', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__devices__pb2.ListAresDevicesResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetServerSerialPorts(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.device.AresDevices/GetServerSerialPorts', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__devices__pb2.ListServerSerialPortsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetDeviceStatus(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.device.AresDevices/GetDeviceStatus', ares__devices__pb2.DeviceStatusRequest.SerializeToString, device_dot_device__status__pb2.DeviceStatus.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetCommandMetadatas(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.device.AresDevices/GetCommandMetadatas', ares__devices__pb2.CommandMetadatasRequest.SerializeToString, ares__devices__pb2.CommandMetadatasResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ExecuteCommand(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.device.AresDevices/ExecuteCommand', templates_dot_command__template__pb2.CommandTemplate.SerializeToString, device__command__result__pb2.DeviceCommandResult.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetAllDeviceConfigs(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.device.AresDevices/GetAllDeviceConfigs', ares__devices__pb2.DeviceConfigRequest.SerializeToString, ares__devices__pb2.DeviceConfigResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def Activate(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.device.AresDevices/Activate', ares__devices__pb2.DeviceActivateRequest.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)