"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'templates/planner_allocation.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from .. import planner_adapter_info_pb2 as planner__adapter__info__pb2
from ..templates import parameter_metadata_pb2 as templates_dot_parameter__metadata__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n"templates/planner_allocation.proto\x12\x18ares.datamodel.templates\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x1aplanner_adapter_info.proto\x1a"templates/parameter_metadata.proto"\x9b\x01\n\x11PlannerAllocation\x12\x11\n\tunique_id\x18\x01 \x01(\t\x123\n\x07planner\x18\x02 \x01(\x0b2".ares.datamodel.PlannerAdapterInfo\x12>\n\tparameter\x18\x03 \x01(\x0b2+.ares.datamodel.templates.ParameterMetadatab\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'templates.planner_allocation_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_PLANNERALLOCATION']._serialized_start = 161
    _globals['_PLANNERALLOCATION']._serialized_end = 316