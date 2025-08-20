from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ResendOrganizationMemberInvitationRequest(_message.Message):
    __slots__ = ("organization_member_id", "request_id")
    ORGANIZATION_MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    organization_member_id: str
    request_id: str
    def __init__(self, organization_member_id: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...
