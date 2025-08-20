from com.terraquantum.experiment.v1.experimentrun.algorithm import shared_pb2 as _shared_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TetraQuEncParametersProto(_message.Message):
    __slots__ = ("qubo", "number_layers", "steps", "velocity", "optimizer")
    QUBO_FIELD_NUMBER: _ClassVar[int]
    NUMBER_LAYERS_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    VELOCITY_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZER_FIELD_NUMBER: _ClassVar[int]
    qubo: _containers.RepeatedScalarFieldContainer[float]
    number_layers: int
    steps: int
    velocity: float
    optimizer: str
    def __init__(self, qubo: _Optional[_Iterable[float]] = ..., number_layers: _Optional[int] = ..., steps: _Optional[int] = ..., velocity: _Optional[float] = ..., optimizer: _Optional[str] = ...) -> None: ...

class TetraQuEncInputsProto(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TetraQuEncMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: TetraQuEncParametersProto
    inputs: TetraQuEncInputsProto
    def __init__(self, parameters: _Optional[_Union[TetraQuEncParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[TetraQuEncInputsProto, _Mapping]] = ...) -> None: ...

class TetraQuEncOutputsProto(_message.Message):
    __slots__ = ("circuit",)
    CIRCUIT_FIELD_NUMBER: _ClassVar[int]
    circuit: _shared_pb2.ModelStorageInfoProto
    def __init__(self, circuit: _Optional[_Union[_shared_pb2.ModelStorageInfoProto, _Mapping]] = ...) -> None: ...

class TetraQuEncOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: str
    outputs: TetraQuEncOutputsProto
    def __init__(self, result: _Optional[str] = ..., outputs: _Optional[_Union[TetraQuEncOutputsProto, _Mapping]] = ...) -> None: ...
