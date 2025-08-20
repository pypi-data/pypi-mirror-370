from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum.authorization.v1alpha1 import check_authorization_pb2 as _check_authorization_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAuthorizationRequest(_message.Message):
    __slots__ = ("resource_type", "resource_id")
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    resource_type: _check_authorization_pb2.ResourceType
    resource_id: str
    def __init__(self, resource_type: _Optional[_Union[_check_authorization_pb2.ResourceType, str]] = ..., resource_id: _Optional[str] = ...) -> None: ...

class GetAuthorizationResponse(_message.Message):
    __slots__ = ("principal_authorizations",)
    class PrincipalAuthorization(_message.Message):
        __slots__ = ("principal_id", "principal_type", "roles")
        PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
        PRINCIPAL_TYPE_FIELD_NUMBER: _ClassVar[int]
        ROLES_FIELD_NUMBER: _ClassVar[int]
        principal_id: str
        principal_type: _check_authorization_pb2.PrincipalType
        roles: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, principal_id: _Optional[str] = ..., principal_type: _Optional[_Union[_check_authorization_pb2.PrincipalType, str]] = ..., roles: _Optional[_Iterable[str]] = ...) -> None: ...
    PRINCIPAL_AUTHORIZATIONS_FIELD_NUMBER: _ClassVar[int]
    principal_authorizations: _containers.RepeatedCompositeFieldContainer[GetAuthorizationResponse.PrincipalAuthorization]
    def __init__(self, principal_authorizations: _Optional[_Iterable[_Union[GetAuthorizationResponse.PrincipalAuthorization, _Mapping]]] = ...) -> None: ...
