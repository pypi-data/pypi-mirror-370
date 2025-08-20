from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RoleIdProto(_message.Message):
    __slots__ = ("object_type", "relation")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    relation: str
    def __init__(self, object_type: _Optional[str] = ..., relation: _Optional[str] = ...) -> None: ...
