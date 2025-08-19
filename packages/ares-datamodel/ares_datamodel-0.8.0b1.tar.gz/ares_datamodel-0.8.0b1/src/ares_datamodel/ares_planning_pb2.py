"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'ares_planning.proto')
_sym_db = _symbol_database.Default()
from . import planner_adapter_info_pb2 as planner__adapter__info__pb2
from .planning import manual_planner_pb2 as planning_dot_manual__planner__pb2
from .planning import ares_planner_pb2 as planning_dot_ares__planner__pb2
from .planning import planner_status_pb2 as planning_dot_planner__status__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13ares_planning.proto\x12\x17ares.messaging.planning\x1a\x1aplanner_adapter_info.proto\x1a\x1dplanning/manual_planner.proto\x1a\x1bplanning/ares_planner.proto\x1a\x1dplanning/planner_status.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x1bgoogle/protobuf/empty.proto"N\n\x16GetAllPlannersResponse\x124\n\x08planners\x18\x01 \x03(\x0b2".ares.datamodel.PlannerAdapterInfo"+\n\x13CapabilitiesRequest\x12\x14\n\x0cadapter_name\x18\x01 \x01(\t",\n\x14PlannerStatusRequest\x12\x14\n\x0cadapter_name\x18\x01 \x01(\t"0\n\x18PlannerActivationRequest\x12\x14\n\x0cadapter_name\x18\x01 \x01(\t"D\n\x16PlannerSettingsRequest\x12\x14\n\x0cservice_name\x18\x01 \x01(\t\x12\x14\n\x0cplanner_name\x18\x02 \x01(\t"T\n\x17PlannerSettingsResponse\x129\n\x08settings\x18\x01 \x03(\x0b2\'.ares.datamodel.planning.PlannerSetting"Z\n\x14CapabilitiesResponse\x12B\n\x12planner_capability\x18\x01 \x03(\x0b2&.ares.messaging.planning.PlannerOption"@\n\x0eGenericPlanner\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x14\n\x07address\x18\x02 \x01(\tH\x00\x88\x01\x01B\n\n\x08_address"C\n\rPlannerOption\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0bdescription\x18\x02 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\t2\x99\x08\n\x0cAresPlanning\x12Y\n\x0eGetAllPlanners\x12\x16.google.protobuf.Empty\x1a/.ares.messaging.planning.GetAllPlannersResponse\x12u\n\x16GetPlannerCapabilities\x12,.ares.messaging.planning.CapabilitiesRequest\x1a-.ares.messaging.planning.CapabilitiesResponse\x12w\n\x12GetPlannerSettings\x12/.ares.messaging.planning.PlannerSettingsRequest\x1a0.ares.messaging.planning.PlannerSettingsResponse\x12i\n\x10GetPlannerStatus\x12-.ares.messaging.planning.PlannerStatusRequest\x1a&.ares.datamodel.planning.PlannerStatus\x12\\\n\x0fActivatePlanner\x121.ares.messaging.planning.PlannerActivationRequest\x1a\x16.google.protobuf.Empty\x12W\n\x11SeedManualPlanner\x12*.ares.datamodel.planning.ManualPlannerSeed\x1a\x16.google.protobuf.Empty\x12c\n\x14GetManualPlannerSeed\x12\x16.google.protobuf.Empty\x1a3.ares.datamodel.planning.ManualPlannerSetCollection\x12D\n\x12ResetManualPlanner\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Empty\x12M\n\nAddPlanner\x12\'.ares.messaging.planning.GenericPlanner\x1a\x16.google.protobuf.Empty\x12P\n\rRemovePlanner\x12\'.ares.messaging.planning.GenericPlanner\x1a\x16.google.protobuf.Empty\x12P\n\rUpdatePlanner\x12\'.ares.messaging.planning.GenericPlanner\x1a\x16.google.protobuf.Emptyb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ares_planning_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_GETALLPLANNERSRESPONSE']._serialized_start = 228
    _globals['_GETALLPLANNERSRESPONSE']._serialized_end = 306
    _globals['_CAPABILITIESREQUEST']._serialized_start = 308
    _globals['_CAPABILITIESREQUEST']._serialized_end = 351
    _globals['_PLANNERSTATUSREQUEST']._serialized_start = 353
    _globals['_PLANNERSTATUSREQUEST']._serialized_end = 397
    _globals['_PLANNERACTIVATIONREQUEST']._serialized_start = 399
    _globals['_PLANNERACTIVATIONREQUEST']._serialized_end = 447
    _globals['_PLANNERSETTINGSREQUEST']._serialized_start = 449
    _globals['_PLANNERSETTINGSREQUEST']._serialized_end = 517
    _globals['_PLANNERSETTINGSRESPONSE']._serialized_start = 519
    _globals['_PLANNERSETTINGSRESPONSE']._serialized_end = 603
    _globals['_CAPABILITIESRESPONSE']._serialized_start = 605
    _globals['_CAPABILITIESRESPONSE']._serialized_end = 695
    _globals['_GENERICPLANNER']._serialized_start = 697
    _globals['_GENERICPLANNER']._serialized_end = 761
    _globals['_PLANNEROPTION']._serialized_start = 763
    _globals['_PLANNEROPTION']._serialized_end = 830
    _globals['_ARESPLANNING']._serialized_start = 833
    _globals['_ARESPLANNING']._serialized_end = 1882