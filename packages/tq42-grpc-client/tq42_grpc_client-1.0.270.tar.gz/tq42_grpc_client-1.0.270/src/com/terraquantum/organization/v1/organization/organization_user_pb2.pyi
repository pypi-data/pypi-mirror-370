from com.terraquantum.common.v1.organization import organization_user_status_pb2 as _organization_user_status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationUserProto(_message.Message):
    __slots__ = ("id", "organization_id", "user_id", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    user_id: str
    status: _organization_user_status_pb2.OrganizationUserStatusProto
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ..., user_id: _Optional[str] = ..., status: _Optional[_Union[_organization_user_status_pb2.OrganizationUserStatusProto, str]] = ...) -> None: ...
