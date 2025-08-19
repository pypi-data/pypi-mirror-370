"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'planning/ares_planner.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bplanning/ares_planner.proto\x12\x17ares.datamodel.planning\x1a\x1bgoogle/protobuf/empty.proto"\xbe\x01\n\x0cCapabilities\x12\x14\n\x0cservice_name\x18\x01 \x01(\t\x12\x17\n\x0ftimeout_seconds\x18\x02 \x01(\x03\x12<\n\x12available_planners\x18\x03 \x03(\x0b2 .ares.datamodel.planning.Planner\x12A\n\x10adapter_settings\x18\x04 \x03(\x0b2\'.ares.datamodel.planning.PlannerSetting"X\n\x07Planner\x12\x14\n\x0cplanner_name\x18\x01 \x01(\t\x12\x13\n\x0bdescription\x18\x02 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\t\x12\x11\n\tunique_id\x18\x04 \x01(\t"v\n\x0ePlannerSetting\x12\x14\n\x0csetting_name\x18\x01 \x01(\t\x12<\n\rsetting_value\x18\x02 \x01(\x0b2%.ares.datamodel.planning.SettingValue\x12\x10\n\x08optional\x18\x03 \x01(\x08"\xbe\x01\n\x0cSettingValue\x12\x14\n\nbool_value\x18\x01 \x01(\x08H\x00\x12\x15\n\x0bint32_value\x18\x02 \x01(\x05H\x00\x12\x15\n\x0bint64_value\x18\x03 \x01(\x03H\x00\x12\x15\n\x0bfloat_value\x18\x04 \x01(\x02H\x00\x12\x16\n\x0cdouble_value\x18\x05 \x01(\x01H\x00\x12\x16\n\x0cstring_value\x18\x06 \x01(\tH\x00\x12\x15\n\x0bbytes_value\x18\x07 \x01(\x0cH\x00B\x0c\n\nvalue_data"V\n\x0bPlanRequest\x12G\n\x13planning_parameters\x18\x01 \x03(\x0b2*.ares.datamodel.planning.PlanningParameter"A\n\x0cPlanResponse\x12\x17\n\x0fparameter_names\x18\x01 \x03(\t\x12\x18\n\x10parameter_values\x18\x02 \x03(\x02"\xad\x02\n\x11PlanningParameter\x12\x16\n\x0eparameter_name\x18\x01 \x01(\t\x12\x17\n\x0fparameter_value\x18\x02 \x01(\x01\x12\x15\n\rminimum_value\x18\x03 \x01(\x01\x12\x15\n\rmaximum_value\x18\x04 \x01(\x01\x12\x19\n\x11minimum_precision\x18\x05 \x01(\x01\x12\x19\n\x11parameter_history\x18\x06 \x03(\x01\x12\x11\n\tdata_type\x18\x07 \x01(\t\x123\n\x08metadata\x18\x08 \x01(\x0b2!.ares.datamodel.planning.Metadata\x12\x12\n\nis_planned\x18\t \x01(\x08\x12\x11\n\tis_result\x18\n \x01(\x08\x12\x14\n\x0cplanner_name\x18\x0b \x01(\t"x\n\x10PlannedParameter\x12\x16\n\x0eparameter_name\x18\x01 \x01(\t\x12\x17\n\x0fparameter_value\x18\x02 \x01(\x01\x123\n\x08metadata\x18\x03 \x01(\x0b2!.ares.datamodel.planning.Metadata"!\n\x08Metadata\x12\x15\n\rmetadata_name\x18\x01 \x01(\t2\xbc\x01\n\x0fAresPlannerGrpc\x12T\n\x13RequestCapabilities\x12\x16.google.protobuf.Empty\x1a%.ares.datamodel.planning.Capabilities\x12S\n\x04Plan\x12$.ares.datamodel.planning.PlanRequest\x1a%.ares.datamodel.planning.PlanResponseb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'planning.ares_planner_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_CAPABILITIES']._serialized_start = 86
    _globals['_CAPABILITIES']._serialized_end = 276
    _globals['_PLANNER']._serialized_start = 278
    _globals['_PLANNER']._serialized_end = 366
    _globals['_PLANNERSETTING']._serialized_start = 368
    _globals['_PLANNERSETTING']._serialized_end = 486
    _globals['_SETTINGVALUE']._serialized_start = 489
    _globals['_SETTINGVALUE']._serialized_end = 679
    _globals['_PLANREQUEST']._serialized_start = 681
    _globals['_PLANREQUEST']._serialized_end = 767
    _globals['_PLANRESPONSE']._serialized_start = 769
    _globals['_PLANRESPONSE']._serialized_end = 834
    _globals['_PLANNINGPARAMETER']._serialized_start = 837
    _globals['_PLANNINGPARAMETER']._serialized_end = 1138
    _globals['_PLANNEDPARAMETER']._serialized_start = 1140
    _globals['_PLANNEDPARAMETER']._serialized_end = 1260
    _globals['_METADATA']._serialized_start = 1262
    _globals['_METADATA']._serialized_end = 1295
    _globals['_ARESPLANNERGRPC']._serialized_start = 1298
    _globals['_ARESPLANNERGRPC']._serialized_end = 1486