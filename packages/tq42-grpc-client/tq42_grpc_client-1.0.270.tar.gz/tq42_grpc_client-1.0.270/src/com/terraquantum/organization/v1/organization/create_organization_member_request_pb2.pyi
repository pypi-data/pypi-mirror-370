from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from com.terraquantum.organization.v1.organization import organization_member_permission_request_pb2 as _organization_member_permission_request_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateOrganizationMemberRequest(_message.Message):
    __slots__ = ("request_id", "organization_id", "email", "first_name", "last_name", "permission")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    organization_id: str
    email: str
    first_name: str
    last_name: str
    permission: _organization_member_permission_request_pb2.OrganizationMemberPermissionRequest
    def __init__(self, request_id: _Optional[str] = ..., organization_id: _Optional[str] = ..., email: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., permission: _Optional[_Union[_organization_member_permission_request_pb2.OrganizationMemberPermissionRequest, _Mapping]] = ...) -> None: ...
