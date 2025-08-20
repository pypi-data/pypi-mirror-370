from com.terraquantum.common.v1.role import project_role_request_pb2 as _project_role_request_pb2
from com.terraquantum.common.v1.role import role_organization_resource_request_pb2 as _role_organization_resource_request_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateGroupRequest(_message.Message):
    __slots__ = ("organization_id", "name", "description", "organization_member_ids", "project_roles", "organization_roles", "request_id")
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_MEMBER_IDS_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ROLES_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ROLES_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    organization_id: str
    name: str
    description: str
    organization_member_ids: _containers.RepeatedScalarFieldContainer[str]
    project_roles: _containers.RepeatedCompositeFieldContainer[_project_role_request_pb2.ProjectRoleRequest]
    organization_roles: _containers.RepeatedCompositeFieldContainer[_role_organization_resource_request_pb2.OrganizationResourceRoleRequest]
    request_id: str
    def __init__(self, organization_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., organization_member_ids: _Optional[_Iterable[str]] = ..., project_roles: _Optional[_Iterable[_Union[_project_role_request_pb2.ProjectRoleRequest, _Mapping]]] = ..., organization_roles: _Optional[_Iterable[_Union[_role_organization_resource_request_pb2.OrganizationResourceRoleRequest, _Mapping]]] = ..., request_id: _Optional[str] = ...) -> None: ...
