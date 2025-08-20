from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AddMemberRequest(_message.Message):
    __slots__ = ("group_id", "member_ids", "request_id")
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_IDS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    group_id: str
    member_ids: _containers.RepeatedScalarFieldContainer[str]
    request_id: str
    def __init__(self, group_id: _Optional[str] = ..., member_ids: _Optional[_Iterable[str]] = ..., request_id: _Optional[str] = ...) -> None: ...
