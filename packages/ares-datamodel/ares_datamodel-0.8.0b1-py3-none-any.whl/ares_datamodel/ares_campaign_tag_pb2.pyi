from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AresCampaignTag(_message.Message):
    __slots__ = ("unique_id", "tag_name")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    TAG_NAME_FIELD_NUMBER: _ClassVar[int]
    unique_id: str
    tag_name: str
    def __init__(self, unique_id: _Optional[str] = ..., tag_name: _Optional[str] = ...) -> None: ...
