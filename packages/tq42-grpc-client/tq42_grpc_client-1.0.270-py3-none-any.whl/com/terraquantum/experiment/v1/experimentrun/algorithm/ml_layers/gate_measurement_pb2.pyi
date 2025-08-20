from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum import default_value_pb2 as _default_value_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import shared_pb2 as _shared_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MeasurementGate(_message.Message):
    __slots__ = ("wire", "pauli")
    WIRE_FIELD_NUMBER: _ClassVar[int]
    PAULI_FIELD_NUMBER: _ClassVar[int]
    wire: int
    pauli: _shared_pb2.MeasureProto
    def __init__(self, wire: _Optional[int] = ..., pauli: _Optional[_Union[_shared_pb2.MeasureProto, str]] = ...) -> None: ...
