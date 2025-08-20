from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CreateOrganizationRequest(_message.Message):
    __slots__ = ("name", "description", "is_personal")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_PERSONAL_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    is_personal: bool
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., is_personal: bool = ...) -> None: ...
