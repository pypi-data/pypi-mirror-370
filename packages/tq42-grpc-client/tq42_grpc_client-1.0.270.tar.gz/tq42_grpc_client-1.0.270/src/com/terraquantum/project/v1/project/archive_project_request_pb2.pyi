from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ArchiveProjectRequest(_message.Message):
    __slots__ = ("id", "request_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    request_id: str
    def __init__(self, id: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...
