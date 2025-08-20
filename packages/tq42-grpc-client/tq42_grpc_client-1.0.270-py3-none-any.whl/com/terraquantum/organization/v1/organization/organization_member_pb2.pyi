from google.protobuf import timestamp_pb2 as _timestamp_pb2
from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from com.terraquantum.organization.v1.organization import organization_member_permission_pb2 as _organization_member_permission_pb2
from com.terraquantum.common.v1.organization import organization_member_status_pb2 as _organization_member_status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationMemberProto(_message.Message):
    __slots__ = ("id", "organization_id", "user_id", "status", "permission", "organization_owner", "email", "first_name", "last_name", "created_at", "activated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_OWNER_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ACTIVATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    user_id: str
    status: _organization_member_status_pb2.OrganizationMemberStatusProto
    permission: _organization_member_permission_pb2.OrganizationMemberPermissionProto
    organization_owner: bool
    email: str
    first_name: str
    last_name: str
    created_at: _timestamp_pb2.Timestamp
    activated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ..., user_id: _Optional[str] = ..., status: _Optional[_Union[_organization_member_status_pb2.OrganizationMemberStatusProto, str]] = ..., permission: _Optional[_Union[_organization_member_permission_pb2.OrganizationMemberPermissionProto, _Mapping]] = ..., organization_owner: bool = ..., email: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., activated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ListOrganizationMembersResponse(_message.Message):
    __slots__ = ("organization_members",)
    ORGANIZATION_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    organization_members: _containers.RepeatedCompositeFieldContainer[OrganizationMemberProto]
    def __init__(self, organization_members: _Optional[_Iterable[_Union[OrganizationMemberProto, _Mapping]]] = ...) -> None: ...
