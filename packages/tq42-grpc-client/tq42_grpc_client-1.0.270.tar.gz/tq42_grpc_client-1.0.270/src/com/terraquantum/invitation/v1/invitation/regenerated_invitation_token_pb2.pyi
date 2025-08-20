from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RegeneratedInvitationTokenProto(_message.Message):
    __slots__ = ("id", "invitation_id", "token", "valid", "organization_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    INVITATION_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    VALID_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    invitation_id: str
    token: str
    valid: bool
    organization_id: str
    def __init__(self, id: _Optional[str] = ..., invitation_id: _Optional[str] = ..., token: _Optional[str] = ..., valid: bool = ..., organization_id: _Optional[str] = ...) -> None: ...
