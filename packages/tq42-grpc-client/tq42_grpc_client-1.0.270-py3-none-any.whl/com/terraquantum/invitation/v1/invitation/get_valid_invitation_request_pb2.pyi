from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetValidInvitationRequest(_message.Message):
    __slots__ = ("invitation_token",)
    INVITATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    invitation_token: str
    def __init__(self, invitation_token: _Optional[str] = ...) -> None: ...
