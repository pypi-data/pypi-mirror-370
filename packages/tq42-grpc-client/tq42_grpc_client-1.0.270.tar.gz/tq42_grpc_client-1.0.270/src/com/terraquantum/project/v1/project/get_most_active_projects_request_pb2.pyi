from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MostActiveProjectsRequest(_message.Message):
    __slots__ = ("most_active_count", "organization_id")
    MOST_ACTIVE_COUNT_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    most_active_count: int
    organization_id: str
    def __init__(self, most_active_count: _Optional[int] = ..., organization_id: _Optional[str] = ...) -> None: ...
