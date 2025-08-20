from com.terraquantum.role.v1.role import role_id_pb2 as _role_id_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PolicyIdProto(_message.Message):
    __slots__ = ("role_id", "member_id", "member_type", "object_id")
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    role_id: _role_id_pb2.RoleIdProto
    member_id: str
    member_type: str
    object_id: str
    def __init__(self, role_id: _Optional[_Union[_role_id_pb2.RoleIdProto, _Mapping]] = ..., member_id: _Optional[str] = ..., member_type: _Optional[str] = ..., object_id: _Optional[str] = ...) -> None: ...
