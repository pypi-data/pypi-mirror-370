import datetime

from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from templates import campaign_template_pb2 as _campaign_template_pb2
import project_pb2 as _project_pb2
import execution_status_messages_pb2 as _execution_status_messages_pb2
import execution_summary_messages_pb2 as _execution_summary_messages_pb2
import ares_campaign_tag_pb2 as _ares_campaign_tag_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TagRequest(_message.Message):
    __slots__ = ("tag",)
    TAG_FIELD_NUMBER: _ClassVar[int]
    tag: _ares_campaign_tag_pb2.AresCampaignTag
    def __init__(self, tag: _Optional[_Union[_ares_campaign_tag_pb2.AresCampaignTag, _Mapping]] = ...) -> None: ...

class TagsResponse(_message.Message):
    __slots__ = ("available_tags",)
    AVAILABLE_TAGS_FIELD_NUMBER: _ClassVar[int]
    available_tags: _containers.RepeatedCompositeFieldContainer[_ares_campaign_tag_pb2.AresCampaignTag]
    def __init__(self, available_tags: _Optional[_Iterable[_Union[_ares_campaign_tag_pb2.AresCampaignTag, _Mapping]]] = ...) -> None: ...

class AddOrUpdateCampaignRequest(_message.Message):
    __slots__ = ("template",)
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    template: _campaign_template_pb2.CampaignTemplate
    def __init__(self, template: _Optional[_Union[_campaign_template_pb2.CampaignTemplate, _Mapping]] = ...) -> None: ...

class RequestById(_message.Message):
    __slots__ = ("unique_id",)
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    def __init__(self, unique_id: _Optional[str] = ...) -> None: ...

class CampaignRequest(_message.Message):
    __slots__ = ("campaign_name", "unique_id")
    CAMPAIGN_NAME_FIELD_NUMBER: _ClassVar[int]
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    campaign_name: str
    unique_id: str
    def __init__(self, campaign_name: _Optional[str] = ..., unique_id: _Optional[str] = ...) -> None: ...

class GetAllCampaignsRequest(_message.Message):
    __slots__ = ("file_path",)
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    file_path: str
    def __init__(self, file_path: _Optional[str] = ...) -> None: ...

class CampaignsResponse(_message.Message):
    __slots__ = ("campaign_templates",)
    CAMPAIGN_TEMPLATES_FIELD_NUMBER: _ClassVar[int]
    campaign_templates: _containers.RepeatedCompositeFieldContainer[_campaign_template_pb2.CampaignTemplate]
    def __init__(self, campaign_templates: _Optional[_Iterable[_Union[_campaign_template_pb2.CampaignTemplate, _Mapping]]] = ...) -> None: ...

class CampaignResponse(_message.Message):
    __slots__ = ("has_value", "value")
    HAS_VALUE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    has_value: bool
    value: _campaign_template_pb2.CampaignTemplate
    def __init__(self, has_value: bool = ..., value: _Optional[_Union[_campaign_template_pb2.CampaignTemplate, _Mapping]] = ...) -> None: ...

class StartCampaignRequest(_message.Message):
    __slots__ = ("user_notes", "campaign_tags")
    USER_NOTES_FIELD_NUMBER: _ClassVar[int]
    CAMPAIGN_TAGS_FIELD_NUMBER: _ClassVar[int]
    user_notes: str
    campaign_tags: _containers.RepeatedCompositeFieldContainer[_ares_campaign_tag_pb2.AresCampaignTag]
    def __init__(self, user_notes: _Optional[str] = ..., campaign_tags: _Optional[_Iterable[_Union[_ares_campaign_tag_pb2.AresCampaignTag, _Mapping]]] = ...) -> None: ...

class ProjectRequest(_message.Message):
    __slots__ = ("project_name",)
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    project_name: str
    def __init__(self, project_name: _Optional[str] = ...) -> None: ...

class ProjectsResponse(_message.Message):
    __slots__ = ("projects",)
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[_project_pb2.Project]
    def __init__(self, projects: _Optional[_Iterable[_Union[_project_pb2.Project, _Mapping]]] = ...) -> None: ...

class CampaignExecutionStatusResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _execution_status_messages_pb2.CampaignExecutionStatus
    def __init__(self, status: _Optional[_Union[_execution_status_messages_pb2.CampaignExecutionStatus, _Mapping]] = ...) -> None: ...

class StartStopConditionsResponse(_message.Message):
    __slots__ = ("start_stop_conditions",)
    START_STOP_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    start_stop_conditions: _containers.RepeatedCompositeFieldContainer[StartStopCondition]
    def __init__(self, start_stop_conditions: _Optional[_Iterable[_Union[StartStopCondition, _Mapping]]] = ...) -> None: ...

class GetReplanRateResponse(_message.Message):
    __slots__ = ("ReplanRate",)
    REPLANRATE_FIELD_NUMBER: _ClassVar[int]
    ReplanRate: int
    def __init__(self, ReplanRate: _Optional[int] = ...) -> None: ...

class StartStopCondition(_message.Message):
    __slots__ = ("name", "message")
    NAME_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    name: str
    message: str
    def __init__(self, name: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class ReplanRate(_message.Message):
    __slots__ = ("ReplanRate",)
    REPLANRATE_FIELD_NUMBER: _ClassVar[int]
    ReplanRate: int
    def __init__(self, ReplanRate: _Optional[int] = ...) -> None: ...

class NumExperimentsCondition(_message.Message):
    __slots__ = ("num_experiments",)
    NUM_EXPERIMENTS_FIELD_NUMBER: _ClassVar[int]
    num_experiments: int
    def __init__(self, num_experiments: _Optional[int] = ...) -> None: ...

class ExperimentStopConditionResponse(_message.Message):
    __slots__ = ("active_condition", "description")
    ACTIVE_CONDITION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    active_condition: str
    description: str
    def __init__(self, active_condition: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class AnalysisResultCondition(_message.Message):
    __slots__ = ("desired_result", "leeway")
    DESIRED_RESULT_FIELD_NUMBER: _ClassVar[int]
    LEEWAY_FIELD_NUMBER: _ClassVar[int]
    desired_result: float
    leeway: float
    def __init__(self, desired_result: _Optional[float] = ..., leeway: _Optional[float] = ...) -> None: ...

class AvailableCampaignExecutionSummariesResponse(_message.Message):
    __slots__ = ("available_campaign_summaries",)
    AVAILABLE_CAMPAIGN_SUMMARIES_FIELD_NUMBER: _ClassVar[int]
    available_campaign_summaries: _containers.RepeatedCompositeFieldContainer[CampaignExecutionSummaryMetadata]
    def __init__(self, available_campaign_summaries: _Optional[_Iterable[_Union[CampaignExecutionSummaryMetadata, _Mapping]]] = ...) -> None: ...

class CampaignExecutionSummaryMetadata(_message.Message):
    __slots__ = ("campaign_name", "completion_time", "summary_id", "num_experiments")
    CAMPAIGN_NAME_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_TIME_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_ID_FIELD_NUMBER: _ClassVar[int]
    NUM_EXPERIMENTS_FIELD_NUMBER: _ClassVar[int]
    campaign_name: str
    completion_time: _timestamp_pb2.Timestamp
    summary_id: str
    num_experiments: int
    def __init__(self, campaign_name: _Optional[str] = ..., completion_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., summary_id: _Optional[str] = ..., num_experiments: _Optional[int] = ...) -> None: ...

class CampaignExecutionSummaryRequest(_message.Message):
    __slots__ = ("summary_id",)
    SUMMARY_ID_FIELD_NUMBER: _ClassVar[int]
    summary_id: str
    def __init__(self, summary_id: _Optional[str] = ...) -> None: ...

class CheckExecutionEligibilityResponse(_message.Message):
    __slots__ = ("is_eligible", "error")
    IS_ELIGIBLE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    is_eligible: bool
    error: str
    def __init__(self, is_eligible: bool = ..., error: _Optional[str] = ...) -> None: ...
