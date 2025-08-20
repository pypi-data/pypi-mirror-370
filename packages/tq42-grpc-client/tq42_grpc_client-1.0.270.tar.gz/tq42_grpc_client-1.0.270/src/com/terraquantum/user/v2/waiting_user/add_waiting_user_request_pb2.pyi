from com.terraquantum.javalibs.logging.v1 import logging_extensions_pb2 as _logging_extensions_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AddWaitingUserRequest(_message.Message):
    __slots__ = ("jwt", "request_id")
    JWT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    jwt: str
    request_id: str
    def __init__(self, jwt: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...
