from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ListExperimentActivitiesRequest(_message.Message):
    __slots__ = ("project_id", "last_count")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_COUNT_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    last_count: int
    def __init__(self, project_id: _Optional[str] = ..., last_count: _Optional[int] = ...) -> None: ...
