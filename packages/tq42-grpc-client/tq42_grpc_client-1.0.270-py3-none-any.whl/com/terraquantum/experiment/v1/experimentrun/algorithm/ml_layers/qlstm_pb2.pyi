from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum import default_value_pb2 as _default_value_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class QLSTMLayer(_message.Message):
    __slots__ = ("hidden_size", "num_qubits", "num_qlayers", "depth", "bidirectional", "inversward")
    HIDDEN_SIZE_FIELD_NUMBER: _ClassVar[int]
    NUM_QUBITS_FIELD_NUMBER: _ClassVar[int]
    NUM_QLAYERS_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    BIDIRECTIONAL_FIELD_NUMBER: _ClassVar[int]
    INVERSWARD_FIELD_NUMBER: _ClassVar[int]
    hidden_size: int
    num_qubits: int
    num_qlayers: int
    depth: int
    bidirectional: bool
    inversward: bool
    def __init__(self, hidden_size: _Optional[int] = ..., num_qubits: _Optional[int] = ..., num_qlayers: _Optional[int] = ..., depth: _Optional[int] = ..., bidirectional: bool = ..., inversward: bool = ...) -> None: ...
