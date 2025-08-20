from com.terraquantum.role.v1.policy import policy_id_pb2 as _policy_id_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PolicyProto(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: _policy_id_pb2.PolicyIdProto
    def __init__(self, id: _Optional[_Union[_policy_id_pb2.PolicyIdProto, _Mapping]] = ...) -> None: ...
