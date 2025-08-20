from com.terraquantum.common.v1.role import role_project_resource_pb2 as _role_project_resource_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProjectRoleProto(_message.Message):
    __slots__ = ("id", "project_id", "organization_member_permission_id", "resource_roles")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_MEMBER_PERMISSION_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ROLES_FIELD_NUMBER: _ClassVar[int]
    id: str
    project_id: str
    organization_member_permission_id: str
    resource_roles: _containers.RepeatedCompositeFieldContainer[_role_project_resource_pb2.ProjectResourceRoleProto]
    def __init__(self, id: _Optional[str] = ..., project_id: _Optional[str] = ..., organization_member_permission_id: _Optional[str] = ..., resource_roles: _Optional[_Iterable[_Union[_role_project_resource_pb2.ProjectResourceRoleProto, _Mapping]]] = ...) -> None: ...
