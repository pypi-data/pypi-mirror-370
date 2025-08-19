"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'plan_transaction.proto')
_sym_db = _symbol_database.Default()
from . import planner_adapter_info_pb2 as planner__adapter__info__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from .planning import ares_planner_pb2 as planning_dot_ares__planner__pb2
from .templates import parameter_metadata_pb2 as templates_dot_parameter__metadata__pb2
from . import ares_struct_pb2 as ares__struct__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16plan_transaction.proto\x12\x0eares.datamodel\x1a\x1aplanner_adapter_info.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x1bplanning/ares_planner.proto\x1a"templates/parameter_metadata.proto\x1a\x11ares_struct.proto"\xf5\x01\n\x12PlannerTransaction\x12\x11\n\tunique_id\x18\x01 \x01(\t\x125\n\x07request\x18\x02 \x01(\x0b2$.ares.datamodel.planning.PlanRequest\x12,\n\x08response\x18\x03 \x03(\x0b2\x1a.ares.datamodel.PlanResult\x128\n\x0cplanner_info\x18\x04 \x01(\x0b2".ares.datamodel.PlannerAdapterInfo\x12\x0f\n\x07success\x18\x05 \x01(\x08\x12\x12\n\x05error\x18\x06 \x01(\tH\x00\x88\x01\x01B\x08\n\x06_error"\x92\x01\n\nPlanResult\x12\x11\n\tunique_id\x18\x01 \x01(\t\x12(\n\x05value\x18\x02 \x01(\x0b2\x19.ares.datamodel.AresValue\x12G\n\x12parameter_metadata\x18\x03 \x01(\x0b2+.ares.datamodel.templates.ParameterMetadatab\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'plan_transaction_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_PLANNERTRANSACTION']._serialized_start = 187
    _globals['_PLANNERTRANSACTION']._serialized_end = 432
    _globals['_PLANRESULT']._serialized_start = 435
    _globals['_PLANRESULT']._serialized_end = 581