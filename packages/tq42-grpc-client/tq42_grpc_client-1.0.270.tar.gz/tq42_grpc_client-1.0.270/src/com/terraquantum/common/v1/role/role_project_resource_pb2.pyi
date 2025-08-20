from com.terraquantum.common.v1.role import role_type_pb2 as _role_type_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RoleProjectResourceTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_PROJECT_RESOURCE_UNSPECIFIED: _ClassVar[RoleProjectResourceTypeProto]
    PROJECT_PROJECT: _ClassVar[RoleProjectResourceTypeProto]
    PROJECT_EXPERIMENT: _ClassVar[RoleProjectResourceTypeProto]
    PROJECT_STORAGE: _ClassVar[RoleProjectResourceTypeProto]
    PROJECT_EXPERIMENT_RUN: _ClassVar[RoleProjectResourceTypeProto]
    PROJECT_EXPERIMENT_RUN_SIM: _ClassVar[RoleProjectResourceTypeProto]
    PROJECT_EXPERIMENT_RUN_QPU: _ClassVar[RoleProjectResourceTypeProto]
ROLE_PROJECT_RESOURCE_UNSPECIFIED: RoleProjectResourceTypeProto
PROJECT_PROJECT: RoleProjectResourceTypeProto
PROJECT_EXPERIMENT: RoleProjectResourceTypeProto
PROJECT_STORAGE: RoleProjectResourceTypeProto
PROJECT_EXPERIMENT_RUN: RoleProjectResourceTypeProto
PROJECT_EXPERIMENT_RUN_SIM: RoleProjectResourceTypeProto
PROJECT_EXPERIMENT_RUN_QPU: RoleProjectResourceTypeProto

class ProjectResourceRoleProto(_message.Message):
    __slots__ = ("id", "resource", "project_role_id", "project_role_types")
    ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ROLE_TYPES_FIELD_NUMBER: _ClassVar[int]
    id: str
    resource: RoleProjectResourceTypeProto
    project_role_id: str
    project_role_types: _containers.RepeatedCompositeFieldContainer[ProjectResourceRoleTypeProto]
    def __init__(self, id: _Optional[str] = ..., resource: _Optional[_Union[RoleProjectResourceTypeProto, str]] = ..., project_role_id: _Optional[str] = ..., project_role_types: _Optional[_Iterable[_Union[ProjectResourceRoleTypeProto, _Mapping]]] = ...) -> None: ...

class ProjectResourceRoleTypeProto(_message.Message):
    __slots__ = ("id", "project_resource_role_id", "role_type")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_RESOURCE_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    project_resource_role_id: str
    role_type: _role_type_pb2.RoleTypeProto
    def __init__(self, id: _Optional[str] = ..., project_resource_role_id: _Optional[str] = ..., role_type: _Optional[_Union[_role_type_pb2.RoleTypeProto, str]] = ...) -> None: ...
