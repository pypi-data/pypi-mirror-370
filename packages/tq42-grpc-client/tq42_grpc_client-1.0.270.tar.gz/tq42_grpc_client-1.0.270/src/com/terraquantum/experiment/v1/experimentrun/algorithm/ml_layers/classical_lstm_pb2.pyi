from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum import default_value_pb2 as _default_value_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ClassicalLSTMLayer(_message.Message):
    __slots__ = ("hidden_size",)
    HIDDEN_SIZE_FIELD_NUMBER: _ClassVar[int]
    hidden_size: int
    def __init__(self, hidden_size: _Optional[int] = ...) -> None: ...
