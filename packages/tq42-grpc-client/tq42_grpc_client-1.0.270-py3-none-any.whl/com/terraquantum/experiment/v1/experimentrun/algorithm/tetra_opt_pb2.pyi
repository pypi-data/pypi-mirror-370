from buf.validate import validate_pb2 as _validate_pb2
from com.terraquantum.experiment.v1.experimentrun.algorithm import shared_pb2 as _shared_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TetraOptParametersProto(_message.Message):
    __slots__ = ("dimensionality", "maximal_rank", "iteration_number", "quantization", "points_number", "tolerance", "lower_limits", "upper_limits", "grid", "objective_function", "start_points", "precision", "point", "seed", "device", "local_optimizer", "polling", "objective_function_channel_id", "local_optimizer_channel_id", "functional_cache", "local_optimization_cache")
    DIMENSIONALITY_FIELD_NUMBER: _ClassVar[int]
    MAXIMAL_RANK_FIELD_NUMBER: _ClassVar[int]
    ITERATION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    QUANTIZATION_FIELD_NUMBER: _ClassVar[int]
    POINTS_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    LOWER_LIMITS_FIELD_NUMBER: _ClassVar[int]
    UPPER_LIMITS_FIELD_NUMBER: _ClassVar[int]
    GRID_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVE_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    START_POINTS_FIELD_NUMBER: _ClassVar[int]
    PRECISION_FIELD_NUMBER: _ClassVar[int]
    POINT_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    LOCAL_OPTIMIZER_FIELD_NUMBER: _ClassVar[int]
    POLLING_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVE_FUNCTION_CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    LOCAL_OPTIMIZER_CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    FUNCTIONAL_CACHE_FIELD_NUMBER: _ClassVar[int]
    LOCAL_OPTIMIZATION_CACHE_FIELD_NUMBER: _ClassVar[int]
    dimensionality: int
    maximal_rank: int
    iteration_number: int
    quantization: bool
    points_number: int
    tolerance: float
    lower_limits: _containers.RepeatedScalarFieldContainer[float]
    upper_limits: _containers.RepeatedScalarFieldContainer[float]
    grid: _containers.RepeatedScalarFieldContainer[int]
    objective_function: str
    start_points: _containers.RepeatedScalarFieldContainer[float]
    precision: str
    point: str
    seed: int
    device: str
    local_optimizer: str
    polling: _shared_pb2.PollingParametersProto
    objective_function_channel_id: str
    local_optimizer_channel_id: str
    functional_cache: bool
    local_optimization_cache: bool
    def __init__(self, dimensionality: _Optional[int] = ..., maximal_rank: _Optional[int] = ..., iteration_number: _Optional[int] = ..., quantization: bool = ..., points_number: _Optional[int] = ..., tolerance: _Optional[float] = ..., lower_limits: _Optional[_Iterable[float]] = ..., upper_limits: _Optional[_Iterable[float]] = ..., grid: _Optional[_Iterable[int]] = ..., objective_function: _Optional[str] = ..., start_points: _Optional[_Iterable[float]] = ..., precision: _Optional[str] = ..., point: _Optional[str] = ..., seed: _Optional[int] = ..., device: _Optional[str] = ..., local_optimizer: _Optional[str] = ..., polling: _Optional[_Union[_shared_pb2.PollingParametersProto, _Mapping]] = ..., objective_function_channel_id: _Optional[str] = ..., local_optimizer_channel_id: _Optional[str] = ..., functional_cache: bool = ..., local_optimization_cache: bool = ...) -> None: ...

class TetraOptInputsProto(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TetraOptMetadataProto(_message.Message):
    __slots__ = ("parameters", "inputs")
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    parameters: TetraOptParametersProto
    inputs: TetraOptInputsProto
    def __init__(self, parameters: _Optional[_Union[TetraOptParametersProto, _Mapping]] = ..., inputs: _Optional[_Union[TetraOptInputsProto, _Mapping]] = ...) -> None: ...

class TetraOptOutputsProto(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TetraOptOutcomeProto(_message.Message):
    __slots__ = ("result", "outputs")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    result: str
    outputs: TetraOptOutputsProto
    def __init__(self, result: _Optional[str] = ..., outputs: _Optional[_Union[TetraOptOutputsProto, _Mapping]] = ...) -> None: ...
