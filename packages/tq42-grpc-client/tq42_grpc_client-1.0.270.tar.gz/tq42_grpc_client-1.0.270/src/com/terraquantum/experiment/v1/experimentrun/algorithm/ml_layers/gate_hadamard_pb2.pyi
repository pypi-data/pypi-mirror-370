from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum import default_value_pb2 as _default_value_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class HadamardGate(_message.Message):
    __slots__ = ("wire",)
    WIRE_FIELD_NUMBER: _ClassVar[int]
    wire: int
    def __init__(self, wire: _Optional[int] = ...) -> None: ...
