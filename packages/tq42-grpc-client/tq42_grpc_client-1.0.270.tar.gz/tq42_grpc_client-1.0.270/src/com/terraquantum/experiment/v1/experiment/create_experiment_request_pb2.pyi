from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CreateExperimentRequest(_message.Message):
    __slots__ = ("project_id", "name", "description", "request_id")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    name: str
    description: str
    request_id: str
    def __init__(self, project_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...
