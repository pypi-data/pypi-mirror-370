from com.terraquantum.experiment.v1.experimentrun.algorithm import shared_pb2 as _shared_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CircuitRunnerBackendProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CIRCUIT_RUNNER_BACKEND_UNSPECIFIED: _ClassVar[CircuitRunnerBackendProto]
    IBM: _ClassVar[CircuitRunnerBackendProto]
    IONQ_SIMULATOR: _ClassVar[CircuitRunnerBackendProto]
    CIRQ_SIMULATOR: _ClassVar[CircuitRunnerBackendProto]
    QISKIT_SIMULATOR: _ClassVar[CircuitRunnerBackendProto]
CIRCUIT_RUNNER_BACKEND_UNSPECIFIED: CircuitRunnerBackendProto
IBM: CircuitRunnerBackendProto
IONQ_SIMULATOR: CircuitRunnerBackendProto
CIRQ_SIMULATOR: CircuitRunnerBackendProto
QISKIT_SIMULATOR: CircuitRunnerBackendProto

class CircuitRunParametersProto(_message.Message):
    __slots__ = ("shots", "backend")
    SHOTS_FIELD_NUMBER: _ClassVar[int]
    BACKEND_FIELD_NUMBER: _ClassVar[int]
    shots: int
    backend: CircuitRunnerBackendProto
    def __init__(self, shots: _Optional[int] = ..., backend: _Optional[_Union[CircuitRunnerBackendProto, str]] = ...) -> None: ...

class CircuitRunInputsProto(_message.Message):
    __slots__ = ("circuit",)
    CIRCUIT_FIELD_NUMBER: _ClassVar[int]
    circuit: _shared_pb2.ModelStorageInfoProto
    def __init__(self, circuit: _Optional[_Union[_shared_pb2.ModelStorageInfoProto, _Mapping]] = ...) -> None: ...

class CircuitRunMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: CircuitRunParametersProto
    inputs: CircuitRunInputsProto
    def __init__(self, parameters: _Optional[_Union[CircuitRunParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[CircuitRunInputsProto, _Mapping]] = ...) -> None: ...

class CircuitRunOutputsProto(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: _shared_pb2.DatasetStorageInfoProto
    def __init__(self, data: _Optional[_Union[_shared_pb2.DatasetStorageInfoProto, _Mapping]] = ...) -> None: ...

class CircuitRunOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: str
    outputs: CircuitRunOutputsProto
    def __init__(self, result: _Optional[str] = ..., outputs: _Optional[_Union[CircuitRunOutputsProto, _Mapping]] = ...) -> None: ...
