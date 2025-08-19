"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'execution_status_messages.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fexecution_status_messages.proto\x12\x0eares.datamodel"\xaf\x01\n\x17CampaignExecutionStatus\x12\x13\n\x0bcampaign_id\x18\x01 \x01(\t\x12-\n\x05state\x18\x02 \x01(\x0e2\x1e.ares.datamodel.ExecutionState\x12P\n\x1dexperiment_execution_statuses\x18\x03 \x03(\x0b2).ares.datamodel.ExperimentExecutionStatus"\\\n\x16CampaignExecutionState\x12\x13\n\x0bcampaign_id\x18\x01 \x01(\t\x12-\n\x05state\x18\x02 \x01(\x0e2\x1e.ares.datamodel.ExecutionState"x\n\x19ExperimentExecutionStatus\x12\x15\n\rexperiment_id\x18\x01 \x01(\t\x12D\n\x17step_execution_statuses\x18\x02 \x03(\x0b2#.ares.datamodel.StepExecutionStatus"u\n\x15CampaignStartupStatus\x12\x13\n\x0bcampaign_id\x18\x01 \x01(\t\x12G\n\x1astartup_execution_statuses\x18\x02 \x03(\x0b2#.ares.datamodel.StepExecutionStatus"w\n\x16CampaignCloseoutStatus\x12\x13\n\x0bcampaign_id\x18\x01 \x01(\t\x12H\n\x1bcloseout_execution_statuses\x18\x02 \x03(\x0b2#.ares.datamodel.StepExecutionStatus"\x85\x01\n\x13StepExecutionStatus\x12\x0f\n\x07step_id\x18\x01 \x01(\t\x12\x11\n\tstep_name\x18\x02 \x01(\t\x12J\n\x1acommand_execution_statuses\x18\x03 \x03(\x0b2&.ares.datamodel.CommandExecutionStatus"\x86\x01\n\x16CommandExecutionStatus\x12\x12\n\ncommand_id\x18\x01 \x01(\t\x12\x14\n\x0ccommand_name\x18\x02 \x01(\t\x12\x13\n\x0bdevice_name\x18\x03 \x01(\t\x12-\n\x05state\x18\x04 \x01(\x0e2\x1e.ares.datamodel.ExecutionState*s\n\x0eExecutionState\x12\r\n\tUNDEFINED\x10\x00\x12\r\n\tSUCCEEDED\x10\x01\x12\x0b\n\x07WAITING\x10\x02\x12\x11\n\rAWAITING_USER\x10\x03\x12\x0b\n\x07RUNNING\x10\x04\x12\n\n\x06PAUSED\x10\x05\x12\n\n\x06FAILED\x10\x06b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'execution_status_messages_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_EXECUTIONSTATE']._serialized_start = 958
    _globals['_EXECUTIONSTATE']._serialized_end = 1073
    _globals['_CAMPAIGNEXECUTIONSTATUS']._serialized_start = 52
    _globals['_CAMPAIGNEXECUTIONSTATUS']._serialized_end = 227
    _globals['_CAMPAIGNEXECUTIONSTATE']._serialized_start = 229
    _globals['_CAMPAIGNEXECUTIONSTATE']._serialized_end = 321
    _globals['_EXPERIMENTEXECUTIONSTATUS']._serialized_start = 323
    _globals['_EXPERIMENTEXECUTIONSTATUS']._serialized_end = 443
    _globals['_CAMPAIGNSTARTUPSTATUS']._serialized_start = 445
    _globals['_CAMPAIGNSTARTUPSTATUS']._serialized_end = 562
    _globals['_CAMPAIGNCLOSEOUTSTATUS']._serialized_start = 564
    _globals['_CAMPAIGNCLOSEOUTSTATUS']._serialized_end = 683
    _globals['_STEPEXECUTIONSTATUS']._serialized_start = 686
    _globals['_STEPEXECUTIONSTATUS']._serialized_end = 819
    _globals['_COMMANDEXECUTIONSTATUS']._serialized_start = 822
    _globals['_COMMANDEXECUTIONSTATUS']._serialized_end = 956