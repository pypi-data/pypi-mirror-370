from com.terraquantum.common.v1.role import role_type_pb2 as _role_type_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RoleOrganizationResourceTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_ORGANIZATION_RESOURCE_UNSPECIFIED: _ClassVar[RoleOrganizationResourceTypeProto]
    ORGANIZATION_USER: _ClassVar[RoleOrganizationResourceTypeProto]
    ORGANIZATION_BILLING: _ClassVar[RoleOrganizationResourceTypeProto]
    ORGANIZATION_PROJECT: _ClassVar[RoleOrganizationResourceTypeProto]
    ORGANIZATION_EXPERIMENT: _ClassVar[RoleOrganizationResourceTypeProto]
    ORGANIZATION_STORAGE: _ClassVar[RoleOrganizationResourceTypeProto]
    ORGANIZATION_EXPERIMENT_RUN: _ClassVar[RoleOrganizationResourceTypeProto]
    ORGANIZATION_EXPERIMENT_RUN_SIM: _ClassVar[RoleOrganizationResourceTypeProto]
    ORGANIZATION_EXPERIMENT_RUN_QPU: _ClassVar[RoleOrganizationResourceTypeProto]
    ORGANIZATION_PLAN: _ClassVar[RoleOrganizationResourceTypeProto]
ROLE_ORGANIZATION_RESOURCE_UNSPECIFIED: RoleOrganizationResourceTypeProto
ORGANIZATION_USER: RoleOrganizationResourceTypeProto
ORGANIZATION_BILLING: RoleOrganizationResourceTypeProto
ORGANIZATION_PROJECT: RoleOrganizationResourceTypeProto
ORGANIZATION_EXPERIMENT: RoleOrganizationResourceTypeProto
ORGANIZATION_STORAGE: RoleOrganizationResourceTypeProto
ORGANIZATION_EXPERIMENT_RUN: RoleOrganizationResourceTypeProto
ORGANIZATION_EXPERIMENT_RUN_SIM: RoleOrganizationResourceTypeProto
ORGANIZATION_EXPERIMENT_RUN_QPU: RoleOrganizationResourceTypeProto
ORGANIZATION_PLAN: RoleOrganizationResourceTypeProto

class OrganizationResourceRoleProto(_message.Message):
    __slots__ = ("id", "resource", "organization_member_permission_id", "organization_role_types")
    ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_MEMBER_PERMISSION_ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ROLE_TYPES_FIELD_NUMBER: _ClassVar[int]
    id: str
    resource: RoleOrganizationResourceTypeProto
    organization_member_permission_id: str
    organization_role_types: _containers.RepeatedCompositeFieldContainer[OrganizationResourceRoleTypeProto]
    def __init__(self, id: _Optional[str] = ..., resource: _Optional[_Union[RoleOrganizationResourceTypeProto, str]] = ..., organization_member_permission_id: _Optional[str] = ..., organization_role_types: _Optional[_Iterable[_Union[OrganizationResourceRoleTypeProto, _Mapping]]] = ...) -> None: ...

class OrganizationResourceRoleTypeProto(_message.Message):
    __slots__ = ("id", "organization_resource_role_id", "role_type")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_RESOURCE_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    organization_resource_role_id: str
    role_type: _role_type_pb2.RoleTypeProto
    def __init__(self, id: _Optional[str] = ..., organization_resource_role_id: _Optional[str] = ..., role_type: _Optional[_Union[_role_type_pb2.RoleTypeProto, str]] = ...) -> None: ...
