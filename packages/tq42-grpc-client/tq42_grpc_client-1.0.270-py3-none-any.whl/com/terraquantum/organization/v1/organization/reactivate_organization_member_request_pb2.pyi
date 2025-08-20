from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ReactivateOrganizationMemberRequest(_message.Message):
    __slots__ = ("request_id", "organization_member_id")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    organization_member_id: str
    def __init__(self, request_id: _Optional[str] = ..., organization_member_id: _Optional[str] = ...) -> None: ...
