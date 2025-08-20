from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum import default_value_pb2 as _default_value_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CnotGate(_message.Message):
    __slots__ = ("wire1", "wire2")
    WIRE1_FIELD_NUMBER: _ClassVar[int]
    WIRE2_FIELD_NUMBER: _ClassVar[int]
    wire1: int
    wire2: int
    def __init__(self, wire1: _Optional[int] = ..., wire2: _Optional[int] = ...) -> None: ...
