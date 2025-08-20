from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ListOrganizationUserPoliciesRequest(_message.Message):
    __slots__ = ("user_id", "organization_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    organization_id: str
    def __init__(self, user_id: _Optional[str] = ..., organization_id: _Optional[str] = ...) -> None: ...
