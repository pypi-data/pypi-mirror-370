from com.terraquantum.common.v1.organization import organization_member_status_pb2 as _organization_member_status_pb2
from com.terraquantum.role.v1.role import member_permission_pb2 as _member_permission_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationMemberRoleProto(_message.Message):
    __slots__ = ("id", "organization_id", "user_id", "project_ids", "organization_member_id", "has_organization_level_project_access", "permission", "status", "organization_owner")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    HAS_ORGANIZATION_LEVEL_PROJECT_ACCESS_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_OWNER_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    user_id: str
    project_ids: _containers.RepeatedScalarFieldContainer[str]
    organization_member_id: str
    has_organization_level_project_access: str
    permission: _member_permission_pb2.MemberPermissionProto
    status: _organization_member_status_pb2.OrganizationMemberStatusProto
    organization_owner: bool
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ..., user_id: _Optional[str] = ..., project_ids: _Optional[_Iterable[str]] = ..., organization_member_id: _Optional[str] = ..., has_organization_level_project_access: _Optional[str] = ..., permission: _Optional[_Union[_member_permission_pb2.MemberPermissionProto, _Mapping]] = ..., status: _Optional[_Union[_organization_member_status_pb2.OrganizationMemberStatusProto, str]] = ..., organization_owner: bool = ...) -> None: ...
