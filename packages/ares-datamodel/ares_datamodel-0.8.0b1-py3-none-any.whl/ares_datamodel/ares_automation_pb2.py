"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_automation.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from .templates import campaign_template_pb2 as templates_dot_campaign__template__pb2
from . import project_pb2 as project__pb2
from . import execution_status_messages_pb2 as execution__status__messages__pb2
from . import execution_summary_messages_pb2 as execution__summary__messages__pb2
from . import ares_campaign_tag_pb2 as ares__campaign__tag__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15ares_automation.proto\x12\rares.services\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a!templates/campaign_template.proto\x1a\rproject.proto\x1a\x1fexecution_status_messages.proto\x1a execution_summary_messages.proto\x1a\x17ares_campaign_tag.proto":\n\nTagRequest\x12,\n\x03tag\x18\x01 \x01(\x0b2\x1f.ares.datamodel.AresCampaignTag"G\n\x0cTagsResponse\x127\n\x0eavailable_tags\x18\x01 \x03(\x0b2\x1f.ares.datamodel.AresCampaignTag"Z\n\x1aAddOrUpdateCampaignRequest\x12<\n\x08template\x18\x01 \x01(\x0b2*.ares.datamodel.templates.CampaignTemplate" \n\x0bRequestById\x12\x11\n\tunique_id\x18\x01 \x01(\t"M\n\x0fCampaignRequest\x12\x17\n\rcampaign_name\x18\x01 \x01(\tH\x00\x12\x13\n\tunique_id\x18\x02 \x01(\tH\x00B\x0c\n\nidentifier"+\n\x16GetAllCampaignsRequest\x12\x11\n\tfile_path\x18\x01 \x01(\t"[\n\x11CampaignsResponse\x12F\n\x12campaign_templates\x18\x01 \x03(\x0b2*.ares.datamodel.templates.CampaignTemplate"`\n\x10CampaignResponse\x12\x11\n\thas_value\x18\x01 \x01(\x08\x129\n\x05value\x18\x02 \x01(\x0b2*.ares.datamodel.templates.CampaignTemplate"b\n\x14StartCampaignRequest\x12\x12\n\nuser_notes\x18\x01 \x01(\t\x126\n\rcampaign_tags\x18\x02 \x03(\x0b2\x1f.ares.datamodel.AresCampaignTag"&\n\x0eProjectRequest\x12\x14\n\x0cproject_name\x18\x01 \x01(\t"=\n\x10ProjectsResponse\x12)\n\x08projects\x18\x01 \x03(\x0b2\x17.ares.datamodel.Project"Z\n\x1fCampaignExecutionStatusResponse\x127\n\x06status\x18\x01 \x01(\x0b2\'.ares.datamodel.CampaignExecutionStatus"_\n\x1bStartStopConditionsResponse\x12@\n\x15start_stop_conditions\x18\x01 \x03(\x0b2!.ares.services.StartStopCondition"+\n\x15GetReplanRateResponse\x12\x12\n\nReplanRate\x18\x01 \x01(\x05"3\n\x12StartStopCondition\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t" \n\nReplanRate\x12\x12\n\nReplanRate\x18\x01 \x01(\x05"2\n\x17NumExperimentsCondition\x12\x17\n\x0fnum_experiments\x18\x01 \x01(\r"P\n\x1fExperimentStopConditionResponse\x12\x18\n\x10active_condition\x18\x01 \x01(\t\x12\x13\n\x0bdescription\x18\x02 \x01(\t"A\n\x17AnalysisResultCondition\x12\x16\n\x0edesired_result\x18\x01 \x01(\x01\x12\x0e\n\x06leeway\x18\x02 \x01(\x01"\x84\x01\n+AvailableCampaignExecutionSummariesResponse\x12U\n\x1cavailable_campaign_summaries\x18\x01 \x03(\x0b2/.ares.services.CampaignExecutionSummaryMetadata"\x9b\x01\n CampaignExecutionSummaryMetadata\x12\x15\n\rcampaign_name\x18\x01 \x01(\t\x123\n\x0fcompletion_time\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12\x12\n\nsummary_id\x18\x03 \x01(\t\x12\x17\n\x0fnum_experiments\x18\x04 \x01(\x03"5\n\x1fCampaignExecutionSummaryRequest\x12\x12\n\nsummary_id\x18\x01 \x01(\t"G\n!CheckExecutionEligibilityResponse\x12\x13\n\x0bis_eligible\x18\x01 \x01(\x08\x12\r\n\x05error\x18\x02 \x01(\t2\xed\x18\n\x0eAresAutomation\x12Z\n\x0fGetAllCampaigns\x12%.ares.services.GetAllCampaignsRequest\x1a .ares.services.CampaignsResponse\x12_\n\x11GetSingleCampaign\x12\x1e.ares.services.CampaignRequest\x1a*.ares.datamodel.templates.CampaignTemplate\x12H\n\x0eRemoveCampaign\x12\x1e.ares.services.CampaignRequest\x1a\x16.google.protobuf.Empty\x12L\n\x0eCampaignExists\x12\x1e.ares.services.CampaignRequest\x1a\x1a.google.protobuf.BoolValue\x12P\n\x0bAddCampaign\x12).ares.services.AddOrUpdateCampaignRequest\x1a\x16.google.protobuf.Empty\x12g\n\x0eUpdateCampaign\x12).ares.services.AddOrUpdateCampaignRequest\x1a*.ares.datamodel.templates.CampaignTemplate\x12e\n\x19CheckExecutionEligibility\x12\x16.google.protobuf.Empty\x1a0.ares.services.CheckExecutionEligibilityResponse\x12I\n\x0eGetAllProjects\x12\x16.google.protobuf.Empty\x1a\x1f.ares.services.ProjectsResponse\x12D\n\nGetProject\x12\x1d.ares.services.ProjectRequest\x1a\x17.ares.datamodel.Project\x12F\n\rRemoveProject\x12\x1d.ares.services.ProjectRequest\x1a\x16.google.protobuf.Empty\x12=\n\nAddProject\x12\x17.ares.datamodel.Project\x1a\x16.google.protobuf.Empty\x12A\n\nGetAllTags\x12\x16.google.protobuf.Empty\x1a\x1b.ares.services.TagsResponse\x12@\n\x06AddTag\x12\x19.ares.services.TagRequest\x1a\x1b.ares.services.TagsResponse\x12C\n\tRemoveTag\x12\x19.ares.services.TagRequest\x1a\x1b.ares.services.TagsResponse\x12e\n\x17SetCampaignForExecution\x12\x1e.ares.services.CampaignRequest\x1a*.ares.datamodel.templates.CampaignTemplate\x12W\n\x1cGetCurrentlySelectedCampaign\x12\x16.google.protobuf.Empty\x1a\x1f.ares.services.CampaignResponse\x12M\n\x0eStartExecution\x12#.ares.services.StartCampaignRequest\x1a\x16.google.protobuf.Empty\x12?\n\rStopExecution\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Empty\x12@\n\x0ePauseExecution\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Empty\x12A\n\x0fResumeExecution\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Empty\x12_\n\x19GetAssignedStopConditions\x12\x16.google.protobuf.Empty\x1a*.ares.services.StartStopConditionsResponse\x12M\n\rGetReplanRate\x12\x16.google.protobuf.Empty\x1a$.ares.services.GetReplanRateResponse\x12^\n\x18GetFailedStartConditions\x12\x16.google.protobuf.Empty\x1a*.ares.services.StartStopConditionsResponse\x12}\n#GetPreliminaryFailedStartConditions\x12*.ares.datamodel.templates.CampaignTemplate\x1a*.ares.services.StartStopConditionsResponse\x12`\n\x1eSetNumExperimentsStopCondition\x12&.ares.services.NumExperimentsCondition\x1a\x16.google.protobuf.Empty\x12B\n\rSetReplanRate\x12\x19.ares.services.ReplanRate\x1a\x16.google.protobuf.Empty\x12`\n\x1eSetAnalysisResultStopCondition\x12&.ares.services.AnalysisResultCondition\x1a\x16.google.protobuf.Empty\x12`\n\x16GetActiveStopCondition\x12\x16.google.protobuf.Empty\x1a..ares.services.ExperimentStopConditionResponse\x12P\n\x13RemoveStopCondition\x12!.ares.services.StartStopCondition\x1a\x16.google.protobuf.Empty\x12_\n\x18GetExecutionStatusStream\x12\x16.google.protobuf.Empty\x1a).ares.datamodel.ExperimentExecutionStatus0\x01\x12b\n\x1fGetStartupExecutionStatusStream\x12\x16.google.protobuf.Empty\x1a%.ares.datamodel.CampaignStartupStatus0\x01\x12d\n GetCloseoutExecutionStatusStream\x12\x16.google.protobuf.Empty\x1a&.ares.datamodel.CampaignCloseoutStatus0\x01\x12d\n\x1aGetCampaignExecutionStatus\x12\x16.google.protobuf.Empty\x1a..ares.services.CampaignExecutionStatusResponse\x12c\n\x1fGetCampaignExecutionStateStream\x12\x16.google.protobuf.Empty\x1a&.ares.datamodel.CampaignExecutionState0\x01\x12|\n&GetAvailableCampaignExecutionSummaries\x12\x16.google.protobuf.Empty\x1a:.ares.services.AvailableCampaignExecutionSummariesResponse\x12n\n\x12GetCampaignSummary\x12..ares.services.CampaignExecutionSummaryRequest\x1a(.ares.datamodel.CampaignExecutionSummaryb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_automation_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_TAGREQUEST']._serialized_start = 276
    _globals['_TAGREQUEST']._serialized_end = 334
    _globals['_TAGSRESPONSE']._serialized_start = 336
    _globals['_TAGSRESPONSE']._serialized_end = 407
    _globals['_ADDORUPDATECAMPAIGNREQUEST']._serialized_start = 409
    _globals['_ADDORUPDATECAMPAIGNREQUEST']._serialized_end = 499
    _globals['_REQUESTBYID']._serialized_start = 501
    _globals['_REQUESTBYID']._serialized_end = 533
    _globals['_CAMPAIGNREQUEST']._serialized_start = 535
    _globals['_CAMPAIGNREQUEST']._serialized_end = 612
    _globals['_GETALLCAMPAIGNSREQUEST']._serialized_start = 614
    _globals['_GETALLCAMPAIGNSREQUEST']._serialized_end = 657
    _globals['_CAMPAIGNSRESPONSE']._serialized_start = 659
    _globals['_CAMPAIGNSRESPONSE']._serialized_end = 750
    _globals['_CAMPAIGNRESPONSE']._serialized_start = 752
    _globals['_CAMPAIGNRESPONSE']._serialized_end = 848
    _globals['_STARTCAMPAIGNREQUEST']._serialized_start = 850
    _globals['_STARTCAMPAIGNREQUEST']._serialized_end = 948
    _globals['_PROJECTREQUEST']._serialized_start = 950
    _globals['_PROJECTREQUEST']._serialized_end = 988
    _globals['_PROJECTSRESPONSE']._serialized_start = 990
    _globals['_PROJECTSRESPONSE']._serialized_end = 1051
    _globals['_CAMPAIGNEXECUTIONSTATUSRESPONSE']._serialized_start = 1053
    _globals['_CAMPAIGNEXECUTIONSTATUSRESPONSE']._serialized_end = 1143
    _globals['_STARTSTOPCONDITIONSRESPONSE']._serialized_start = 1145
    _globals['_STARTSTOPCONDITIONSRESPONSE']._serialized_end = 1240
    _globals['_GETREPLANRATERESPONSE']._serialized_start = 1242
    _globals['_GETREPLANRATERESPONSE']._serialized_end = 1285
    _globals['_STARTSTOPCONDITION']._serialized_start = 1287
    _globals['_STARTSTOPCONDITION']._serialized_end = 1338
    _globals['_REPLANRATE']._serialized_start = 1340
    _globals['_REPLANRATE']._serialized_end = 1372
    _globals['_NUMEXPERIMENTSCONDITION']._serialized_start = 1374
    _globals['_NUMEXPERIMENTSCONDITION']._serialized_end = 1424
    _globals['_EXPERIMENTSTOPCONDITIONRESPONSE']._serialized_start = 1426
    _globals['_EXPERIMENTSTOPCONDITIONRESPONSE']._serialized_end = 1506
    _globals['_ANALYSISRESULTCONDITION']._serialized_start = 1508
    _globals['_ANALYSISRESULTCONDITION']._serialized_end = 1573
    _globals['_AVAILABLECAMPAIGNEXECUTIONSUMMARIESRESPONSE']._serialized_start = 1576
    _globals['_AVAILABLECAMPAIGNEXECUTIONSUMMARIESRESPONSE']._serialized_end = 1708
    _globals['_CAMPAIGNEXECUTIONSUMMARYMETADATA']._serialized_start = 1711
    _globals['_CAMPAIGNEXECUTIONSUMMARYMETADATA']._serialized_end = 1866
    _globals['_CAMPAIGNEXECUTIONSUMMARYREQUEST']._serialized_start = 1868
    _globals['_CAMPAIGNEXECUTIONSUMMARYREQUEST']._serialized_end = 1921
    _globals['_CHECKEXECUTIONELIGIBILITYRESPONSE']._serialized_start = 1923
    _globals['_CHECKEXECUTIONELIGIBILITYRESPONSE']._serialized_end = 1994
    _globals['_ARESAUTOMATION']._serialized_start = 1997
    _globals['_ARESAUTOMATION']._serialized_end = 5178