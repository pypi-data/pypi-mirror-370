from com.terraquantum.role.v2.role import check_permission_pb2 as _check_permission_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CheckPermissionsRequestProto(_message.Message):
    __slots__ = ("checks",)
    CHECKS_FIELD_NUMBER: _ClassVar[int]
    checks: _containers.RepeatedCompositeFieldContainer[_check_permission_pb2.CheckPermissionProto]
    def __init__(self, checks: _Optional[_Iterable[_Union[_check_permission_pb2.CheckPermissionProto, _Mapping]]] = ...) -> None: ...
