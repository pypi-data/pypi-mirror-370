from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm.ml_layers import shared_pb2 as _shared_pb2
from com.terraquantum import default_value_pb2 as _default_value_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EFQLayer(_message.Message):
    __slots__ = ("num_qubits", "depth", "measurement_mode", "rotation", "entangling", "measure")
    NUM_QUBITS_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    MEASUREMENT_MODE_FIELD_NUMBER: _ClassVar[int]
    ROTATION_FIELD_NUMBER: _ClassVar[int]
    ENTANGLING_FIELD_NUMBER: _ClassVar[int]
    MEASURE_FIELD_NUMBER: _ClassVar[int]
    num_qubits: int
    depth: int
    measurement_mode: _shared_pb2.MeasurementModeProto
    rotation: _shared_pb2.MeasureProto
    entangling: _shared_pb2.EntanglingProto
    measure: _shared_pb2.MeasureProto
    def __init__(self, num_qubits: _Optional[int] = ..., depth: _Optional[int] = ..., measurement_mode: _Optional[_Union[_shared_pb2.MeasurementModeProto, str]] = ..., rotation: _Optional[_Union[_shared_pb2.MeasureProto, str]] = ..., entangling: _Optional[_Union[_shared_pb2.EntanglingProto, str]] = ..., measure: _Optional[_Union[_shared_pb2.MeasureProto, str]] = ...) -> None: ...
