from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class InitBalanceRequest(_message.Message):
    __slots__ = ("org_id", "initial_balance")
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    INITIAL_BALANCE_FIELD_NUMBER: _ClassVar[int]
    org_id: str
    initial_balance: int
    def __init__(self, org_id: _Optional[str] = ..., initial_balance: _Optional[int] = ...) -> None: ...
