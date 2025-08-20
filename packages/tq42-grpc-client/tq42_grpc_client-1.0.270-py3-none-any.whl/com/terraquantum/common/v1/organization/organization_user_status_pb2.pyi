from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationUserStatusProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORGANIZATION_USER_STATUS_UNSPECIFIED: _ClassVar[OrganizationUserStatusProto]
    ACTIVE: _ClassVar[OrganizationUserStatusProto]
    INACTIVATING: _ClassVar[OrganizationUserStatusProto]
    REACTIVATING: _ClassVar[OrganizationUserStatusProto]
    INACTIVE: _ClassVar[OrganizationUserStatusProto]
ORGANIZATION_USER_STATUS_UNSPECIFIED: OrganizationUserStatusProto
ACTIVE: OrganizationUserStatusProto
INACTIVATING: OrganizationUserStatusProto
REACTIVATING: OrganizationUserStatusProto
INACTIVE: OrganizationUserStatusProto
