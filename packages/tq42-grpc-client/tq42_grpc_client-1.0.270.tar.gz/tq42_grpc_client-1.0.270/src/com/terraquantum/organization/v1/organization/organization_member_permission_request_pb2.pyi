from com.terraquantum.common.v1.role import project_role_request_pb2 as _project_role_request_pb2
from com.terraquantum.common.v1.role import role_organization_resource_request_pb2 as _role_organization_resource_request_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationMemberPermissionRequest(_message.Message):
    __slots__ = ("projects_roles", "organization_roles")
    PROJECTS_ROLES_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ROLES_FIELD_NUMBER: _ClassVar[int]
    projects_roles: _containers.RepeatedCompositeFieldContainer[_project_role_request_pb2.ProjectRoleRequest]
    organization_roles: _containers.RepeatedCompositeFieldContainer[_role_organization_resource_request_pb2.OrganizationResourceRoleRequest]
    def __init__(self, projects_roles: _Optional[_Iterable[_Union[_project_role_request_pb2.ProjectRoleRequest, _Mapping]]] = ..., organization_roles: _Optional[_Iterable[_Union[_role_organization_resource_request_pb2.OrganizationResourceRoleRequest, _Mapping]]] = ...) -> None: ...
