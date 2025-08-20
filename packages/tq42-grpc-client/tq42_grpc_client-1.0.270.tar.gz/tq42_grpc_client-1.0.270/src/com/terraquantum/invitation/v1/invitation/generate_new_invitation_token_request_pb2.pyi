from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GenerateNewInvitationTokenRequest(_message.Message):
    __slots__ = ("invitation_token_code", "request_id")
    INVITATION_TOKEN_CODE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    invitation_token_code: str
    request_id: str
    def __init__(self, invitation_token_code: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...
