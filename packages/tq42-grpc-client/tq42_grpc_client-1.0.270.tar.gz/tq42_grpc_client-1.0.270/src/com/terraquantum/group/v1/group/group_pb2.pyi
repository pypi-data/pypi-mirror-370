from google.protobuf import timestamp_pb2 as _timestamp_pb2
from com.terraquantum.common.v1.role import role_organization_resource_pb2 as _role_organization_resource_pb2
from com.terraquantum.common.v1.role import project_role_pb2 as _project_role_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GroupProto(_message.Message):
    __slots__ = ("id", "organization_id", "name", "description", "created_at", "organization_member_ids", "project_roles", "organization_roles", "created_by")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_MEMBER_IDS_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ROLES_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ROLES_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_id: str
    name: str
    description: str
    created_at: _timestamp_pb2.Timestamp
    organization_member_ids: _containers.RepeatedScalarFieldContainer[str]
    project_roles: _containers.RepeatedCompositeFieldContainer[_project_role_pb2.ProjectRoleProto]
    organization_roles: _containers.RepeatedCompositeFieldContainer[_role_organization_resource_pb2.OrganizationResourceRoleProto]
    created_by: str
    def __init__(self, id: _Optional[str] = ..., organization_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., organization_member_ids: _Optional[_Iterable[str]] = ..., project_roles: _Optional[_Iterable[_Union[_project_role_pb2.ProjectRoleProto, _Mapping]]] = ..., organization_roles: _Optional[_Iterable[_Union[_role_organization_resource_pb2.OrganizationResourceRoleProto, _Mapping]]] = ..., created_by: _Optional[str] = ...) -> None: ...
