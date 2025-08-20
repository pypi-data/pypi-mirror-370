from com.terraquantum.common.v1.role import project_role_pb2 as _project_role_pb2
from com.terraquantum.common.v1.role import role_organization_resource_pb2 as _role_organization_resource_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationMemberPermissionProto(_message.Message):
    __slots__ = ("id", "organization_member_id", "projects_roles", "organization_roles")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECTS_ROLES_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ROLES_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_member_id: str
    projects_roles: _containers.RepeatedCompositeFieldContainer[_project_role_pb2.ProjectRoleProto]
    organization_roles: _containers.RepeatedCompositeFieldContainer[_role_organization_resource_pb2.OrganizationResourceRoleProto]
    def __init__(self, id: _Optional[str] = ..., organization_member_id: _Optional[str] = ..., projects_roles: _Optional[_Iterable[_Union[_project_role_pb2.ProjectRoleProto, _Mapping]]] = ..., organization_roles: _Optional[_Iterable[_Union[_role_organization_resource_pb2.OrganizationResourceRoleProto, _Mapping]]] = ...) -> None: ...
