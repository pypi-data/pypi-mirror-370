from com.terraquantum.role.v1.role import organization_resource_role_pb2 as _organization_resource_role_pb2
from com.terraquantum.role.v1.role import project_role_pb2 as _project_role_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberPermissionProto(_message.Message):
    __slots__ = ("project_roles", "organization_roles")
    PROJECT_ROLES_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ROLES_FIELD_NUMBER: _ClassVar[int]
    project_roles: _containers.RepeatedCompositeFieldContainer[_project_role_pb2.ProjectRoleProto]
    organization_roles: _containers.RepeatedCompositeFieldContainer[_organization_resource_role_pb2.OrganizationResourceRoleProto]
    def __init__(self, project_roles: _Optional[_Iterable[_Union[_project_role_pb2.ProjectRoleProto, _Mapping]]] = ..., organization_roles: _Optional[_Iterable[_Union[_organization_resource_role_pb2.OrganizationResourceRoleProto, _Mapping]]] = ...) -> None: ...
