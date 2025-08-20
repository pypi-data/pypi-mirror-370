from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class RoleTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_TYPE_UNSPECIFIED: _ClassVar[RoleTypeProto]
    ADMIN: _ClassVar[RoleTypeProto]
    CREATE: _ClassVar[RoleTypeProto]
    EDIT: _ClassVar[RoleTypeProto]
    DELETE: _ClassVar[RoleTypeProto]
    VIEW: _ClassVar[RoleTypeProto]
ROLE_TYPE_UNSPECIFIED: RoleTypeProto
ADMIN: RoleTypeProto
CREATE: RoleTypeProto
EDIT: RoleTypeProto
DELETE: RoleTypeProto
VIEW: RoleTypeProto
