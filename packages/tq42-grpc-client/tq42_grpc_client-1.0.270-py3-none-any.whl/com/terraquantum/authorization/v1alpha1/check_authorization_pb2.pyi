from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PrincipalType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRINCIPAL_TYPE_UNSPECIFIED: _ClassVar[PrincipalType]
    PRINCIPAL_TYPE_USER: _ClassVar[PrincipalType]

class ResourceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESOURCE_TYPE_UNSPECIFIED: _ClassVar[ResourceType]
    RESOURCE_TYPE_ORGANIZATION: _ClassVar[ResourceType]
    RESOURCE_TYPE_PROJECT: _ClassVar[ResourceType]
PRINCIPAL_TYPE_UNSPECIFIED: PrincipalType
PRINCIPAL_TYPE_USER: PrincipalType
RESOURCE_TYPE_UNSPECIFIED: ResourceType
RESOURCE_TYPE_ORGANIZATION: ResourceType
RESOURCE_TYPE_PROJECT: ResourceType

class CheckAuthorizationRequest(_message.Message):
    __slots__ = ("principal_type", "principal_id", "permission", "resource_type", "resource_id")
    PRINCIPAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    principal_type: PrincipalType
    principal_id: str
    permission: str
    resource_type: ResourceType
    resource_id: str
    def __init__(self, principal_type: _Optional[_Union[PrincipalType, str]] = ..., principal_id: _Optional[str] = ..., permission: _Optional[str] = ..., resource_type: _Optional[_Union[ResourceType, str]] = ..., resource_id: _Optional[str] = ...) -> None: ...

class CheckAuthorizationResponse(_message.Message):
    __slots__ = ("authorized",)
    AUTHORIZED_FIELD_NUMBER: _ClassVar[int]
    authorized: bool
    def __init__(self, authorized: bool = ...) -> None: ...
