"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'planning/manual_planner.proto')
_sym_db = _symbol_database.Default()
from .. import ares_struct_pb2 as ares__struct__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dplanning/manual_planner.proto\x12\x17ares.datamodel.planning\x1a\x11ares_struct.proto"\xba\x01\n\x11ManualPlannerSeed\x12M\n\x0eplanner_values\x18\x01 \x01(\x0b23.ares.datamodel.planning.ManualPlannerSetCollectionH\x00\x12E\n\nfile_lines\x18\x02 \x01(\x0b2/.ares.datamodel.planning.ManualPlannerFileLinesH\x00B\x0f\n\rplanner_stuff"]\n\x10ManualPlannerSet\x12I\n\x10parameter_values\x18\x01 \x03(\x0b2/.ares.datamodel.planning.ParameterNameValuePair"P\n\x16ParameterNameValuePair\x12\x0c\n\x04name\x18\x01 \x01(\t\x12(\n\x05value\x18\x02 \x01(\x0b2\x19.ares.datamodel.AresValue"0\n\x16ManualPlannerFileLines\x12\x16\n\x0eplanner_values\x18\x01 \x03(\t"_\n\x1aManualPlannerSetCollection\x12A\n\x0eplanned_values\x18\x01 \x03(\x0b2).ares.datamodel.planning.ManualPlannerSetb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'planning.manual_planner_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_MANUALPLANNERSEED']._serialized_start = 78
    _globals['_MANUALPLANNERSEED']._serialized_end = 264
    _globals['_MANUALPLANNERSET']._serialized_start = 266
    _globals['_MANUALPLANNERSET']._serialized_end = 359
    _globals['_PARAMETERNAMEVALUEPAIR']._serialized_start = 361
    _globals['_PARAMETERNAMEVALUEPAIR']._serialized_end = 441
    _globals['_MANUALPLANNERFILELINES']._serialized_start = 443
    _globals['_MANUALPLANNERFILELINES']._serialized_end = 491
    _globals['_MANUALPLANNERSETCOLLECTION']._serialized_start = 493
    _globals['_MANUALPLANNERSETCOLLECTION']._serialized_end = 588