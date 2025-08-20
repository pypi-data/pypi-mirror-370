from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class OrganizationProto(_message.Message):
    __slots__ = ("id", "name", "description", "is_personal_org")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_PERSONAL_ORG_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    is_personal_org: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., is_personal_org: bool = ...) -> None: ...
