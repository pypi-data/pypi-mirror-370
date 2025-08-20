from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationMemberStatusProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORGANIZATION_MEMBER_STATUS_UNSPECIFIED: _ClassVar[OrganizationMemberStatusProto]
    MEMBER_PENDING: _ClassVar[OrganizationMemberStatusProto]
    MEMBER_ACTIVE: _ClassVar[OrganizationMemberStatusProto]
    MEMBER_INACTIVE: _ClassVar[OrganizationMemberStatusProto]
ORGANIZATION_MEMBER_STATUS_UNSPECIFIED: OrganizationMemberStatusProto
MEMBER_PENDING: OrganizationMemberStatusProto
MEMBER_ACTIVE: OrganizationMemberStatusProto
MEMBER_INACTIVE: OrganizationMemberStatusProto
