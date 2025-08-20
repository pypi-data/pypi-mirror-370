from com.terraquantum.role.v1.role import project_resource_role_pb2 as _project_resource_role_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProjectRoleProto(_message.Message):
    __slots__ = ("project_id", "resource_roles")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ROLES_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    resource_roles: _containers.RepeatedCompositeFieldContainer[_project_resource_role_pb2.ProjectResourceRoleProto]
    def __init__(self, project_id: _Optional[str] = ..., resource_roles: _Optional[_Iterable[_Union[_project_resource_role_pb2.ProjectResourceRoleProto, _Mapping]]] = ...) -> None: ...
