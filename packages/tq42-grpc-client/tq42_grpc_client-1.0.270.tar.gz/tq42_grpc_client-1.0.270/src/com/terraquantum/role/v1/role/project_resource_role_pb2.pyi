from com.terraquantum.common.v1.role import role_project_resource_pb2 as _role_project_resource_pb2
from com.terraquantum.common.v1.role import role_type_pb2 as _role_type_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProjectResourceRoleProto(_message.Message):
    __slots__ = ("resource", "project_role_types")
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ROLE_TYPES_FIELD_NUMBER: _ClassVar[int]
    resource: _role_project_resource_pb2.RoleProjectResourceTypeProto
    project_role_types: _containers.RepeatedScalarFieldContainer[_role_type_pb2.RoleTypeProto]
    def __init__(self, resource: _Optional[_Union[_role_project_resource_pb2.RoleProjectResourceTypeProto, str]] = ..., project_role_types: _Optional[_Iterable[_Union[_role_type_pb2.RoleTypeProto, str]]] = ...) -> None: ...
