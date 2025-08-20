from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum import default_value_pb2 as _default_value_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ClassicalDenseLayer(_message.Message):
    __slots__ = ("hidden_size", "bias")
    HIDDEN_SIZE_FIELD_NUMBER: _ClassVar[int]
    BIAS_FIELD_NUMBER: _ClassVar[int]
    hidden_size: int
    bias: bool
    def __init__(self, hidden_size: _Optional[int] = ..., bias: bool = ...) -> None: ...
