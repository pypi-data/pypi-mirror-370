"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings
from . import ares_automation_pb2 as ares__automation__pb2
from . import execution_status_messages_pb2 as execution__status__messages__pb2
from . import execution_summary_messages_pb2 as execution__summary__messages__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from . import project_pb2 as project__pb2
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
    raise RuntimeError(f'The grpc package installed is at version {GRPC_VERSION},' + f' but the generated code in ares_automation_pb2_grpc.py depends on' + f' grpcio>={GRPC_GENERATED_VERSION}.' + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}' + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.')

class AresAutomationStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetAllCampaigns = channel.unary_unary('/ares.services.AresAutomation/GetAllCampaigns', request_serializer=ares__automation__pb2.GetAllCampaignsRequest.SerializeToString, response_deserializer=ares__automation__pb2.CampaignsResponse.FromString, _registered_method=True)
        self.GetSingleCampaign = channel.unary_unary('/ares.services.AresAutomation/GetSingleCampaign', request_serializer=ares__automation__pb2.CampaignRequest.SerializeToString, response_deserializer=templates_dot_campaign__template__pb2.CampaignTemplate.FromString, _registered_method=True)
        self.RemoveCampaign = channel.unary_unary('/ares.services.AresAutomation/RemoveCampaign', request_serializer=ares__automation__pb2.CampaignRequest.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.CampaignExists = channel.unary_unary('/ares.services.AresAutomation/CampaignExists', request_serializer=ares__automation__pb2.CampaignRequest.SerializeToString, response_deserializer=google_dot_protobuf_dot_wrappers__pb2.BoolValue.FromString, _registered_method=True)
        self.AddCampaign = channel.unary_unary('/ares.services.AresAutomation/AddCampaign', request_serializer=ares__automation__pb2.AddOrUpdateCampaignRequest.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.UpdateCampaign = channel.unary_unary('/ares.services.AresAutomation/UpdateCampaign', request_serializer=ares__automation__pb2.AddOrUpdateCampaignRequest.SerializeToString, response_deserializer=templates_dot_campaign__template__pb2.CampaignTemplate.FromString, _registered_method=True)
        self.CheckExecutionEligibility = channel.unary_unary('/ares.services.AresAutomation/CheckExecutionEligibility', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__automation__pb2.CheckExecutionEligibilityResponse.FromString, _registered_method=True)
        self.GetAllProjects = channel.unary_unary('/ares.services.AresAutomation/GetAllProjects', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__automation__pb2.ProjectsResponse.FromString, _registered_method=True)
        self.GetProject = channel.unary_unary('/ares.services.AresAutomation/GetProject', request_serializer=ares__automation__pb2.ProjectRequest.SerializeToString, response_deserializer=project__pb2.Project.FromString, _registered_method=True)
        self.RemoveProject = channel.unary_unary('/ares.services.AresAutomation/RemoveProject', request_serializer=ares__automation__pb2.ProjectRequest.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.AddProject = channel.unary_unary('/ares.services.AresAutomation/AddProject', request_serializer=project__pb2.Project.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.GetAllTags = channel.unary_unary('/ares.services.AresAutomation/GetAllTags', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__automation__pb2.TagsResponse.FromString, _registered_method=True)
        self.AddTag = channel.unary_unary('/ares.services.AresAutomation/AddTag', request_serializer=ares__automation__pb2.TagRequest.SerializeToString, response_deserializer=ares__automation__pb2.TagsResponse.FromString, _registered_method=True)
        self.RemoveTag = channel.unary_unary('/ares.services.AresAutomation/RemoveTag', request_serializer=ares__automation__pb2.TagRequest.SerializeToString, response_deserializer=ares__automation__pb2.TagsResponse.FromString, _registered_method=True)
        self.SetCampaignForExecution = channel.unary_unary('/ares.services.AresAutomation/SetCampaignForExecution', request_serializer=ares__automation__pb2.CampaignRequest.SerializeToString, response_deserializer=templates_dot_campaign__template__pb2.CampaignTemplate.FromString, _registered_method=True)
        self.GetCurrentlySelectedCampaign = channel.unary_unary('/ares.services.AresAutomation/GetCurrentlySelectedCampaign', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__automation__pb2.CampaignResponse.FromString, _registered_method=True)
        self.StartExecution = channel.unary_unary('/ares.services.AresAutomation/StartExecution', request_serializer=ares__automation__pb2.StartCampaignRequest.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.StopExecution = channel.unary_unary('/ares.services.AresAutomation/StopExecution', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.PauseExecution = channel.unary_unary('/ares.services.AresAutomation/PauseExecution', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.ResumeExecution = channel.unary_unary('/ares.services.AresAutomation/ResumeExecution', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.GetAssignedStopConditions = channel.unary_unary('/ares.services.AresAutomation/GetAssignedStopConditions', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__automation__pb2.StartStopConditionsResponse.FromString, _registered_method=True)
        self.GetReplanRate = channel.unary_unary('/ares.services.AresAutomation/GetReplanRate', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__automation__pb2.GetReplanRateResponse.FromString, _registered_method=True)
        self.GetFailedStartConditions = channel.unary_unary('/ares.services.AresAutomation/GetFailedStartConditions', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__automation__pb2.StartStopConditionsResponse.FromString, _registered_method=True)
        self.GetPreliminaryFailedStartConditions = channel.unary_unary('/ares.services.AresAutomation/GetPreliminaryFailedStartConditions', request_serializer=templates_dot_campaign__template__pb2.CampaignTemplate.SerializeToString, response_deserializer=ares__automation__pb2.StartStopConditionsResponse.FromString, _registered_method=True)
        self.SetNumExperimentsStopCondition = channel.unary_unary('/ares.services.AresAutomation/SetNumExperimentsStopCondition', request_serializer=ares__automation__pb2.NumExperimentsCondition.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.SetReplanRate = channel.unary_unary('/ares.services.AresAutomation/SetReplanRate', request_serializer=ares__automation__pb2.ReplanRate.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.SetAnalysisResultStopCondition = channel.unary_unary('/ares.services.AresAutomation/SetAnalysisResultStopCondition', request_serializer=ares__automation__pb2.AnalysisResultCondition.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.GetActiveStopCondition = channel.unary_unary('/ares.services.AresAutomation/GetActiveStopCondition', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__automation__pb2.ExperimentStopConditionResponse.FromString, _registered_method=True)
        self.RemoveStopCondition = channel.unary_unary('/ares.services.AresAutomation/RemoveStopCondition', request_serializer=ares__automation__pb2.StartStopCondition.SerializeToString, response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, _registered_method=True)
        self.GetExecutionStatusStream = channel.unary_stream('/ares.services.AresAutomation/GetExecutionStatusStream', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=execution__status__messages__pb2.ExperimentExecutionStatus.FromString, _registered_method=True)
        self.GetStartupExecutionStatusStream = channel.unary_stream('/ares.services.AresAutomation/GetStartupExecutionStatusStream', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=execution__status__messages__pb2.CampaignStartupStatus.FromString, _registered_method=True)
        self.GetCloseoutExecutionStatusStream = channel.unary_stream('/ares.services.AresAutomation/GetCloseoutExecutionStatusStream', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=execution__status__messages__pb2.CampaignCloseoutStatus.FromString, _registered_method=True)
        self.GetCampaignExecutionStatus = channel.unary_unary('/ares.services.AresAutomation/GetCampaignExecutionStatus', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__automation__pb2.CampaignExecutionStatusResponse.FromString, _registered_method=True)
        self.GetCampaignExecutionStateStream = channel.unary_stream('/ares.services.AresAutomation/GetCampaignExecutionStateStream', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=execution__status__messages__pb2.CampaignExecutionState.FromString, _registered_method=True)
        self.GetAvailableCampaignExecutionSummaries = channel.unary_unary('/ares.services.AresAutomation/GetAvailableCampaignExecutionSummaries', request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, response_deserializer=ares__automation__pb2.AvailableCampaignExecutionSummariesResponse.FromString, _registered_method=True)
        self.GetCampaignSummary = channel.unary_unary('/ares.services.AresAutomation/GetCampaignSummary', request_serializer=ares__automation__pb2.CampaignExecutionSummaryRequest.SerializeToString, response_deserializer=execution__summary__messages__pb2.CampaignExecutionSummary.FromString, _registered_method=True)

class AresAutomationServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetAllCampaigns(self, request, context):
        """Campaigns
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetSingleCampaign(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveCampaign(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CampaignExists(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddCampaign(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateCampaign(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CheckExecutionEligibility(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAllProjects(self, request, context):
        """Projects
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetProject(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveProject(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddProject(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAllTags(self, request, context):
        """Tags
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddTag(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveTag(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetCampaignForExecution(self, request, context):
        """Execution
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetCurrentlySelectedCampaign(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StartExecution(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StopExecution(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PauseExecution(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ResumeExecution(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAssignedStopConditions(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetReplanRate(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetFailedStartConditions(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPreliminaryFailedStartConditions(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetNumExperimentsStopCondition(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetReplanRate(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetAnalysisResultStopCondition(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetActiveStopCondition(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveStopCondition(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetExecutionStatusStream(self, request, context):
        """Gets a stream of experiment execution statuses that can be observed in real time as experiment is running
        Works best after grabbing all the execution statuses which then lets you know how many experiments have been run
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetStartupExecutionStatusStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetCloseoutExecutionStatusStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetCampaignExecutionStatus(self, request, context):
        """Gets the current status of a campaign execution assuming one is running
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetCampaignExecutionStateStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetAvailableCampaignExecutionSummaries(self, request, context):
        """Summaries
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetCampaignSummary(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_AresAutomationServicer_to_server(servicer, server):
    rpc_method_handlers = {'GetAllCampaigns': grpc.unary_unary_rpc_method_handler(servicer.GetAllCampaigns, request_deserializer=ares__automation__pb2.GetAllCampaignsRequest.FromString, response_serializer=ares__automation__pb2.CampaignsResponse.SerializeToString), 'GetSingleCampaign': grpc.unary_unary_rpc_method_handler(servicer.GetSingleCampaign, request_deserializer=ares__automation__pb2.CampaignRequest.FromString, response_serializer=templates_dot_campaign__template__pb2.CampaignTemplate.SerializeToString), 'RemoveCampaign': grpc.unary_unary_rpc_method_handler(servicer.RemoveCampaign, request_deserializer=ares__automation__pb2.CampaignRequest.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'CampaignExists': grpc.unary_unary_rpc_method_handler(servicer.CampaignExists, request_deserializer=ares__automation__pb2.CampaignRequest.FromString, response_serializer=google_dot_protobuf_dot_wrappers__pb2.BoolValue.SerializeToString), 'AddCampaign': grpc.unary_unary_rpc_method_handler(servicer.AddCampaign, request_deserializer=ares__automation__pb2.AddOrUpdateCampaignRequest.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'UpdateCampaign': grpc.unary_unary_rpc_method_handler(servicer.UpdateCampaign, request_deserializer=ares__automation__pb2.AddOrUpdateCampaignRequest.FromString, response_serializer=templates_dot_campaign__template__pb2.CampaignTemplate.SerializeToString), 'CheckExecutionEligibility': grpc.unary_unary_rpc_method_handler(servicer.CheckExecutionEligibility, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__automation__pb2.CheckExecutionEligibilityResponse.SerializeToString), 'GetAllProjects': grpc.unary_unary_rpc_method_handler(servicer.GetAllProjects, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__automation__pb2.ProjectsResponse.SerializeToString), 'GetProject': grpc.unary_unary_rpc_method_handler(servicer.GetProject, request_deserializer=ares__automation__pb2.ProjectRequest.FromString, response_serializer=project__pb2.Project.SerializeToString), 'RemoveProject': grpc.unary_unary_rpc_method_handler(servicer.RemoveProject, request_deserializer=ares__automation__pb2.ProjectRequest.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'AddProject': grpc.unary_unary_rpc_method_handler(servicer.AddProject, request_deserializer=project__pb2.Project.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'GetAllTags': grpc.unary_unary_rpc_method_handler(servicer.GetAllTags, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__automation__pb2.TagsResponse.SerializeToString), 'AddTag': grpc.unary_unary_rpc_method_handler(servicer.AddTag, request_deserializer=ares__automation__pb2.TagRequest.FromString, response_serializer=ares__automation__pb2.TagsResponse.SerializeToString), 'RemoveTag': grpc.unary_unary_rpc_method_handler(servicer.RemoveTag, request_deserializer=ares__automation__pb2.TagRequest.FromString, response_serializer=ares__automation__pb2.TagsResponse.SerializeToString), 'SetCampaignForExecution': grpc.unary_unary_rpc_method_handler(servicer.SetCampaignForExecution, request_deserializer=ares__automation__pb2.CampaignRequest.FromString, response_serializer=templates_dot_campaign__template__pb2.CampaignTemplate.SerializeToString), 'GetCurrentlySelectedCampaign': grpc.unary_unary_rpc_method_handler(servicer.GetCurrentlySelectedCampaign, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__automation__pb2.CampaignResponse.SerializeToString), 'StartExecution': grpc.unary_unary_rpc_method_handler(servicer.StartExecution, request_deserializer=ares__automation__pb2.StartCampaignRequest.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'StopExecution': grpc.unary_unary_rpc_method_handler(servicer.StopExecution, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'PauseExecution': grpc.unary_unary_rpc_method_handler(servicer.PauseExecution, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'ResumeExecution': grpc.unary_unary_rpc_method_handler(servicer.ResumeExecution, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'GetAssignedStopConditions': grpc.unary_unary_rpc_method_handler(servicer.GetAssignedStopConditions, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__automation__pb2.StartStopConditionsResponse.SerializeToString), 'GetReplanRate': grpc.unary_unary_rpc_method_handler(servicer.GetReplanRate, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__automation__pb2.GetReplanRateResponse.SerializeToString), 'GetFailedStartConditions': grpc.unary_unary_rpc_method_handler(servicer.GetFailedStartConditions, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__automation__pb2.StartStopConditionsResponse.SerializeToString), 'GetPreliminaryFailedStartConditions': grpc.unary_unary_rpc_method_handler(servicer.GetPreliminaryFailedStartConditions, request_deserializer=templates_dot_campaign__template__pb2.CampaignTemplate.FromString, response_serializer=ares__automation__pb2.StartStopConditionsResponse.SerializeToString), 'SetNumExperimentsStopCondition': grpc.unary_unary_rpc_method_handler(servicer.SetNumExperimentsStopCondition, request_deserializer=ares__automation__pb2.NumExperimentsCondition.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'SetReplanRate': grpc.unary_unary_rpc_method_handler(servicer.SetReplanRate, request_deserializer=ares__automation__pb2.ReplanRate.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'SetAnalysisResultStopCondition': grpc.unary_unary_rpc_method_handler(servicer.SetAnalysisResultStopCondition, request_deserializer=ares__automation__pb2.AnalysisResultCondition.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'GetActiveStopCondition': grpc.unary_unary_rpc_method_handler(servicer.GetActiveStopCondition, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__automation__pb2.ExperimentStopConditionResponse.SerializeToString), 'RemoveStopCondition': grpc.unary_unary_rpc_method_handler(servicer.RemoveStopCondition, request_deserializer=ares__automation__pb2.StartStopCondition.FromString, response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString), 'GetExecutionStatusStream': grpc.unary_stream_rpc_method_handler(servicer.GetExecutionStatusStream, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=execution__status__messages__pb2.ExperimentExecutionStatus.SerializeToString), 'GetStartupExecutionStatusStream': grpc.unary_stream_rpc_method_handler(servicer.GetStartupExecutionStatusStream, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=execution__status__messages__pb2.CampaignStartupStatus.SerializeToString), 'GetCloseoutExecutionStatusStream': grpc.unary_stream_rpc_method_handler(servicer.GetCloseoutExecutionStatusStream, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=execution__status__messages__pb2.CampaignCloseoutStatus.SerializeToString), 'GetCampaignExecutionStatus': grpc.unary_unary_rpc_method_handler(servicer.GetCampaignExecutionStatus, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__automation__pb2.CampaignExecutionStatusResponse.SerializeToString), 'GetCampaignExecutionStateStream': grpc.unary_stream_rpc_method_handler(servicer.GetCampaignExecutionStateStream, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=execution__status__messages__pb2.CampaignExecutionState.SerializeToString), 'GetAvailableCampaignExecutionSummaries': grpc.unary_unary_rpc_method_handler(servicer.GetAvailableCampaignExecutionSummaries, request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString, response_serializer=ares__automation__pb2.AvailableCampaignExecutionSummariesResponse.SerializeToString), 'GetCampaignSummary': grpc.unary_unary_rpc_method_handler(servicer.GetCampaignSummary, request_deserializer=ares__automation__pb2.CampaignExecutionSummaryRequest.FromString, response_serializer=execution__summary__messages__pb2.CampaignExecutionSummary.SerializeToString)}
    generic_handler = grpc.method_handlers_generic_handler('ares.services.AresAutomation', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ares.services.AresAutomation', rpc_method_handlers)

class AresAutomation(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetAllCampaigns(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetAllCampaigns', ares__automation__pb2.GetAllCampaignsRequest.SerializeToString, ares__automation__pb2.CampaignsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetSingleCampaign(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetSingleCampaign', ares__automation__pb2.CampaignRequest.SerializeToString, templates_dot_campaign__template__pb2.CampaignTemplate.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def RemoveCampaign(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/RemoveCampaign', ares__automation__pb2.CampaignRequest.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def CampaignExists(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/CampaignExists', ares__automation__pb2.CampaignRequest.SerializeToString, google_dot_protobuf_dot_wrappers__pb2.BoolValue.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def AddCampaign(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/AddCampaign', ares__automation__pb2.AddOrUpdateCampaignRequest.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def UpdateCampaign(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/UpdateCampaign', ares__automation__pb2.AddOrUpdateCampaignRequest.SerializeToString, templates_dot_campaign__template__pb2.CampaignTemplate.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def CheckExecutionEligibility(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/CheckExecutionEligibility', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__automation__pb2.CheckExecutionEligibilityResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetAllProjects(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetAllProjects', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__automation__pb2.ProjectsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetProject(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetProject', ares__automation__pb2.ProjectRequest.SerializeToString, project__pb2.Project.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def RemoveProject(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/RemoveProject', ares__automation__pb2.ProjectRequest.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def AddProject(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/AddProject', project__pb2.Project.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetAllTags(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetAllTags', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__automation__pb2.TagsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def AddTag(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/AddTag', ares__automation__pb2.TagRequest.SerializeToString, ares__automation__pb2.TagsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def RemoveTag(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/RemoveTag', ares__automation__pb2.TagRequest.SerializeToString, ares__automation__pb2.TagsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def SetCampaignForExecution(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/SetCampaignForExecution', ares__automation__pb2.CampaignRequest.SerializeToString, templates_dot_campaign__template__pb2.CampaignTemplate.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetCurrentlySelectedCampaign(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetCurrentlySelectedCampaign', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__automation__pb2.CampaignResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def StartExecution(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/StartExecution', ares__automation__pb2.StartCampaignRequest.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def StopExecution(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/StopExecution', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def PauseExecution(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/PauseExecution', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def ResumeExecution(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/ResumeExecution', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetAssignedStopConditions(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetAssignedStopConditions', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__automation__pb2.StartStopConditionsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetReplanRate(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetReplanRate', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__automation__pb2.GetReplanRateResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetFailedStartConditions(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetFailedStartConditions', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__automation__pb2.StartStopConditionsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetPreliminaryFailedStartConditions(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetPreliminaryFailedStartConditions', templates_dot_campaign__template__pb2.CampaignTemplate.SerializeToString, ares__automation__pb2.StartStopConditionsResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def SetNumExperimentsStopCondition(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/SetNumExperimentsStopCondition', ares__automation__pb2.NumExperimentsCondition.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def SetReplanRate(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/SetReplanRate', ares__automation__pb2.ReplanRate.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def SetAnalysisResultStopCondition(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/SetAnalysisResultStopCondition', ares__automation__pb2.AnalysisResultCondition.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetActiveStopCondition(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetActiveStopCondition', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__automation__pb2.ExperimentStopConditionResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def RemoveStopCondition(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/RemoveStopCondition', ares__automation__pb2.StartStopCondition.SerializeToString, google_dot_protobuf_dot_empty__pb2.Empty.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetExecutionStatusStream(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/ares.services.AresAutomation/GetExecutionStatusStream', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, execution__status__messages__pb2.ExperimentExecutionStatus.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetStartupExecutionStatusStream(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/ares.services.AresAutomation/GetStartupExecutionStatusStream', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, execution__status__messages__pb2.CampaignStartupStatus.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetCloseoutExecutionStatusStream(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/ares.services.AresAutomation/GetCloseoutExecutionStatusStream', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, execution__status__messages__pb2.CampaignCloseoutStatus.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetCampaignExecutionStatus(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetCampaignExecutionStatus', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__automation__pb2.CampaignExecutionStatusResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetCampaignExecutionStateStream(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_stream(request, target, '/ares.services.AresAutomation/GetCampaignExecutionStateStream', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, execution__status__messages__pb2.CampaignExecutionState.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetAvailableCampaignExecutionSummaries(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetAvailableCampaignExecutionSummaries', google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString, ares__automation__pb2.AvailableCampaignExecutionSummariesResponse.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)

    @staticmethod
    def GetCampaignSummary(request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False, compression=None, wait_for_ready=None, timeout=None, metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ares.services.AresAutomation/GetCampaignSummary', ares__automation__pb2.CampaignExecutionSummaryRequest.SerializeToString, execution__summary__messages__pb2.CampaignExecutionSummary.FromString, options, channel_credentials, insecure, call_credentials, compression, wait_for_ready, timeout, metadata, _registered_method=True)