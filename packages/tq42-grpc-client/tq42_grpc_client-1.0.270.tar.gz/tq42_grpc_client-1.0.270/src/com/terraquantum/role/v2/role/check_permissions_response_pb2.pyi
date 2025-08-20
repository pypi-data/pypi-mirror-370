from com.terraquantum.role.v2.role import check_permission_pb2 as _check_permission_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CheckPermissionsResponsesProto(_message.Message):
    __slots__ = ("responses",)
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    responses: _containers.RepeatedCompositeFieldContainer[CheckPermissionResponseProto]
    def __init__(self, responses: _Optional[_Iterable[_Union[CheckPermissionResponseProto, _Mapping]]] = ...) -> None: ...

class CheckPermissionResponseProto(_message.Message):
    __slots__ = ("check", "has_permission")
    CHECK_FIELD_NUMBER: _ClassVar[int]
    HAS_PERMISSION_FIELD_NUMBER: _ClassVar[int]
    check: _check_permission_pb2.CheckPermissionProto
    has_permission: bool
    def __init__(self, check: _Optional[_Union[_check_permission_pb2.CheckPermissionProto, _Mapping]] = ..., has_permission: bool = ...) -> None: ...
