from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum.authorization.v1alpha1 import check_authorization_pb2 as _check_authorization_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetAuthorizationRequest(_message.Message):
    __slots__ = ("principal_type", "principal_id", "resource_type", "resource_id", "roles")
    PRINCIPAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    principal_type: _check_authorization_pb2.PrincipalType
    principal_id: str
    resource_type: _check_authorization_pb2.ResourceType
    resource_id: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, principal_type: _Optional[_Union[_check_authorization_pb2.PrincipalType, str]] = ..., principal_id: _Optional[str] = ..., resource_type: _Optional[_Union[_check_authorization_pb2.ResourceType, str]] = ..., resource_id: _Optional[str] = ..., roles: _Optional[_Iterable[str]] = ...) -> None: ...
