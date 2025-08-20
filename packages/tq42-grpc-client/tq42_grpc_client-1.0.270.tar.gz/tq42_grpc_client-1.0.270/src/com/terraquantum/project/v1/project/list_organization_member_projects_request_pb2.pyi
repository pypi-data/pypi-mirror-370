from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ListOrganizationMemberProjectsRequest(_message.Message):
    __slots__ = ("organization_id", "organization_member_id")
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    organization_member_id: str
    def __init__(self, organization_id: _Optional[str] = ..., organization_member_id: _Optional[str] = ...) -> None: ...
