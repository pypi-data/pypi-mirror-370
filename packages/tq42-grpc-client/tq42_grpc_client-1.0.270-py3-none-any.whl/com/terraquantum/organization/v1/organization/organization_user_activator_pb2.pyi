from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationUserActivatorProto(_message.Message):
    __slots__ = ("id", "organization_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ...) -> None: ...
